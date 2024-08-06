#####################################################################################################

from abc import abstractmethod
from http import HTTPStatus
from logging import Logger
from typing import Any, Final
from urllib.parse import urljoin

from aiohttp import BytesPayload, ClientSession, FormData

from l7x.configs.settings import AppSettings
from l7x.services.base import BaseService
from l7x.utils.orjson_utils import orjson_dumps, orjson_loads

#####################################################################################################

class JsonPayload(BytesPayload):
    #####################################################################################################

    def __init__(self, value_for_send: Any) -> None:
        super().__init__(orjson_dumps(value_for_send), content_type='application/json', encoding='utf-8')

#####################################################################################################

class RecognizeService(BaseService):
    #####################################################################################################

    def __init__(self, aiohttp_client: ClientSession, logger: Logger) -> None:
        self._aiohttp_client: Final = aiohttp_client
        self._logger: Final = logger

    #####################################################################################################

    @abstractmethod
    async def recognize(self, *, file_name: str, wav: bytes, language: str, mime_type: str) -> str:
        raise NotImplementedError()

#####################################################################################################

class PrivateRecognizeService(RecognizeService):
    #####################################################################################################

    def __init__(self, app_settings: AppSettings, aiohttp_client: ClientSession, logger: Logger) -> None:
        super().__init__(aiohttp_client, logger)
        self._url: Final = urljoin(app_settings.recognizer_api_url, '/speech-to-text')

    #####################################################################################################

    async def recognize(self, *, file_name: str, wav: bytes, language: str | None, mime_type: str = 'audio/wav') -> str:
        data = FormData()
        if language is not None:
            data.add_field('lang', language)
        data.add_field('output_native', 'false')
        data.add_field('file', wav, filename=file_name, content_type=mime_type)
        data.add_field('denoise', 'false')

        recognize_resp = await self._aiohttp_client.post(
            url=self._url,
            data=data,
        )

        if recognize_resp.status == HTTPStatus.OK:
            recognize_json = await recognize_resp.json(loads=orjson_loads)
            recognized_text = recognize_json.get('result', '')
        else:
            self._logger.warning(f'Return invalid status for /speech-to-text [{recognize_resp.status}]')
            recognized_text = ''

        return recognized_text

#####################################################################################################
