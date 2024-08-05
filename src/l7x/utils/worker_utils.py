#####################################################################################################

from asyncio import FIRST_COMPLETED, AbstractEventLoop, Future, sleep as _async_sleep, wait
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from logging import Logger
from multiprocessing import get_context as _multiprocessing_get_context
from multiprocessing.connection import Connection
from multiprocessing.context import SpawnContext as _MultiprocessContext
from multiprocessing.process import BaseProcess, current_process
from multiprocessing.synchronize import Event as _MultiprocessEvent
from signal import SIG_IGN, SIGINT, signal
from threading import Thread, get_ident
from time import sleep as _sync_sleep
from typing import Final, Generic, TypeVar

from setproctitle import setproctitle, setthreadtitle

from l7x.types.errors import AppException, ShutdownException
from l7x.types.shutdown_event import ShutdownEvent
from l7x.utils.contextmanager_utils import with_cleanup
from l7x.utils.loop_utils import AfterAllStartedFunc

#####################################################################################################

class WorkerType(Enum):
    PROCESS = 0
    THREAD = 1

#####################################################################################################

class RestartType(Enum):
    INFINITY = 0
    ONLY_IF_ERR = 1
    NONE = 3

#####################################################################################################

class DaemonType(Enum):
    DAEMON = 0
    NOT_DAEMON = 1

#####################################################################################################

StartedEvent = _MultiprocessEvent

#####################################################################################################

_WorkerRunFunctionParams_co = TypeVar('_WorkerRunFunctionParams_co', covariant=True)

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class WorkerDescription(Generic[_WorkerRunFunctionParams_co]):
    func: Callable[[_WorkerRunFunctionParams_co, str, ShutdownEvent, StartedEvent], None]
    func_params: _WorkerRunFunctionParams_co
    name: str = ''
    worker_type: WorkerType = WorkerType.THREAD
    restart_type: RestartType = RestartType.INFINITY
    daemon_type: DaemonType = DaemonType.DAEMON

#####################################################################################################

WorkerDescriptions = tuple[WorkerDescription[_WorkerRunFunctionParams_co], ...]

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class _WorkerInfo(Generic[_WorkerRunFunctionParams_co]):
    err_conn_read: Connection
    join_func: Callable[[None], None]
    close_func: Callable[[], None] | None
    desc: WorkerDescription[_WorkerRunFunctionParams_co]

    #####################################################################################################

    def create_future(self, loop: AbstractEventLoop, /) -> Future[None]:
        def internal_worker() -> None:
            self.join_func(None)
            with with_cleanup(self._err_conn_read_cleanup):
                self._check_and_forward_error()

        return loop.run_in_executor(None, internal_worker)

    #####################################################################################################

    def _check_and_forward_error(self, /) -> None:
        if self.err_conn_read.poll():
            with suppress(EOFError):
                raise self.err_conn_read.recv()

    #####################################################################################################

    def _err_conn_read_cleanup(self, /) -> None:
        self.err_conn_read.close()
        if self.close_func is not None:
            self.close_func()

#####################################################################################################

def _internal_worker_func(
    desc: WorkerDescription[_WorkerRunFunctionParams_co],
    shutdown_event: ShutdownEvent,
    started_event: StartedEvent,
    logger: Logger,
    /,
    err_conn_write: Connection,
) -> None:
    logger.info(f'Initiating worker with pid {current_process().pid} and tid {get_ident()}.')

    if desc.worker_type == WorkerType.PROCESS:
        signal(SIGINT, SIG_IGN)  # отключаем для дочернего процесс реакцию на Ctrl+C, поскольку по дефолту она шлется всем процессам
        setproctitle(desc.name)

    if desc.worker_type == WorkerType.THREAD:
        setthreadtitle(desc.name)
    else:
        setthreadtitle(f'm_{desc.name}')

    try:
        desc.func(desc.func_params, desc.name, shutdown_event, started_event)
    except BaseException as err:  # noqa: PIE786, WPS424 # pylint: disable=broad-except
        is_need_raise_and_logging: Final = not isinstance(err, ShutdownException)
        if is_need_raise_and_logging:
            logger.error(f'Worker error: {err}', exc_info=err)
        err_conn_write.send(err)
        started_event.set()
        if is_need_raise_and_logging:
            raise err
    finally:
        err_conn_write.close()

#####################################################################################################

_SLEEP_SEC_BEFORE_RESTART: Final = 1

#####################################################################################################

def _prepare_worker(
    desc: WorkerDescription[_WorkerRunFunctionParams_co],
    logger: Logger,
    shutdown_event: ShutdownEvent,
    ctx: _MultiprocessContext,
) -> _WorkerInfo[_WorkerRunFunctionParams_co]:
    started_event: Final = ctx.Event()

    while True:
        try:  # noqa: WPS229
            err_conn_read, err_conn_write = ctx.Pipe(duplex=False)
            started_event.clear()

            class_name: type[BaseProcess | Thread] = Thread
            if desc.worker_type == WorkerType.PROCESS:
                class_name = ctx.Process

            worker = class_name(
                target=_internal_worker_func,
                args=(desc, shutdown_event, started_event, logger,),
                kwargs={'err_conn_write': err_conn_write},
                name=desc.name,
                daemon=desc.daemon_type == DaemonType.DAEMON,
            )
            worker.start()
            if desc.worker_type == WorkerType.PROCESS:
                err_conn_write.close()
            started_event.wait()

            if err_conn_read.poll():
                child_process_err = err_conn_read.recv()
                err_conn_read.close()
                raise child_process_err

            return _WorkerInfo(
                err_conn_read=err_conn_read,
                join_func=worker.join,
                close_func=getattr(worker, 'close', None),
                desc=desc,
            )

        except BaseException as err:  # noqa: PIE786, WPS424 # pylint: disable=broad-except
            if isinstance(err, ShutdownException):
                raise err
            if isinstance(err, KeyboardInterrupt):
                raise ShutdownException() from err
            logger.error(f'Prepare worker error: {err}', exc_info=err)
            _sync_sleep(_SLEEP_SEC_BEFORE_RESTART)

#####################################################################################################

def _prepare_worker_infos(
    descriptions: WorkerDescriptions[_WorkerRunFunctionParams_co],
    logger: Logger,
    shutdown_event: ShutdownEvent,
    ctx: _MultiprocessContext,
    /,
) -> Sequence[_WorkerInfo[_WorkerRunFunctionParams_co]]:
    worker_infos: Final[list[_WorkerInfo[_WorkerRunFunctionParams_co]]] = []
    for description in descriptions:
        prepared_worker_info = _prepare_worker(description, logger, shutdown_event, ctx)
        worker_infos.append(prepared_worker_info)
        if shutdown_event.is_set():
            break
    return worker_infos

#####################################################################################################

def _get_future_names(
    futures: dict[Future[None], WorkerDescription[_WorkerRunFunctionParams_co]],
    original_futures: set[Future[None]],
) -> str:
    return ', '.join(futures[original_future].name for original_future in original_futures)

#####################################################################################################

async def _wait_while_pending(
    pending: set[Future[None]],
    futures: dict[Future[None], WorkerDescription[_WorkerRunFunctionParams_co]],
    logger: Logger,
    loop: AbstractEventLoop,
    ctx: _MultiprocessContext,
    shutdown_event: ShutdownEvent,
    /,
) -> None:
    num_times_called = 0
    while pending:
        num_times_called += 1

        finished, pending = await wait(pending, return_when=FIRST_COMPLETED)
        finished_str = _get_future_names(futures, finished)
        pending_str = _get_future_names(futures, pending)
        logger.info(f'Finished: [{finished_str}], Working: [{pending_str}], called counter: {num_times_called}')

        for finished_future in finished:
            finished_desc = futures[finished_future]
            del futures[finished_future]  # noqa: WPS420
            err = finished_future.exception()
            if err:
                if isinstance(err, ShutdownException):
                    shutdown_event.set()
                    continue
                logger.error(f'"{finished_desc.name}" got an exception {err}', exc_info=err)
            elif finished_desc.restart_type != RestartType.ONLY_IF_ERR:
                continue

            if finished_desc.restart_type == RestartType.NONE or shutdown_event.is_set():
                continue
            logger.info(f'"{finished_desc.name}" retry restart after {_SLEEP_SEC_BEFORE_RESTART} sec...')
            await _async_sleep(_SLEEP_SEC_BEFORE_RESTART)
            new_worker_info = _prepare_worker(finished_desc, logger, shutdown_event, ctx)
            new_future = new_worker_info.create_future(loop)
            futures[new_future] = finished_desc
            pending.add(new_future)

#####################################################################################################

# TODO: сделать чтобы воркеры дожидались закрытия друг друга, и гарантировано закрывались в обратной последовательности от процесс открытия

async def run_workers(
    descriptions: WorkerDescriptions[_WorkerRunFunctionParams_co],
    logger: Logger,
    loop: AbstractEventLoop,
    shutdown_event: ShutdownEvent,
    func_after_all_started: AfterAllStartedFunc | None,
    /,
) -> None:
    worker_count: Final = len(descriptions)
    logger.info(f'Starting {worker_count} workers...')

    ctx: Final = _multiprocessing_get_context('spawn')
    if not isinstance(ctx, _MultiprocessContext):
        raise AppException('Can not create spawn context.')

    worker_infos: Final = _prepare_worker_infos(descriptions, logger, shutdown_event, ctx)
    if shutdown_event.is_set():
        return

    if func_after_all_started is not None:
        func_after_all_started(logger)

    loop.set_default_executor(ThreadPoolExecutor(worker_count))
    futures: dict[Future[None], WorkerDescription[_WorkerRunFunctionParams_co]] = {}
    for worker_info in worker_infos:
        future = worker_info.create_future(loop)
        futures[future] = worker_info.desc
    pending: set[Future[None]] = set(futures.keys())

    await _wait_while_pending(
        pending,
        futures,
        logger,
        loop,
        ctx,
        shutdown_event,
    )

#####################################################################################################
