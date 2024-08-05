#####################################################################################################

from asyncio import AbstractEventLoop, all_tasks, gather, get_running_loop, new_event_loop, set_event_loop
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from logging import Logger, getLogger
from multiprocessing.managers import SyncManager
from typing import Final, Generic, TypeVar

from elasticapm import Client as _ApmClient
from uvloop import install as _uvloop_install

from l7x.configs.settings import AppSettings
from l7x.logger import DEFAULT_LOGGER_NAME
from l7x.types.errors import AppException, ShutdownException
from l7x.types.shutdown_event import ShutdownEvent
from l7x.utils.apm_utils import init_apm_client, init_elastic_log

#####################################################################################################

LoopFuncAdditionalParams = TypeVar('LoopFuncAdditionalParams')

LoopFuncContext = TypeVar('LoopFuncContext')

#####################################################################################################

AfterAllStartedFunc = Callable[[Logger], None]

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class LoopFuncParams(Generic[LoopFuncAdditionalParams]):
    app_settings: AppSettings
    logger: Logger
    ext: LoopFuncAdditionalParams
    shutdown_event: ShutdownEvent
    cmd_manager: SyncManager | None = None
    apm_client: _ApmClient | None = None
    func_after_all_started: AfterAllStartedFunc | None = None

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class EventLoopFuncParams(LoopFuncParams[LoopFuncAdditionalParams]):
    loop: AbstractEventLoop

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class CreateLoopBaseParams(Generic[LoopFuncAdditionalParams]):
    app_settings: AppSettings
    ext: LoopFuncAdditionalParams
    shutdown_event: ShutdownEvent
    loop_name: str = ''
    cmd_manager: SyncManager | None = None
    func_after_all_started: AfterAllStartedFunc | None = None

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class LoopContext:
    wait_set_shutdown_event = False

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class CreateLoopParams(CreateLoopBaseParams[LoopFuncAdditionalParams]):
    func: Callable[[LoopFuncParams[LoopFuncAdditionalParams]], LoopContext | None]
    func_before_exit: Callable[[LoopContext | None], None] | None = None

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class EventLoopContext(LoopContext):
    """EMPTY BASE CLASS."""

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class CreateEventLoopParams(CreateLoopBaseParams[LoopFuncAdditionalParams]):
    func: Callable[[EventLoopFuncParams[LoopFuncAdditionalParams]], Awaitable[EventLoopContext | None]]
    func_before_exit: Callable[[EventLoopContext | None], Awaitable[None]] | None = None

#####################################################################################################

def _create_event_loop(is_dev_mode: bool = False) -> AbstractEventLoop:
    _uvloop_install()
    loop = None

    is_loop_already_run = True
    try:
        loop = get_running_loop()
    except BaseException:  # noqa: PIE786, WPS424 # pylint: disable=broad-except
        is_loop_already_run = False

    if is_loop_already_run or loop is not None:
        raise AppException(f'Event loop already exist: {loop}')

    loop = new_event_loop()
    loop.set_debug(is_dev_mode)
    set_event_loop(loop)

    return loop

#####################################################################################################

def _cancel_all_tasks(loop: AbstractEventLoop) -> None:
    tasks: Final = tuple(task for task in all_tasks(loop) if not task.done())
    if not tasks:
        return

    for task_for_cancel in tasks:
        task_for_cancel.cancel()

    loop.run_until_complete(gather(*tasks, return_exceptions=True))

    for task in tasks:
        if not task.cancelled() and task.exception() is not None:
            loop.call_exception_handler({
                'message': 'unhandled exception during shutdown',
                'exception': task.exception(),
                'task': task,
            })

#####################################################################################################

def _finalize_event_loop(loop: AbstractEventLoop, logger: Logger, apm_client: _ApmClient | None, /) -> None:
    try:
        _cancel_all_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())
    except BaseException as err:  # noqa: PIE786, WPS424 # pylint: disable=broad-except
        logger.error(f'Finalize loop error: {err}', exc_info=err)
    finally:
        set_event_loop(None)
        logger.info('Closing loop')
        if not loop.is_closed():
            loop.close()
        logger.info('Closed loop')

        if apm_client is not None:
            logger.info('Closing amp')
            apm_client.close()
            logger.info('Closed amp')

#####################################################################################################

def _call_event_loop_func_before_exit(
    func_before_exit: Callable[[EventLoopContext | None], Awaitable[None]] | None,
    context: EventLoopContext | None,
    loop: AbstractEventLoop,
    logger: Logger,
    /,
) -> None:
    if func_before_exit is None:
        return
    try:
        loop.run_until_complete(func_before_exit(context))
    except BaseException as err:  # noqa: PIE786, WPS424 # pylint: disable=broad-exception-caught
        logger.error(f'Finalize loop error: {err}', exc_info=err)

#####################################################################################################

def create_event_loop(cel_params: CreateEventLoopParams[LoopFuncAdditionalParams], /) -> None:
    app_settings: Final = cel_params.app_settings
    shutdown_event: Final = cel_params.shutdown_event
    init_elastic_log(app_settings)
    logger: Final = getLogger(DEFAULT_LOGGER_NAME if cel_params.loop_name == '' else cel_params.loop_name)
    apm_client: Final = init_apm_client(logger, app_settings)
    cmd_manager: Final = cel_params.cmd_manager

    loop: Final = _create_event_loop(app_settings.is_dev_mode)

    context: EventLoopContext | None = None
    try:
        context = loop.run_until_complete(cel_params.func(EventLoopFuncParams(
            loop=loop,
            app_settings=app_settings,
            logger=logger,
            ext=cel_params.ext,
            apm_client=apm_client,
            shutdown_event=shutdown_event,
            func_after_all_started=cel_params.func_after_all_started,
            cmd_manager=cmd_manager,
        )))

        if context is not None:
            if not isinstance(context, EventLoopContext):
                raise AppException('Loop context unknown class')

            if context.wait_set_shutdown_event and not shutdown_event.is_set():
                shutdown_event_wait_obj = loop.run_in_executor(None, shutdown_event.wait)
                loop.run_until_complete(shutdown_event_wait_obj)

    except (KeyboardInterrupt, ShutdownException) as err:
        logger.info('Shutdown...')
        shutdown_event.set()
        if isinstance(err, ShutdownException):
            raise err
        raise ShutdownException() from err

    except BaseException as err:  # noqa: WPS424 # pylint: disable=broad-except
        if apm_client is not None:
            apm_client.capture_exception()  # type: ignore[no-untyped-call]
        logger.error(f'Create loop error: {err}', exc_info=err)
        raise err
    finally:
        _call_event_loop_func_before_exit(cel_params.func_before_exit, context, loop, logger)
        _finalize_event_loop(loop, logger, apm_client)

#####################################################################################################

def _call_loop_func_before_exit(
    func_before_exit: Callable[[LoopContext | None], None] | None,
    context: LoopContext | None,
    logger: Logger,
    /,
) -> None:
    if func_before_exit is None:
        return
    try:
        func_before_exit(context)
    except BaseException as err:  # noqa: PIE786, WPS424 # pylint: disable=broad-exception-caught
        logger.error(f'Finalize loop error: {err}', exc_info=err)

#####################################################################################################

def create_loop(cl_params: CreateLoopParams[LoopFuncAdditionalParams], /) -> None:
    app_settings: Final = cl_params.app_settings
    shutdown_event: Final = cl_params.shutdown_event
    init_elastic_log(app_settings)
    logger: Final = getLogger(DEFAULT_LOGGER_NAME if cl_params.loop_name == '' else cl_params.loop_name)
    apm_client: Final = init_apm_client(logger, app_settings)

    context: LoopContext | None = None
    try:

        context = cl_params.func(LoopFuncParams(
            app_settings=app_settings,
            logger=logger,
            ext=cl_params.ext,
            shutdown_event=shutdown_event,
            apm_client=apm_client,
            func_after_all_started=cl_params.func_after_all_started,
        ))

        if context is not None:
            if not isinstance(context, LoopContext):
                raise AppException('Loop context unknown class')

            if context.wait_set_shutdown_event and not shutdown_event.is_set():
                shutdown_event.wait()

    except (KeyboardInterrupt, ShutdownException) as err:
        logger.info('Shutdown...')
        shutdown_event.set()
        if isinstance(err, ShutdownException):
            raise err
        raise ShutdownException() from err

    except BaseException as err:  # noqa: WPS424 # pylint: disable=broad-except
        if apm_client is not None:
            apm_client.capture_exception()  # type: ignore[no-untyped-call]
        logger.error(f'Create loop error: {err}', exc_info=err)
        raise err
    finally:
        _call_loop_func_before_exit(cl_params.func_before_exit, context, logger)
        if apm_client is not None:
            apm_client.close()

#####################################################################################################
