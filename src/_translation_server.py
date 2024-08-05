#####################################################################################################

import argparse
from asyncio import run
from logging import Logger
from typing import Final, cast

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config as _HypercornConfig
from hypercorn.typing import ASGIFramework
# pylint: disable-next=no-name-in-module
from pydantic import BaseModel
from setproctitle import setproctitle, setthreadtitle

from l7x.configs.constants import DEFAULT_TRANSLATION_SERVER_PORT

#####################################################################################################

_LANG_CODE: Final = 'code_alpha_1'
_LANGUAGE: Final = 'codeName'

_SUPPORTED_LANGS: Final = (
    {_LANG_CODE: 'en', _LANGUAGE: 'English'},
    {_LANG_CODE: 'de', _LANGUAGE: 'German'},
    {_LANG_CODE: 'ru', _LANGUAGE: 'Russian'},
)

_SUPPORTED_LANGS_CODES: Final = tuple(lang[_LANG_CODE] for lang in _SUPPORTED_LANGS)

#####################################################################################################

class _TranslationRequest(BaseModel):
    translateMode: str  # noqa: N815
    q: str  # noqa: VNE001, WPS111
    source: str | None = None
    target: str

#####################################################################################################

class _TranslationResponse(BaseModel):
    translatedText: str  # noqa: N815
    detectedSourceLanguage: str  # noqa: N815
    sourceText: str  # noqa: N815

#####################################################################################################

class _DetectLanguageRequest(BaseModel):
    q: str  # noqa: VNE001, WPS111

#####################################################################################################

class TranslationApp(FastAPI):
    def __init__(self) -> None:
        super().__init__()

        async def _get_languages() -> JSONResponse:
            return JSONResponse(_SUPPORTED_LANGS)
        self.get('/api/get-languages')(_get_languages)

        async def _translate(req: _TranslationRequest) -> _TranslationResponse:
            if req.source is None:
                req.source = 'en'

            if not (req.source in _SUPPORTED_LANGS_CODES and req.target in _SUPPORTED_LANGS_CODES):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            return _TranslationResponse(
                translatedText=f'[{req.target}] {req.q}',
                detectedSourceLanguage=req.source,
                sourceText=req.q,
            )
        self.post('/api/translate')(_translate)

        async def _detect_language(req: _DetectLanguageRequest) -> JSONResponse:  # pylint: disable=unused-argument
            return JSONResponse({'result': [[{'language_code': 'en'}]]})
        self.post('/api/detect-language')(_detect_language)

#####################################################################################################

def run_mock_translation_server(port: int, logger: Logger | None = None) -> None:
    setproctitle('translation_server')
    setthreadtitle('translation_server')

    if logger is not None:
        logger.info('Translation server started...')

    hypercorn_config: Final = _HypercornConfig()
    hypercorn_config.bind = [f'0.0.0.0:{port}']

    translator: Final = TranslationApp()
    translator_wrapper: Final = cast(ASGIFramework, translator)

    run(serve(translator_wrapper, hypercorn_config))

#####################################################################################################

def main() -> None:
    parser: Final = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=DEFAULT_TRANSLATION_SERVER_PORT)
    args: Final = parser.parse_args()

    run_mock_translation_server(port=args.port)

#####################################################################################################

if __name__ == '__main__':
    main()

#####################################################################################################
