from logging import Logger
from typing import Final

from l7x.configs.settings import AppSettings
from l7x.utils.cmd_manager_utils import CmdGlobalContextCreatorReturn, CmdMiddlewareResults


class BaseCmdGlobalContext:
    #####################################################################################################

    def __init__(self, logger: Logger, app_settings: AppSettings) -> None:
        self._logger = logger
        self._app_settings = app_settings

    #####################################################################################################

    @property
    def logger(self) -> Logger:
        return self._logger

    #####################################################################################################

    @property
    def app_settings(self) -> AppSettings:
        return self._app_settings

#####################################################################################################

class BaseCmdLocalContext:
    #####################################################################################################

    def __init__(self, global_context: BaseCmdGlobalContext) -> None:
        self._global_context: Final = global_context

#####################################################################################################

async def creator_base_global_cmd_context(
    logger: Logger,
    app_settings: AppSettings,
    _additional_params: None,
) -> CmdGlobalContextCreatorReturn:
    return BaseCmdGlobalContext(logger, app_settings), None

#####################################################################################################

async def creator_local_tokens_cmd_context(
    global_context: BaseCmdGlobalContext,
    _middleware_results: CmdMiddlewareResults,
) -> BaseCmdLocalContext:
    return BaseCmdLocalContext(global_context)

#####################################################################################################
