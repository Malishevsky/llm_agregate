#####################################################################################################

from re import RegexFlag, compile as _re_compile
from typing import Any

from fastapi.responses import HTMLResponse
from starlette import status
from starlette.responses import JSONResponse, Response

from l7x.utils.orjson_utils import orjson_default, orjson_dumps

#####################################################################################################

_REMOVE_WHITESPACE = _re_compile(r'\s+', RegexFlag.UNICODE)

#####################################################################################################

class HTMLResponseExt(HTMLResponse):
    def __init__(self, content: str, status_code: int = status.HTTP_200_OK) -> None:  # noqa: WPS110
        super().__init__(_REMOVE_WHITESPACE.sub(' ', content), status_code=status_code)

#####################################################################################################

class JSONResponseExt(JSONResponse):
    def render(self, content: Any) -> bytes:  # noqa: WPS110
        return orjson_dumps(content, default=orjson_default)

#####################################################################################################

def create_error_response(
    err_msg: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    err_code: str = 'ERROR',
    headers: dict[str, str] | None = None,
) -> Response:
    return JSONResponseExt(content={'err': err_code, 'msg': err_msg}, status_code=status_code, headers=headers)

#####################################################################################################
