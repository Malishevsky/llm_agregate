#####################################################################################################

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from http import HTTPStatus
from logging import Logger
from time import time
from types import MappingProxyType
from typing import Final
from urllib.parse import urljoin

from aiohttp import ClientSession

from l7x.configs.constants import TRANSLATE_API_LANGS_CACHE_EXPIRE_WHEN_LIST_EMPTY_SEC
from l7x.configs.settings import AppSettings
from l7x.services.base import BaseService
from l7x.types.lang_services import EMPTY_LANGS, LangInfo, LanguageDetail
from l7x.utils.orjson_utils import orjson_loads

#####################################################################################################

class InvalidRequestError(Exception):
    def __init__(self, status: int) -> None:
        super().__init__()
        self.status: Final = status

#####################################################################################################

class RecognizerLangsService(BaseService, ABC):
    #####################################################################################################

    def __init__(self, app_settings: AppSettings, aiohttp_client: ClientSession, logger: Logger) -> None:
        self._translate_api_langs_cache_expire_sec: Final = app_settings.translate_api_langs_cache_expire_sec
        self._aiohttp_client: Final = aiohttp_client
        self._logger: Final = logger
        self._langs_options: Mapping[str, LanguageDetail] = EMPTY_LANGS
        self._next_update_ts = -1.0

    #####################################################################################################

    async def get_recognizer_lang_options(self, /) -> Mapping[str, LanguageDetail]:
        cur_ts = time()
        if self._next_update_ts <= cur_ts:
            self._next_update_ts = cur_ts + float(self._translate_api_langs_cache_expire_sec)

            try:
                langs_options = await self._get_languages()
            except InvalidRequestError as exc:
                self._logger.warning(f'Return invalid status for get-languages: {exc.status}')
                self._langs_options = EMPTY_LANGS
                self._next_update_ts = cur_ts + min(self._translate_api_langs_cache_expire_sec, 10)
                return self._langs_options

            if not langs_options:
                self._langs_options = EMPTY_LANGS
                self._next_update_ts = cur_ts + TRANSLATE_API_LANGS_CACHE_EXPIRE_WHEN_LIST_EMPTY_SEC
            else:
                self._langs_options = MappingProxyType(langs_options)

        return self._langs_options

    #####################################################################################################

    @abstractmethod
    async def _get_languages(self, /) -> Mapping[str, LanguageDetail]:
        raise NotImplementedError()

#####################################################################################################

class PrivateRecognizerLangsService(RecognizerLangsService):
    #####################################################################################################

    def __init__(self, app_settings: AppSettings, aiohttp_client: ClientSession, logger: Logger) -> None:
        super().__init__(app_settings, aiohttp_client, logger)
        self._url: Final = urljoin(app_settings.translate_api_url, 'api/get-speech-to-text-languages')

    #####################################################################################################

    async def _get_languages(self, /) -> Mapping[str, LanguageDetail]:
        get_languages_resp = await self._aiohttp_client.get(self._url)
        if get_languages_resp.status != HTTPStatus.OK:
            raise InvalidRequestError(status=get_languages_resp.status)

        languages: Sequence[LangInfo] = await get_languages_resp.json(loads=orjson_loads)
        if not languages:
            return {}
        return {
            lang.get('code_alpha_1'): LanguageDetail(code=lang.get('codeName'), rtl=lang.get('rtl'))
            for lang in languages
        }

#####################################################################################################
