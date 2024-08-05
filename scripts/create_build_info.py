#!/usr/bin/env -S poetry run python

#####################################################################################################

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from logging import INFO, Logger, StreamHandler, getLogger
from pathlib import Path
from string import Template
from subprocess import run  # noqa: S404
from typing import Final

import tomli

#####################################################################################################

_LOGGER: Final = getLogger(__name__)

_STREAM_HANDLER: Final = StreamHandler()
_LOGGER.addHandler(_STREAM_HANDLER)
_LOGGER.setLevel(INFO)

#####################################################################################################

_AVAILABLE_PROJECT_DESCRIPTION_FILES: Final = ('pyproject.toml', 'Pipfile')

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _AppBuildInfo:
    app_name: str
    app_version: str
    app_branch: str
    app_commit_hash: str

#####################################################################################################

_BUILD_INFO_TEMPLATE_STR: Final = """
#####################################################################################################

from typing import Final

#####################################################################################################

APP_NAME: Final = '$app_name'
APP_VERSION: Final = '$app_version'
APP_BRANCH: Final = '$app_branch'
APP_COMMIT_HASH: Final = '$app_commit_hash'
APP_BUILD_TIMESTAMP: Final = '$app_build_timestamp'

#####################################################################################################
"""

_BUILD_INFO_TEMPLATE: Final = Template(_BUILD_INFO_TEMPLATE_STR)

#####################################################################################################

def _get_project_root_folder_path(logger: Logger) -> Path:
    current_folder = Path(__file__)
    system_root_folder: Final = Path(current_folder.root)

    while current_folder != system_root_folder:
        project_desc_files = []
        for desc_file in _AVAILABLE_PROJECT_DESCRIPTION_FILES:
            project_desc_files.extend(current_folder.glob(desc_file))
        if project_desc_files:
            logger.info(f'{current_folder} is used as project root folder\n')
            return current_folder
        current_folder = current_folder.parent

    logger.error('Cannot find any project description files')
    sys.exit(1)

#####################################################################################################

_ROOT_FOLDER_PATH: Final = _get_project_root_folder_path(_LOGGER)
_PROJECT_DESCRIPTION_FILE: Final = _ROOT_FOLDER_PATH.joinpath('pyproject.toml')

#####################################################################################################

def _get_app_branch() -> str:
    app_branch_output: Final = run(  # noqa: S603, S607
        ['git', 'log', '-n', '1', '--pretty=%d', 'HEAD'],  # noqa: WPS323
        capture_output=True,
        text=True,
        check=True,
    )
    return app_branch_output.stdout.strip()

#####################################################################################################

def _get_app_commit_hash() -> str:
    app_commit_hash_output: Final = run(  # noqa: S603, S607
        ['git', 'log', '-n', '1', '--pretty=%H', 'HEAD'],  # noqa: WPS323
        capture_output=True,
        text=True,
        check=True,
    )
    return app_commit_hash_output.stdout.strip()

#####################################################################################################

def _get_app_info(logger: Logger) -> _AppBuildInfo:
    app_branch: Final = _get_app_branch()
    app_commit_hash: Final = _get_app_commit_hash()

    with open(_PROJECT_DESCRIPTION_FILE, 'rb') as pyproject:
        project_config: Final = tomli.load(pyproject)

    project_config_tool_part: Final = project_config.get('tool', {})
    project_config_poetry_part: Final = project_config_tool_part.get('poetry', {})

    app_name: Final = project_config_poetry_part.get('name', '')
    if not app_name:
        logger.error('Cannot get app name from pyproject.toml')
        sys.exit(1)

    app_version: Final = project_config_poetry_part.get('version', '')
    if not app_version:
        logger.error('Cannot get app version from pyproject.toml')
        sys.exit(1)

    return _AppBuildInfo(app_name=app_name, app_version=app_version, app_branch=app_branch, app_commit_hash=app_commit_hash)

#####################################################################################################

def _main(logger: Logger) -> None:
    app_info: Final = _get_app_info(logger)
    current_datetime_utc: Final = datetime.now(timezone.utc)
    build_info = _BUILD_INFO_TEMPLATE.substitute({
        'app_name': app_info.app_name,
        'app_version': app_info.app_version,
        'app_branch': app_info.app_branch,
        'app_commit_hash': app_info.app_commit_hash,
        'app_build_timestamp': current_datetime_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
    })
    sys.stdout.write(build_info)

#####################################################################################################

if __name__ == '__main__':
    _main(_LOGGER)

#####################################################################################################
