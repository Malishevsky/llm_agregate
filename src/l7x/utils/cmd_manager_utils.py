#####################################################################################################

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Iterable, MutableSequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager, AsyncExitStack
from dataclasses import dataclass, field
from logging import Logger
from multiprocessing.managers import SyncManager
from queue import Empty, Queue
from threading import Condition
from time import monotonic
from types import UnionType
from typing import Any, Final, Generic, Optional, TypeAlias, TypeVar, Union, cast, final, get_args, get_origin
from uuid import UUID, uuid4

from l7x.configs.settings import AppSettings
from l7x.types.errors import AppException
from l7x.types.shutdown_event import ShutdownEvent
from l7x.utils.loop_utils import CreateEventLoopParams, EventLoopFuncParams, create_event_loop
from l7x.utils.worker_utils import StartedEvent, WorkerDescription, WorkerType

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class WorkerParams(ABC):
    """DO NOTHING."""

#####################################################################################################

_CmdGlobalContext = TypeVar('_CmdGlobalContext')
_CmdLocalContext = TypeVar('_CmdLocalContext')
_CmdReturnValue = TypeVar('_CmdReturnValue')

#####################################################################################################

class BaseCommand(Generic[_CmdGlobalContext, _CmdLocalContext, _CmdReturnValue]):
    #####################################################################################################

    @abstractmethod
    async def execute(
        self,
        *,
        global_context: _CmdGlobalContext,
        local_context: _CmdLocalContext,
    ) -> _CmdReturnValue:
        raise NotImplementedError()

#####################################################################################################

_CmdMiddlewareResult = TypeVar('_CmdMiddlewareResult')

class CmdMiddlewareResults(ABC):
    @abstractmethod
    def get(self, middleware_result_class: type[_CmdMiddlewareResult]) -> _CmdMiddlewareResult:
        raise NotImplementedError()

#####################################################################################################

@final
class CmdMiddlewareBreak(ABC):
    """NOTHING."""

CmdMiddleware: TypeAlias = Callable[
    [_CmdGlobalContext, BaseCommand[_CmdGlobalContext, Any, Any], CmdMiddlewareResults], Awaitable[Any],
]

CmdMiddlewares: TypeAlias = Iterable[CmdMiddleware[_CmdGlobalContext]]

CmdMiddlewaresSelector: TypeAlias = Callable[
    [type[BaseCommand[_CmdGlobalContext, Any, Any]]], CmdMiddlewares[_CmdGlobalContext],
]

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _CallInfo:
    call_id: UUID | None = field(default_factory=uuid4)

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _InputCallInfo(Generic[_CmdGlobalContext, _CmdLocalContext], _CallInfo):
    cmd: BaseCommand[_CmdGlobalContext, _CmdLocalContext, Any]

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _ResultCallInfo(_CallInfo):
    execute_result: Any

#####################################################################################################

_GlobalContextCreatorAdditionalParams = TypeVar('_GlobalContextCreatorAdditionalParams')

CmdGlobalContextCreatorReturn: TypeAlias = tuple[_CmdGlobalContext, Optional[CmdMiddlewaresSelector[_CmdGlobalContext]]]

_CmdGlobalContextCreator: TypeAlias = Callable[
    [Logger, AppSettings, _GlobalContextCreatorAdditionalParams],
    Awaitable[CmdGlobalContextCreatorReturn[_CmdGlobalContext]],
]

#####################################################################################################

_CmdLocalContextCreator: TypeAlias = Callable[[_CmdGlobalContext, CmdMiddlewareResults], Awaitable[_CmdLocalContext]]

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class _ManagerWorkerParams(Generic[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext], WorkerParams):
    app_settings: AppSettings
    global_context_creator: _CmdGlobalContextCreator[_GlobalContextCreatorAdditionalParams, _CmdGlobalContext]
    global_context_creator_additional_params: _GlobalContextCreatorAdditionalParams
    local_context_creator: _CmdLocalContextCreator[_CmdGlobalContext, _CmdLocalContext]
    call_queue: Queue[_InputCallInfo[_CmdGlobalContext, _CmdLocalContext]]
    call_results_condition: Condition
    call_results: MutableSequence[_ResultCallInfo]

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class _ManagerWorkerExtParams(Generic[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext]):
    loop_name: str
    worker_params: _ManagerWorkerParams[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext]

#####################################################################################################

async def _create_exit_stack_from_context(context: Any, /) -> AsyncExitStack:
    context_exit_stack: Final = AsyncExitStack()
    if isinstance(context, AbstractAsyncContextManager):
        await context_exit_stack.enter_async_context(context)
    if isinstance(context, AbstractContextManager):
        context_exit_stack.enter_context(context)
    return context_exit_stack

#####################################################################################################

async def _execute_command(
    global_context: _CmdGlobalContext,
    local_context_creator: _CmdLocalContextCreator[_CmdGlobalContext, _CmdLocalContext],
    middleware_results: CmdMiddlewareResults,
    cmd: BaseCommand[_CmdGlobalContext, _CmdLocalContext, _CmdReturnValue],
    /,
) -> _CmdReturnValue:
    local_context: Final = await local_context_creator(global_context, middleware_results)
    async with await _create_exit_stack_from_context(local_context):
        return await cmd.execute(
            global_context=global_context,
            local_context=local_context,
        )
    raise AppException('Cmd not executed')  # fix mypy 'Missing return statement'

#####################################################################################################

class _CmdMiddlewareResults(CmdMiddlewareResults):
    #####################################################################################################

    def __init__(self) -> None:
        self._middleware_results: Final[dict[type[Any], Any]] = {}

    #####################################################################################################

    def get(self, middleware_result_class: type[_CmdMiddlewareResult]) -> _CmdMiddlewareResult:
        ret: Final = self._middleware_results.get(middleware_result_class)
        if not isinstance(ret, middleware_result_class):
            raise TypeError('Query invalid middleware result')
        return ret

    #####################################################################################################

    def put_middleware_result(self, middleware_result: Any) -> None:
        if middleware_result is None:
            return
        middleware_result_class: Final = type(middleware_result)
        middleware_results: Final = self._middleware_results
        if middleware_result_class in middleware_results:
            raise TypeError('Put duplicate middleware result')
        middleware_results[middleware_result_class] = middleware_result

    #####################################################################################################

    def clear_middleware_results(self) -> None:
        self._middleware_results.clear()

#####################################################################################################

async def _cmd_manager_worker(
    elp_params: EventLoopFuncParams[_ManagerWorkerExtParams[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext]],
    /,
) -> None:
    ext: Final = elp_params.ext
    logger: Final = elp_params.logger
    app_settings: Final = elp_params.app_settings

    logger.info(f'Worker process "{ext.loop_name}" starting...')

    shutdown_event: Final = elp_params.shutdown_event

    worker_params: Final = ext.worker_params
    call_queue: Final = worker_params.call_queue
    call_results: Final = worker_params.call_results
    call_results_condition: Final = worker_params.call_results_condition

    global_context, middlewares_selector = await worker_params.global_context_creator(
        logger,
        app_settings,
        worker_params.global_context_creator_additional_params,
    )

    local_context_creator: Final = worker_params.local_context_creator

    middleware_results: Final = _CmdMiddlewareResults()

    func_after_all_started: Final = elp_params.func_after_all_started
    if func_after_all_started is not None:
        func_after_all_started(logger)

    async with await _create_exit_stack_from_context(global_context):

        while not shutdown_event.is_set():
            input_call_info: _InputCallInfo[Any, Any] | None = None
            try:
                input_call_info = call_queue.get(timeout=2)
            except Empty:
                continue

            if input_call_info is None:
                raise AppException('input_call_info is None')

            logger.debug(input_call_info)

            call_id = input_call_info.call_id

            cmd = input_call_info.cmd

            logger.info(f'handle {cmd}')
            start_ts = monotonic()

            allow_execute = True
            if middlewares_selector is not None:
                middlewares = middlewares_selector(type(cmd))
                for middleware in middlewares:
                    middleware_result = await middleware(global_context, cmd, middleware_results)
                    if middleware_result is CmdMiddlewareBreak:
                        allow_execute = False
                        break
                    middleware_results.put_middleware_result(middleware_result)

            if allow_execute:
                try:
                    execute_result = await _execute_command(global_context, local_context_creator, middleware_results, cmd)
                except BaseException as err:  # noqa: PIE786, WPS424 # pylint: disable=broad-except
                    if call_id is None:
                        raise err
                    execute_result = err

            middleware_results.clear_middleware_results()

            delta_ts = monotonic() - start_ts
            logger.info(f'{cmd} ({delta_ts} sec)')

            if call_id is not None:
                call_return_info = _ResultCallInfo(call_id=call_id, execute_result=execute_result)
                with call_results_condition:
                    call_results.append(call_return_info)
                    call_results_condition.notify_all()

#####################################################################################################

def _run_cmd_manager_worker(
    cmd_manager_params: _ManagerWorkerParams[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext],
    worker_name: str,
    shutdown_event: ShutdownEvent,
    started_event: StartedEvent,
    /,
) -> None:
    app_settings: Final = cmd_manager_params.app_settings

    def after_all_started(logger: Logger) -> None:
        logger.info(f'Worker process "{worker_name}" started')
        started_event.set()

    create_event_loop(CreateEventLoopParams(
        func=_cmd_manager_worker,
        app_settings=app_settings,
        loop_name=worker_name,
        shutdown_event=shutdown_event,
        ext=_ManagerWorkerExtParams(loop_name=worker_name, worker_params=cmd_manager_params),
        func_after_all_started=after_all_started,
    ))

#####################################################################################################

DEFAULT_CMD_EXECUTE_WAIT_TIMEOUT_SEC: Final[float] = 10.0

#####################################################################################################

class CmdManager(Generic[_CmdGlobalContext, _CmdLocalContext]):
    #####################################################################################################

    @abstractmethod
    def send_and_wait_result(
        self,
        cmd: BaseCommand[_CmdGlobalContext, _CmdLocalContext, _CmdReturnValue],
        *,
        type_ret: type[_CmdReturnValue] | None = None,
        call_timeout_sec: float | None = DEFAULT_CMD_EXECUTE_WAIT_TIMEOUT_SEC,
    ) -> _CmdReturnValue:
        raise NotImplementedError()

    #####################################################################################################

    @abstractmethod
    def send(self, cmd: BaseCommand[_CmdGlobalContext, _CmdLocalContext, Any]) -> None:
        raise NotImplementedError()

#####################################################################################################

def _get_origin_type(type_ret: type) -> type | tuple[type, ...]:
    origin_type: Final = get_origin(type_ret)
    if origin_type is None:
        return type_ret
    if origin_type is UnionType or origin_type is Union:
        union_types: list[type] = []
        for hint in get_args(type_ret):
            origin_hint_type = _get_origin_type(hint)
            if isinstance(origin_hint_type, Iterable):
                union_types.extend(origin_hint_type)
            else:
                union_types.append(origin_hint_type)
        return tuple(union_types)
    return cast(type, origin_type)

#####################################################################################################

class CmdManagerImpl(
    Generic[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext],
    CmdManager[_CmdGlobalContext, _CmdLocalContext],
):
    #####################################################################################################

    _WORKER_PARAMS_TYPE: Final[TypeAlias] = _ManagerWorkerParams[_CmdGlobalContext, _GlobalContextCreatorAdditionalParams, _CmdLocalContext]

    #####################################################################################################

    def __init__(
        self,
        worker_count: int,
        global_context_creator: _CmdGlobalContextCreator[_GlobalContextCreatorAdditionalParams, _CmdGlobalContext],
        global_context_creator_additional_params: _GlobalContextCreatorAdditionalParams,
        local_context_creator: _CmdLocalContextCreator[_CmdGlobalContext, _CmdLocalContext],
        manager: SyncManager,
        logger: Logger,
        app_settings: AppSettings,
        name_prefix: str = 'command_processor_',
    ) -> None:
        self._logger: Final = logger
        self._is_disable_timeout: Final = app_settings.is_dev_mode

        self._worker_params = CmdManagerImpl._WORKER_PARAMS_TYPE(  # noqa: WPS437
            app_settings=app_settings,
            global_context_creator=global_context_creator,
            global_context_creator_additional_params=global_context_creator_additional_params,
            local_context_creator=local_context_creator,
            call_queue=manager.Queue(),
            call_results_condition=manager.Condition(),
            call_results=manager.list(),
        )

        descriptions: Final[list[WorkerDescription[WorkerParams]]] = []
        for manager_worker_index in range(worker_count):
            manager_worker_desc = WorkerDescription(
                func=_run_cmd_manager_worker,
                name=f'{name_prefix}{manager_worker_index}',
                func_params=self._worker_params,
                worker_type=WorkerType.PROCESS,
            )
            descriptions.append(manager_worker_desc)
        self._descriptions = tuple(descriptions)

    #####################################################################################################

    @property
    def worker_descriptions(self) -> Iterable[WorkerDescription[WorkerParams]]:
        return self._descriptions

    #####################################################################################################

    def send_and_wait_result(
        self,
        cmd: BaseCommand[_CmdGlobalContext, _CmdLocalContext, _CmdReturnValue],
        *,
        type_ret: type[_CmdReturnValue] | None = None,
        call_timeout_sec: float | None = DEFAULT_CMD_EXECUTE_WAIT_TIMEOUT_SEC,
    ) -> _CmdReturnValue:
        call_info: Final = _InputCallInfo(cmd=cmd)
        worker_params: Final = self._worker_params
        worker_params.call_queue.put(call_info)

        call_results: Final = worker_params.call_results
        wait_predicate: Final = lambda: tuple(
            (index, cri) for index, cri in enumerate(call_results) if cri.call_id == call_info.call_id
        )

        call_results_condition: Final = worker_params.call_results_condition
        with call_results_condition:
            call_result_infos: Final = call_results_condition.wait_for(
                wait_predicate,
                timeout=None if self._is_disable_timeout else call_timeout_sec,
            )
            if not call_result_infos:
                raise AppException(detail='Timeout. Server busy.')
            self._logger.debug(call_result_infos)
            (index, call_result_info) = call_result_infos[0]
            call_results.pop(index)

        execute_result: Final = call_result_info.execute_result
        if isinstance(execute_result, BaseException):
            raise execute_result
        if type_ret is not None and not isinstance(execute_result, _get_origin_type(type_ret)):
            execute_result_type = type(execute_result)
            execute_need_type = str(type_ret)
            raise TypeError(f'type {execute_result_type} must be {execute_need_type}')

        return cast(_CmdReturnValue, execute_result)

    #####################################################################################################

    def send(self, cmd: BaseCommand[_CmdGlobalContext, _CmdLocalContext, Any]) -> None:
        call_info: Final = _InputCallInfo(call_id=None, cmd=cmd)
        self._worker_params.call_queue.put(call_info)

#####################################################################################################
