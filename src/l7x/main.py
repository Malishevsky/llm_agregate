#####################################################################################################

from collections.abc import Sequence
from contextlib import ExitStack, closing as _contextlib_closing, suppress
from gc import DEBUG_UNCOLLECTABLE, collect as _gc_collect, garbage as _gc_garbage, set_debug as _gc_set_debug
from logging import Logger
from multiprocessing import freeze_support, get_context as _multiprocessing_get_context
from multiprocessing.managers import SyncManager
from os.path import exists, realpath
from pathlib import Path
from signal import SIG_IGN, SIGINT, SIGTERM, signal
from ssl import OPENSSL_VERSION
from sys import exit as _sys_exit, modules
from time import sleep
from typing import Any, Final

from cpuinfo import get_cpu_info
from hypercorn.config import Config as _HypercornConfig, Sockets
from setproctitle import setproctitle, setthreadtitle

from l7x.commands.base_context_creator import (
    BaseCmdGlobalContext,
    BaseCmdLocalContext,
    creator_base_global_cmd_context,
    creator_local_tokens_cmd_context,
)
from l7x.configs.settings import AppSettings, create_app_settings
from l7x.types.errors import ShutdownException
from l7x.utils.cmd_manager_utils import CmdManagerImpl
from l7x.utils.loop_utils import (
    AbstractEventLoop,
    AfterAllStartedFunc,
    CreateEventLoopParams,
    EventLoopFuncParams,
    ShutdownEvent,
    create_event_loop,
)
from l7x.utils.worker_utils import WorkerDescription, WorkerType, run_workers
from l7x.web_worker import WebWorkerParams, WorkerParams, run_web_worker

#####################################################################################################

async def _run_worker_processes(
    app_settings: AppSettings,
    logger: Logger,
    loop: AbstractEventLoop,
    shutdown_event: ShutdownEvent,
    func_after_all_started: AfterAllStartedFunc | None,
    manager: SyncManager,
    /,
) -> None:
    sockets_need_close: list[Sockets] = []
    certificate_path: Final = app_settings.certificate_path
    private_key_path: Final = app_settings.private_key_path
    hypercorn_config: Final = _HypercornConfig()
    # TODO: hypercorn_config.quic_bind = [f'0.0.0.0:{app_settings.port}']
    hypercorn_config.bind = [f'0.0.0.0:{app_settings.port}']
    hypercorn_config.alpn_protocols = ['http/1.1']

    if certificate_path is not None or private_key_path is not None:
        if certificate_path is not None:
            if not certificate_path.is_file():
                raise FileNotFoundError(f'SSL Certificate file not found or path is invalid: {str(certificate_path)}')
        else:
            raise ValueError('Certificate file path is not specified.')
        if private_key_path is not None:
            if not private_key_path.is_file():
                raise FileNotFoundError(f'SSL Private Key file not found or path is invalid: {str(private_key_path)}')
        else:
            raise ValueError('Private Key file path is not specified')
        hypercorn_config.certfile = certificate_path
        hypercorn_config.keyfile = private_key_path
        logger.info('HTTPS secure connection will be used.')
    else:
        logger.warning('HTTP not secure connection will be used.')

    if app_settings.is_dev_mode:
        hypercorn_config.debug = True
        hypercorn_config.use_reloader = True
        hypercorn_config.loglevel = 'DEBUG'

    web_sockets: Final = hypercorn_config.create_sockets()
    sockets_need_close.append(web_sockets)

    descriptions: Final[list[WorkerDescription[WorkerParams]]] = []

    metrics_cmd_manager: Final = CmdManagerImpl[BaseCmdGlobalContext, None, BaseCmdLocalContext](
        name_prefix='metrics_cmd_processor_',
        global_context_creator=creator_base_global_cmd_context,
        global_context_creator_additional_params=None,
        local_context_creator=creator_local_tokens_cmd_context,
        worker_count=1,
        manager=manager,
        logger=logger,
        app_settings=app_settings,
    )
    descriptions.extend(metrics_cmd_manager.worker_descriptions)

    for worker_index in range(app_settings.worker_count):
        web_work_desc = WorkerDescription(
            func=run_web_worker,
            name=f'main_worker_{worker_index}',
            func_params=WebWorkerParams(
                app_settings=app_settings,
                sockets=web_sockets,
                hypercorn_config=hypercorn_config,
                cmd_manager=metrics_cmd_manager,
            ),
            worker_type=WorkerType.PROCESS,
        )
        descriptions.append(web_work_desc)

    def _func_after_all_started(local_logger: Logger) -> None:
        if func_after_all_started is not None:
            func_after_all_started(local_logger)

    with ExitStack() as exit_stack:
        for sockets in sockets_need_close:
            for secure_socket in sockets.secure_sockets:
                exit_stack.enter_context(_contextlib_closing(secure_socket))
            for insecure_socket in sockets.insecure_sockets:
                exit_stack.enter_context(_contextlib_closing(insecure_socket))

        await run_workers(tuple(descriptions), logger, loop, shutdown_event, func_after_all_started)

#####################################################################################################

async def _main_loop(mel_params: EventLoopFuncParams[None], /) -> None:
    logger: Final = mel_params.logger
    logger.info('Main process starting...')
    app_settings: Final = mel_params.app_settings
    logger.info(f'App settings: {app_settings}')

    with _multiprocessing_get_context('spawn').Manager() as manager:
        await _run_worker_processes(
            app_settings,
            logger,
            mel_params.loop,
            mel_params.shutdown_event,
            mel_params.func_after_all_started,
            manager,
        )

#####################################################################################################

def _wait_for_source_files_content_changes(shutdown_event: ShutdownEvent, /) -> bool:
    last_updates: dict[Path, float] = {}
    for module in list(modules.values()):
        filename = getattr(module, '__file__', None)
        if filename is None:
            continue
        file_path = Path(filename)
        with suppress(FileNotFoundError, NotADirectoryError):
            last_updates[file_path] = file_path.stat().st_mtime

    env_file: Final = realpath('./.env')
    if exists(env_file):
        file_path = Path(env_file)
        with suppress(FileNotFoundError, NotADirectoryError):
            last_updates[file_path] = file_path.stat().st_mtime

    while not shutdown_event.is_set():
        for index, (file_path_for_check, last_mtime) in enumerate(last_updates.items()):
            if index % 10 == 0:
                # Yield to the event loop
                sleep(0)

            try:
                mtime = file_path_for_check.stat().st_mtime
            except FileNotFoundError:
                return True

            if mtime > last_mtime:
                return True

            last_updates[file_path_for_check] = mtime

        sleep(2)

    return False

######################################################################################

def _handle_options(logger: Logger, app_settings: AppSettings, argv_list: Sequence[str], /) -> int:
    option = argv_list[0].strip()
    error_msg = 'Invalid params, support "--version" or empty params'
    if not argv_list:
        return -1

    if len(argv_list) != 1:
        logger.info(f'{error_msg}. Cur params: {argv_list}')
        return 1

    match option:
        case '--version':
            app_version = app_settings.service_version
            app_name = app_settings.service_name
            logger.info(f'{app_name} (version {app_version})')
            return 0
        case _:
            # TODO: fix work in docker after build with nuitka: "/usr/src/app/run.bin"
            # logger.info(f'{error_msg}. Cur option: {option}')
            # return 1
            return -1

#####################################################################################################

def _run_server_main_process(
    logger: Logger,
    app_settings: AppSettings,
    _argv_list: Sequence[str],
    shutdown_event: ShutdownEvent,
    func_after_all_started: AfterAllStartedFunc | None = None,
    /,
) -> None:
    signal(SIGINT, SIG_IGN)

    setproctitle('main')
    setthreadtitle('m_main')

    logger.info('Starting...')
    logger.info(f'OPENSSL_VERSION: {OPENSSL_VERSION}')

    if app_settings.is_dev_mode:
        logger.warning('Application run in DEVELOPMENT mode.')

    #if not app_settings.db_secret:
    #    logger.warning(
    #        'Password store in db without encryption. To improve security, we recommend generating and set L7X_DB_SECRET.',
    #    )

    def after_all_started(logger_local: Logger) -> None:
        sleep(0)  # Для корректного вывода в консоль логов.
        logger_local.info('Main process started (CTRL + C to quit)')
        if func_after_all_started is not None:
            func_after_all_started(logger_local)

    with suppress(ShutdownException):
        create_event_loop(CreateEventLoopParams(
            func=_main_loop,
            app_settings=app_settings,
            func_after_all_started=after_all_started,
            shutdown_event=shutdown_event,
            ext=None,
        ))

#####################################################################################################

def run(
    logger: Logger,
    argv_list: Sequence[str],
    func_after_all_started: AfterAllStartedFunc | None = None,
    /,
) -> None:
    logger.info('Running...')
    setproctitle('demo_page_server')
    setthreadtitle('m_demo_page_server')
    freeze_support()
    ctx: Final = _multiprocessing_get_context('spawn')
    with ctx.Manager() as manager:
        shutdown_event: ShutdownEvent = manager.Event()

        need_restart = False
        while need_restart or not shutdown_event.is_set():
            app_settings = create_app_settings(include_db_admin_credentials=True)
            cpu_info: dict[str, Any] = get_cpu_info()
            if not app_settings.is_dev_mode:
                cpu_info.pop('python_version', None)
            logger.info(f'CPU info: {cpu_info}')

            _gc_set_debug(DEBUG_UNCOLLECTABLE if app_settings.is_dev_mode else 0)

            _gc_collect()
            if app_settings.is_dev_mode:
                for garbage_obj in _gc_garbage:
                    logger.warning(f'garbage: {garbage_obj}')

            if argv_list:
                ret_code = _handle_options(logger, app_settings, argv_list)
                if ret_code >= 0:
                    _sys_exit(ret_code)

            shutdown_event.clear()

            def shutdown(*_args: Any) -> None:
                logger.info(f'Receive signal: {_args[0]}')
                shutdown_event.set()

            signal(SIGINT, shutdown)
            signal(SIGTERM, shutdown)

            process = ctx.Process(
                target=_run_server_main_process,
                args=(logger, app_settings, argv_list, shutdown_event, func_after_all_started,),
            )
            process.start()

            if app_settings.is_dev_mode:
                need_restart = _wait_for_source_files_content_changes(shutdown_event)
                shutdown_event.set()
            else:
                while not shutdown_event.is_set():
                    sleep(1)

            process.join()
            process.close()

    logger.info('Ended')

######################################################################################
