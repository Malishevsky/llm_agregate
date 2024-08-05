#####################################################################################################

from dataclasses import dataclass
from typing import Final

from l7x.utils.datetime_utils import now_utc
from l7x.utils.mapping_utils import find_value_by_keys_sequence

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class AppBuildInfo:
    app_name: str
    app_version: str
    app_branch: str
    app_commit_hash: str
    app_build_timestamp: str

#####################################################################################################

def get_app_build_info() -> AppBuildInfo:
    try:
        from l7x.build_info import (  # type: ignore[import-not-found, unused-ignore] # noqa: E501, WPS433 # pylint: disable=import-outside-toplevel
            APP_BRANCH,
            APP_BUILD_TIMESTAMP,
            APP_COMMIT_HASH,
            APP_NAME,
            APP_VERSION,
        )
        return AppBuildInfo(
            app_name=APP_NAME,
            app_version=APP_VERSION,
            app_branch=APP_BRANCH,
            app_commit_hash=APP_COMMIT_HASH,
            app_build_timestamp=APP_BUILD_TIMESTAMP,
        )
    except ModuleNotFoundError:

        # то что ниже используется только в режиме разработки и в проде вызываться не должно

        from os import getenv  # noqa: WPS433 # pylint: disable=import-outside-toplevel
        from pathlib import Path  # noqa: WPS433 # pylint: disable=import-outside-toplevel
        from subprocess import run  # noqa: S404, WPS433 # pylint: disable=import-outside-toplevel

        from tomli import load as _tomli_load  # noqa: WPS433 # pylint: disable=import-outside-toplevel

        root_folder: Final = getenv('PWD', '').strip()

        app_branch: Final = run(  # noqa: S603, S607
            ['git', 'log', '-n', '1', '--pretty=%d', 'HEAD'],  # noqa: WPS323
            capture_output=True,
            text=True,
            check=True,
            cwd=root_folder,
        ).stdout.strip()

        app_commit_hash: Final = run(  # noqa: S603, S607
            ['git', 'log', '-n', '1', '--pretty=%H', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            cwd=root_folder,
        ).stdout.strip()

        project_description_file: Final = Path(root_folder).joinpath('pyproject.toml')
        with open(project_description_file, 'rb') as pyproject:
            project_config: Final = _tomli_load(pyproject)

        app_name: Final = find_value_by_keys_sequence(project_config, 'tool', 'poetry', 'name', default='')
        app_version: Final = find_value_by_keys_sequence(project_config, 'tool', 'poetry', 'version', default='')
        current_datetime_utc = now_utc()
        app_build_timestamp: Final = current_datetime_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

        return AppBuildInfo(
            app_name=app_name,
            app_version=app_version,
            app_branch=app_branch,
            app_commit_hash=app_commit_hash,
            app_build_timestamp=app_build_timestamp,
        )

#####################################################################################################

def convert_str_to_bool(text: str) -> bool:
    text = text.lower()
    if text in {'y', 'yes', 't', 'true', 'on', '1'}:
        return True
    if text in {'n', 'no', 'f', 'false', 'off', '0'}:
        return False
    raise ValueError(f'Invalid truth value {text}')

#####################################################################################################
