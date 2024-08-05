#####################################################################################################

from collections.abc import Iterable
from logging import Logger
from typing import Final

from aiohttp import ClientSession

from l7x.configs.settings import AppSettings
from l7x.services.autodetect_lang_service import AutodetectLanguageService, PrivateAutodetectLanguageService
from l7x.services.base import BaseServiceDecl
from l7x.services.langs_service import LangsService, PrivateLangsService
from l7x.services.translation_service import PrivateTranslationService, TranslationService

#####################################################################################################

def private_service_creator(app_settings: AppSettings, aiohttp_client: ClientSession, logger: Logger) -> Iterable[BaseServiceDecl]:
    private_langs_service: Final = PrivateLangsService(app_settings, aiohttp_client, logger)
    private_autodetect_language_service: Final = PrivateAutodetectLanguageService(app_settings, aiohttp_client, logger)
    private_translation_service: Final = PrivateTranslationService(app_settings, aiohttp_client, logger)
    return (
        (LangsService, private_langs_service),
        (AutodetectLanguageService, private_autodetect_language_service),
        (TranslationService, private_translation_service),
    )

#####################################################################################################
