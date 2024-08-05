#!/usr/bin/env -S poetry run python

#####################################################################################################

# pylint: disable=wrong-import-position, wrong-import-order
from collections.abc import Sequence
from sys import argv
from typing import Any, Final

from l7x.logger import setup_logging

# pylint: enable=wrong-import-position

_LOGGER: Final = setup_logging(default_path='logging_debug.json')

#####################################################################################################

from dataclasses import dataclass  # noqa: E402
from logging import Logger  # noqa: E402
from multiprocessing.context import _default_context as _multiprocess_default_context  # noqa: E402
from os import environ, getenv  # noqa: E402
from os.path import dirname, isfile as _path_isfile, join as _path_join, realpath  # noqa: E402
from signal import SIGINT, SIGTERM, signal  # noqa: E402
from subprocess import Popen  # noqa: E402, S404
from sys import stdout  # noqa: E402
from urllib.parse import urlparse  # noqa: E402

from _environment import is_all_containers_running, up_environment  # noqa: E402, WPS436
from _translation_server import run_mock_translation_server  # noqa: E402, WPS436
from l7x.configs.constants import DEFAULT_TRANSLATION_SERVER_PORT  # noqa: E402
from l7x.configs.settings import create_app_settings  # noqa: E402
from l7x.main import run  # noqa: E402
from l7x.utils.config_utils import convert_str_to_bool  # noqa: E402

#####################################################################################################

def _run_lt(logger: Logger) -> Popen:  # type: ignore
    dir_path: Final = dirname(realpath(__file__))
    lt_path = _path_join(dir_path, '..', 'node_modules', '.bin', 'lt')
    lt_path = realpath(lt_path)
    if _path_isfile(lt_path):
        logger.info('localtunnel is already installed.')
    else:
        with Popen(  # noqa: S603, S607
            [
                'yarn',
                'install',
                '--frozen-lockfile',
                '--check-files',
                '--non-interactive',
                '--ignore-scripts',
                '--ignore-optional',
                '--prefer-offline',
            ],
            stdout=stdout.buffer,
            stderr=stdout.buffer,
        ) as proc:
            proc.wait()

    app_settings: Final = create_app_settings()
    port: Final = app_settings.port

    server_url = urlparse(app_settings.server_url)
    subdomain = server_url.netloc.split('.')[0]
    subdomain = subdomain.split('@')[-1]

    server_url = server_url._replace(  # noqa: WPS437
        netloc=server_url.netloc.replace(f'{subdomain}.', ''),
        path='',
        params='',
        query='',
        fragment='',
    )
    localtunnel_user: Final = app_settings.localtunnel_user
    localtunnel_pass: Final = app_settings.localtunnel_pass
    if localtunnel_user and localtunnel_pass:
        localthunnel_host = f'{server_url.scheme}://{localtunnel_user}:{localtunnel_pass}@{server_url.netloc}'
    else:
        localthunnel_host = server_url.geturl()

    return Popen(  # noqa: S603, S607
        ['yarn', 'lt', '-h', localthunnel_host, '--port', str(port), '--subdomain', subdomain],
        stdout=stdout.buffer,
        stderr=stdout.buffer,
    )

#####################################################################################################

@dataclass
class _ProcInfo:
    proc: Popen | None = None  # type: ignore

_PROC_INFO: Final = _ProcInfo()

#####################################################################################################

def _after_all_started(logger: Logger) -> None:
    proc: Final = _PROC_INFO.proc
    if proc is not None:
        proc.terminate()
        proc.wait()
    _PROC_INFO.proc = _run_lt(logger)

#####################################################################################################

def _run_translation_server(port: int, logger: Logger | None = None) -> None:
    ctx: Final = _multiprocess_default_context.get_context('spawn')

    environ['L7X_TRANSLATE_API_URL'] = f'http://0.0.0.0:{port}/'

    process = ctx.Process(target=run_mock_translation_server, args=(port, logger))
    process.start()

    def shutdown(*_args: Any) -> None:
        nonlocal process  # noqa: WPS420
        process.join()
        process.close()

    signal(SIGINT, shutdown)
    signal(SIGTERM, shutdown)

#####################################################################################################

def _main(argv_list: Sequence[str]) -> None:
    if convert_str_to_bool(getenv('L7X_RUN_TRANSLATION_SERVER', 'false')):
        _run_translation_server(DEFAULT_TRANSLATION_SERVER_PORT, _LOGGER)

    if not is_all_containers_running():
        up_environment(_LOGGER, detached=True)

    run(_LOGGER, argv_list, _after_all_started)

    proc: Final = _PROC_INFO.proc
    if proc is not None:
        proc.terminate()
        proc.wait()
        _PROC_INFO.proc = None

#####################################################################################################

_MAIN: Final = '__main__'

if __name__ == _MAIN:

    # For support profiling
    from cProfile import __file__ as _cprofile_file  # noqa: WPS433
    from sys import modules  # noqa: WPS433
    _MAIN_MODULE: Final = modules.get(_MAIN)
    if _MAIN_MODULE is not None and _MAIN_MODULE.__file__ == _cprofile_file:
        from src import _debug_run  # noqa: WPS433 # Imports you again (does *not* use cache or execute as __main__)
        globals().update(vars(_debug_run))  # Replaces current contents with newly imported stuff
        modules[_MAIN] = _debug_run  # Ensures pickle lookups on __main__ find matching version

    _main(tuple(argv[1:]))

#####################################################################################################
