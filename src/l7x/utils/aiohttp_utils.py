#####################################################################################################

from asyncio import get_event_loop
from ssl import create_default_context as _create_default_ssl_context

from aiohttp import ClientSession, TCPConnector
from certifi import where as _certifi_where

from l7x.utils.orjson_utils import orjson_dumps_to_str

#####################################################################################################

def create_aiohttp_client() -> ClientSession:
    return ClientSession(
        connector=TCPConnector(
            loop=get_event_loop(),
            ssl=_create_default_ssl_context(
                cafile=_certifi_where(),  # cspell:disable-line
            ),
        ),
        json_serialize=orjson_dumps_to_str,
    )

#####################################################################################################
