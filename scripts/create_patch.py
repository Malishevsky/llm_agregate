#!/usr/bin/env -S python3.11 -m poetry run -q python

#####################################################################################################

import argparse
import shutil
import site
import sys
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, distribution, packages_distributions
from logging import INFO, Logger, StreamHandler, getLogger
from pathlib import Path
from subprocess import CalledProcessError, run  # noqa: S404
from tempfile import TemporaryDirectory
from typing import Any, Final, Iterable, Optional

import tomli

#####################################################################################################

_LOGGER: Final = getLogger(__name__)

_STREAM_HANDLER: Final = StreamHandler()
_LOGGER.addHandler(_STREAM_HANDLER)
_LOGGER.setLevel(INFO)

#####################################################################################################

_PIPFILE: Final = 'Pipfile'
_PYPROJECT: Final = 'pyproject.toml'

#####################################################################################################

_SEPARATOR: Final = '@'

#####################################################################################################

def _get_project_root_folder_path(logger: Logger) -> Path:
    current_folder = Path(__file__)
    system_root_folder: Final = Path(current_folder.root)

    while current_folder != system_root_folder:
        project_desc_files = []
        for desc_file in (_PYPROJECT, _PIPFILE):
            project_desc_files.extend(current_folder.glob(desc_file))
        if project_desc_files:
            logger.info(f'{current_folder} is used as project root folder\n')
            return current_folder
        current_folder = current_folder.parent

    logger.error('Cannot find any project description files')
    sys.exit(1)

#####################################################################################################

def _get_project_description_file(root_folder_path: Path, logger: Logger) -> tuple[str, Path]:
    project_description_file = root_folder_path.joinpath(_PIPFILE)
    if project_description_file.exists():
        return (_PIPFILE, project_description_file)

    project_description_file = root_folder_path.joinpath(_PYPROJECT)
    if project_description_file.exists():
        return (_PYPROJECT, project_description_file)

    logger.error('Cannot find any project description files')
    sys.exit(1)

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _PyprojectParser:
    #####################################################################################################

    project_config: dict[str, Any]

    #####################################################################################################

    def get_index_url(self, package_name: str) -> str | None:
        tool_section: Final = self.project_config.get('tool', {})
        poetry_section: Final = tool_section.get('poetry', {})
        dependencies_section: Final = poetry_section.get('dependencies', {})
        package_info: Final = dependencies_section.get(package_name)

        if not isinstance(package_info, dict):
            return None

        package_source_name: Final = package_info.get('source')
        source_section: Final = poetry_section.get('source', [])
        package_source: Final = next((src for src in source_section if src['name'] == package_source_name), None)

        if package_source is None:
            return None

        return package_source.get('url')

    #####################################################################################################

    def get_git_url(self, package_name: str) -> str | None:
        tool_section: Final = self.project_config.get('tool', {})
        poetry_section: Final = tool_section.get('poetry', {})
        dependencies_section: Final = poetry_section.get('dependencies', {})
        package_info: Final = dependencies_section.get(package_name)

        if not isinstance(package_info, dict):
            return None

        git_url = package_info.get('git')
        branch = package_info.get('branch') or package_info.get('rev')

        if git_url is None or branch is None:
            return None

        return f'git+{git_url}{_SEPARATOR}{branch}'

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _PipenvParser:
    #####################################################################################################

    project_config: dict[str, Any]

    #####################################################################################################

    def get_index_url(self, package_name: str) -> str | None:
        packages_section: Final = self.project_config.get('packages', {})
        package_info: Final = packages_section.get(package_name)

        if not isinstance(package_info, dict):
            return None

        package_index: Final = package_info.get('index')
        source_section: Final = self.project_config.get('source', [])
        package_source: Final = next((src for src in source_section if src['name'] == package_index), None)

        if package_source is None:
            return None

        return package_source.get('url')

    #####################################################################################################

    def get_git_url(self, package_name: str) -> str | None:
        packages_section: Final = self.project_config.get('packages', {})
        package_info: Final = packages_section.get(package_name)

        if not isinstance(package_info, dict):
            return None

        git_url = package_info.get('git')
        branch = package_info.get('ref')

        if git_url is None or branch is None:
            return None

        return f'git+{git_url}{_SEPARATOR}{branch}'

#####################################################################################################

def _get_package_name(module_name: str, logger: Logger) -> str:
    package_distributions: Final = packages_distributions()
    package_names: Final = package_distributions.get(module_name)

    if package_names is None:
        logger.error(f'Cannot find package name for module "{module_name}"')
        sys.exit(1)
    elif len(package_names) > 1:
        logger.error(f'Cannot definitely determine package name for module "{module_name}". Got packages: {package_names}')
        sys.exit(1)

    return package_names[0]

#####################################################################################################

def _get_package_version(package_name: str, logger: Logger) -> str:
    try:
        dist = distribution(package_name)
    except PackageNotFoundError:
        logger.error(f'Cannot find package "{package_name}" to get package version')
        sys.exit(1)

    return dist.version

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _PackageInfo:
    package_name: str
    version: str
    location: Path
    module_name: str
    index_url: Optional[str]
    git_url: Optional[str]

#####################################################################################################

def _get_package_info(module_name: str, root_folder_path: Path, logger: Logger) -> _PackageInfo:
    description_filename, project_description_file = _get_project_description_file(root_folder_path, logger)

    with open(project_description_file, 'rb') as pyproject:
        project_config: Final = tomli.load(pyproject)

    if description_filename == _PYPROJECT:
        parser_cls = _PyprojectParser
    else:
        parser_cls = _PipenvParser

    parser: Final = parser_cls(project_config=project_config)

    package_name: Final = _get_package_name(module_name, logger)
    package_version: Final = _get_package_version(package_name, logger)
    package_index_url: Final = parser.get_index_url(package_name)
    package_git_url: Final = parser.get_git_url(package_name)
    module_location: Final = Path(site.getsitepackages()[0]).joinpath(module_name)

    return _PackageInfo(
        package_name=package_name,
        version=package_version,
        module_name=module_name,
        location=module_location,
        index_url=package_index_url,
        git_url=package_git_url,
    )

#####################################################################################################

def _get_frozen_requirements(logger: Logger) -> Iterable[str]:
    command: Final = [
        'python3',
        '-m',
        'pip',
        'freeze',
    ]
    try:
        raw_frozen_requirements = run(command, check=True, capture_output=True, text=True)  # noqa: S603
    except CalledProcessError as exc:
        logger.error(f'Cannot get frozen requirements. Got exception: {exc}')
        return []

    return raw_frozen_requirements.stdout.split('\n')

#####################################################################################################

def _get_package_commit_id(package_name: str, requirements: list[str], logger: Logger) -> str | None:
    pkg_freeze_info: Final = next((desc for desc in requirements if desc.startswith(f'{package_name} {_SEPARATOR}')), None)
    if pkg_freeze_info is None:
        logger.info(f'Cannot get info from "pip freeze" for package "{package_name}"')
        return None

    commit_id = pkg_freeze_info.split(_SEPARATOR)[-1]
    return commit_id.strip()

#####################################################################################################

def _create_install_package_command(package_info: _PackageInfo, destination_folder: Path) -> Iterable[str]:
    command: Final = [
        'python3',
        '-m',
        'pip',
        'install',
    ]

    if package_info.git_url is not None:
        command.extend([package_info.git_url])
    else:
        command.extend([f'{package_info.package_name}=={package_info.version}'])

        if package_info.index_url is not None:
            command.extend(['--index-url', package_info.index_url])

    command.extend(['--no-deps', '--target', str(destination_folder)])
    return command

#####################################################################################################

def _install_package(package_info: _PackageInfo, destination_folder: Path, logger: Logger) -> None:
    install_package_command: Final = _create_install_package_command(package_info, destination_folder)

    try:
        run(install_package_command, check=True)  # noqa: S603, S606, DUO116
    except CalledProcessError as exc:
        logger.error(exc.stderr, exc_info=exc)
        sys.exit(1)

#####################################################################################################

def _create_patch(original: Path, patched: Path, patch: Path, workdir: Path) -> None:
    original_relative: Final = str(original.relative_to(workdir))
    patched_relative: Final = str(patched.relative_to(workdir))

    command: Final = ('diff', '-ruN', original_relative, patched_relative)
    try:
        output = run(command, check=True, capture_output=True, cwd=workdir).stdout  # noqa: S602, S603, S606, DUO116
    except CalledProcessError as exc:
        output = exc.stdout

    with open(patch, 'wb') as patch_file:
        patch_file.write(output)

#####################################################################################################

def _clean_folder(folder: Path) -> None:
    for file_path in folder.rglob('*.pyc'):
        file_path.unlink()

#####################################################################################################

def _mark_patched(folder: Path) -> None:
    filename: Final = folder.joinpath('___PATCHED___.txt')
    if filename.exists():
        return

    with open(filename, 'wb') as patched:
        patched.write(b'patched\n')

#####################################################################################################

def _patch(module_name: str, logger: Logger) -> None:
    root_folder_path: Final = _get_project_root_folder_path(logger)
    patches_folder_path: Final = root_folder_path.joinpath('patches')
    patches_folder_path.mkdir(exist_ok=True)

    base_commands = []
    if root_folder_path.joinpath(_PIPFILE).exists():
        base_commands.append('pipenv')
    elif root_folder_path.joinpath(_PYPROJECT).exists():
        base_commands.append('poetry')
    else:
        logger.error('Cannot find any project description files')
        sys.exit(1)

    package_info: Final = _get_package_info(module_name, root_folder_path, logger)
    frozen_requirements: Final = _get_frozen_requirements(logger)

    with TemporaryDirectory() as tmpdir:
        tmpdir_path: Final = Path(tmpdir)
        _install_package(package_info, destination_folder=tmpdir_path, logger=logger)

        module_path: Final = tmpdir_path.joinpath(module_name)
        original_module_path: Final = tmpdir_path.joinpath(f'{module_name}_orig')

        shutil.move(module_path, original_module_path)
        shutil.copytree(package_info.location, module_path)

        _clean_folder(module_path)
        _clean_folder(original_module_path)

        _mark_patched(module_path)

        package_commit_id: Final = _get_package_commit_id(package_info.package_name, frozen_requirements, logger)

        package_patch_meta_info = package_info.version
        if package_commit_id is not None:
            package_patch_meta_info = f'{package_patch_meta_info}{_SEPARATOR}{package_commit_id}'

        patch_file_path: Final = patches_folder_path.joinpath(f'{module_name}{_SEPARATOR}{package_patch_meta_info}.patch')
        _create_patch(
            original=original_module_path,
            patched=module_path,
            patch=patch_file_path,
            workdir=tmpdir_path,
        )

#####################################################################################################

def _main(logger: Logger):
    logger.info('Creating patch...')

    parser: Final = argparse.ArgumentParser()
    parser.add_argument('module_name')
    args: Final = parser.parse_args()

    module_name: Final = args.module_name

    try:
        _patch(module_name, logger)
    except BaseException as exc:  # noqa: PIE786, WPS424  # pylint: disable=broad-exception-caught
        logger.error(exc, exc_info=exc)
    else:
        logger.info('Patch was created')

#####################################################################################################

if __name__ == '__main__':
    _main(_LOGGER)

#####################################################################################################
