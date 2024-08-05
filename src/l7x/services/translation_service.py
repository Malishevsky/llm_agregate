#####################################################################################################

from abc import ABC, abstractmethod
from collections.abc import Iterable
from http import HTTPStatus
from logging import Logger
from typing import Any, Final
from urllib.parse import urljoin

from aiohttp import BytesPayload, ClientSession

from l7x.configs.settings import AppSettings
from l7x.services.base import BaseService
from l7x.utils.orjson_utils import orjson_dumps, orjson_loads

#####################################################################################################

class JsonPayload(BytesPayload):
    #####################################################################################################

    def __init__(self, value_for_send: Any) -> None:
        super().__init__(orjson_dumps(value_for_send), content_type='application/json', encoding='utf-8')

#####################################################################################################

class TranslationService(BaseService, ABC):
    #####################################################################################################

    def __init__(self, aiohttp_client: ClientSession, logger: Logger) -> None:
        self._aiohttp_client: Final = aiohttp_client
        self._logger: Final = logger

    #####################################################################################################

    @abstractmethod
    async def translate(self, *, text: str, dest_lang: str, source_lang: str) -> tuple[str, str]:
        raise NotImplementedError()

#####################################################################################################

class PrivateTranslationService(TranslationService):
    #####################################################################################################

    def __init__(self, app_settings: AppSettings, aiohttp_client: ClientSession, logger: Logger) -> None:
        super().__init__(aiohttp_client, logger)
        self._url: Final = urljoin(app_settings.translate_api_url, 'api/translate')

    #####################################################################################################

    async def translate(self, *, text: str, target_lang: str, source_lang: str) -> str:
        payload: Final = {
            'translateMode': 'text',
            'q': text,
            'target': target_lang,
        }

        if source_lang:
            payload['source'] = source_lang

        translate_resp = await self._aiohttp_client.post(
            url=self._url,
            data=JsonPayload(payload),
        )

        if translate_resp.status == HTTPStatus.OK:
            translate_json = await translate_resp.json(loads=orjson_loads)
            translated_text = translate_json.get('translatedText', '')
            # detected_source = translate_json.get('detectedSourceLanguage', '')
        else:
            self._logger.warning(f'Return invalid status for api/translate [{translate_resp.status}]')
            translated_text = ''
            # detected_source = ''

        return translated_text

#####################################################################################################
