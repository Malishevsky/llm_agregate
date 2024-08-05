#####################################################################################################

from abc import ABC, abstractmethod
from http import HTTPStatus
from logging import Logger
from typing import Final
from urllib.parse import urljoin

from aiohttp import ClientSession

from l7x.configs.settings import AppSettings
from l7x.services.base import BaseService
from l7x.services.translation_service import JsonPayload
from l7x.utils.mapping_utils import find_value_by_keys_sequence
from l7x.utils.orjson_utils import orjson_loads

#####################################################################################################

class AutodetectLanguageService(BaseService, ABC):
    #####################################################################################################

    def __init__(self, aiohttp_client: ClientSession, logger: Logger) -> None:
        self._aiohttp_client: Final = aiohttp_client
        self._logger: Final = logger

    #####################################################################################################

    @abstractmethod
    async def detect_language(self, *, text: str) -> str:
        raise NotImplementedError()

#####################################################################################################

class PrivateAutodetectLanguageService(AutodetectLanguageService):
    #####################################################################################################

    def __init__(self, app_settings: AppSettings, aiohttp_client: ClientSession, logger: Logger) -> None:
        super().__init__(aiohttp_client, logger)
        self._url: Final = urljoin(app_settings.translate_api_url, 'api/detect-language')

    #####################################################################################################

    async def detect_language(self, *, text: str) -> str:
        query: Final = {
            'q': text,
        }

        detected_lang_resp: Final = await self._aiohttp_client.post(url=self._url, data=JsonPayload(query))
        if detected_lang_resp.status != HTTPStatus.OK:
            self._logger.warning(f'Return invalid status for api/detect-language [{detected_lang_resp.status}]')
            return ''

        detected_lang_json: Final = await detected_lang_resp.json(loads=orjson_loads)
        return find_value_by_keys_sequence(detected_lang_json, 'result', 0, 0, 'language_code', default='', logger=self._logger)

#####################################################################################################
