from logging import Logger
from typing import Final

from tokenizers import Tokenizer
from torch import float16 as _torch_float16
from transformers import LlamaForCausalLM, AutoModelForCausalLM, AutoTokenizer

from l7x.configs.settings import AppSettings
from l7x.utils.cmd_manager_utils import CmdGlobalContextCreatorReturn, CmdMiddlewareResults


class BaseCmdGlobalContext:
    #####################################################################################################

    def __init__(
        self,
        logger: Logger,
        app_settings: AppSettings,
        llm_model: LlamaForCausalLM,
        llm_tokenizer: Tokenizer,
    ) -> None:
        self._logger = logger
        self._app_settings = app_settings
        self._llm_model = llm_model
        self._llm_tokenizer = llm_tokenizer

    #####################################################################################################

    @property
    def logger(self) -> Logger:
        return self._logger

    #####################################################################################################

    @property
    def app_settings(self) -> AppSettings:
        return self._app_settings

    #####################################################################################################

    @property
    def model(self) -> LlamaForCausalLM:
        return self._llm_model

    #####################################################################################################

    @property
    def tokenizer(self) -> Tokenizer:
        return self._llm_tokenizer

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
    model_id: Final = app_settings.llm_model_id
    cache_dir: Final = app_settings.models_cache_dir

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map='auto',
        cache_dir=cache_dir,
        torch_dtype=_torch_float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    return BaseCmdGlobalContext(logger, app_settings, llm_model=model, llm_tokenizer=tokenizer), None

#####################################################################################################

async def creator_local_tokens_cmd_context(
    global_context: BaseCmdGlobalContext,
    _middleware_results: CmdMiddlewareResults,
) -> BaseCmdLocalContext:
    return BaseCmdLocalContext(global_context)

#####################################################################################################
