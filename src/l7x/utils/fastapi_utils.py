#####################################################################################################

from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Coroutine, Sequence
from logging import Logger
from time import monotonic
from typing import Any, Final, cast
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.utils import is_body_allowed_for_status_code
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request as _StarletteRequest
from starlette.responses import FileResponse, PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp

from l7x.configs.settings import AppSettings
from l7x.utils.orjson_utils import orjson_dumps_to_str_pretty
from l7x.utils.response_utils import create_error_response

#####################################################################################################

class _ValidateMaxContentLengthMiddleware(BaseHTTPMiddleware):
    #####################################################################################################

    def __init__(
        self,
        app: ASGIApp,
        router_paths: Sequence[str] | None = None,
        max_size_in_byte: int = -1,
    ) -> None:
        super().__init__(app)
        self._router_paths = router_paths
        self._max_size_in_byte = max_size_in_byte
        self._methods = frozenset(('POST', 'PUT',))

    #####################################################################################################

    async def dispatch(self, request: _StarletteRequest, call_next: RequestResponseEndpoint) -> Response:
        max_size_in_byte: Final = self._max_size_in_byte
        if max_size_in_byte < 0:
            return await call_next(request)

        scope: Final = request.scope
        if scope['method'] not in self._methods:
            return await call_next(request)

        if self._router_paths is not None and scope['path'] not in self._router_paths:
            return await call_next(request)

        headers: Final = request.headers
        if 'content-length' not in headers:
            return create_error_response('content-length header in the request is required', status.HTTP_411_LENGTH_REQUIRED)

        content_len: Final = int(headers['content-length'])
        if content_len > max_size_in_byte:
            return create_error_response(
                f'Request Entity Too Large: {content_len} bytes. Maximum allowable size: {max_size_in_byte} bytes.',
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        return await call_next(request)

#####################################################################################################

async def _get_root() -> Response:
    return PlainTextResponse('OK')

#####################################################################################################

async def _get_favicon_ico() -> FileResponse:
    return FileResponse("static/images/favicon.ico")

#####################################################################################################
class AppFastAPI(FastAPI):
    #####################################################################################################

    def __init__(
        self,
        logger: Logger,
        app_settings: AppSettings,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
    ) -> None:
        super().__init__(
            debug=app_settings.is_dev_mode,
            root_path=urlparse(app_settings.server_url).path.strip('/'),
            on_shutdown=on_shutdown,
            on_startup=on_startup,
            exception_handlers={
                Exception: _http_exception_handler,
                HTTPException: _http_exception_handler,
            },
        )

        self._app_settings: Final = app_settings
        self._logger: Final = logger

        self.router.route_class = _AppDevAPIRoute if app_settings.is_dev_mode else _AppAPIRoute

        self.add_middleware(
            _ValidateMaxContentLengthMiddleware,
            max_size_in_byte=app_settings.max_upload_file_size_in_byte,
        )

        self.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        self.get('/test')(_get_root)
        self.get('/favicon.ico', include_in_schema=False)(_get_favicon_ico)

    #####################################################################################################

    @property
    def logger(self, /) -> Logger:
        return self._logger

    #####################################################################################################

    @property
    def app_settings(self, /) -> AppSettings:
        return self._app_settings

#####################################################################################################

class AppRequest(_StarletteRequest, metaclass=ABCMeta):
    #####################################################################################################

    @property
    @abstractmethod
    def app(self) -> AppFastAPI:
        raise NotImplementedError()

#####################################################################################################

_INTERNAL_ERROR_STATUS_CODE: Final = 500

#####################################################################################################

async def _http_exception_handler(req: _StarletteRequest, exc: Exception) -> Response:
    app: Final = cast(AppRequest, req).app
    app.logger.error(f'HTTP exception handler got {exc}', exc_info=exc)
    if app.debug is True:
        raise exc

    status_code: Final = getattr(exc, 'status_code', _INTERNAL_ERROR_STATUS_CODE)
    headers: Final = getattr(exc, 'headers', None)

    if is_body_allowed_for_status_code(status_code):
        err_code: Final = getattr(exc, 'err_code', 'ERROR')
        err_msg: Final = getattr(exc, 'detail', err_code) if status_code < _INTERNAL_ERROR_STATUS_CODE else err_code
        return create_error_response(err_code=err_code, err_msg=err_msg, status_code=status_code, headers=headers)

    return Response(status_code=status_code, headers=headers)

#####################################################################################################

class _AppAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable[[_StarletteRequest], Coroutine[Any, Any, Response]]:
        original_route_handler: Final = super().get_route_handler()

        async def custom_route_handler(req: _StarletteRequest) -> Response:
            start_ts: Final = monotonic()
            logger: Final = cast(AppRequest, req).app.logger
            logger.info(f'{req.method} {req.url}')
            res: Final = await original_route_handler(req)
            delta_sec: Final = monotonic() - start_ts
            logger.info(f'{req.method} {req.url} [{res.status_code}] ({delta_sec} sec)')
            return res

        return custom_route_handler

#####################################################################################################

async def _decode_req_body(req: _StarletteRequest) -> str | None:
    req_body: Final = await req.body()
    try:
        return req_body.decode('utf-8')
    except UnicodeDecodeError:
        return None

#####################################################################################################

async def _decode_req_form(req: _StarletteRequest) -> str | None:
    req_from: Final = await req.form()
    try:
        return orjson_dumps_to_str_pretty(req_from)
    except UnicodeDecodeError:  # pragma: no cover  # TODO: Добавить покрытие тестом
        return None

#####################################################################################################

class _AppDevAPIRoute(APIRoute):
    #####################################################################################################

    def get_route_handler(self) -> Callable[[_StarletteRequest], Coroutine[Any, Any, Response]]:
        original_route_handler: Final = super().get_route_handler()

        async def custom_route_handler(req: _StarletteRequest) -> Response:
            start_ts: Final = monotonic()
            logger: Final = cast(AppRequest, req).app.logger
            req_body_str = await _decode_req_body(req)
            if req_body_str is None:
                req_body_str = await _decode_req_form(req)
            if req_body_str is None:  # pragma: no cover  # TODO: Добавить покрытие тестом
                req_body_str = 'UnicodeDecodeError'
            logger.info(f'{req.method} {req.url} {req_body_str}')

            res: Final = await original_route_handler(req)
            try:
                res_body_str = res.body.decode('utf-8')
            except UnicodeDecodeError:
                res_body_str = 'UnicodeDecodeError'
            delta_sec: Final = monotonic() - start_ts
            logger.info(f'{req.method} {req.url} [{res.status_code}] ({delta_sec} sec) {res_body_str}')
            return res

        return custom_route_handler

#####################################################################################################

def redirect_or_nothing(location_url: str) -> Response:
    if location_url:
        return RedirectResponse(location_url)

    return Response()

#####################################################################################################
