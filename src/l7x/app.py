#####################################################################################################

from logging import Logger
from multiprocessing.managers import SyncManager
from typing import Final

from nicegui.core import app as _nicegui_app

from l7x.configs.settings import AppSettings
from l7x.services.langs_service import PrivateLangsService
from l7x.services.recognize_langs_service import PrivateRecognizerLangsService
from l7x.services.recognize_service import PrivateRecognizeService
from l7x.services.translation_service import PrivateTranslationService
from l7x.utils.aiohttp_utils import create_aiohttp_client
from l7x.utils.fastapi_utils import AppFastAPI
from l7x.utils.loop_utils import AfterAllStartedFunc

#####################################################################################################

class App(AppFastAPI):
    #####################################################################################################

    def __init__(
        self,
        logger: Logger,
        app_settings: AppSettings,
        func_after_all_started: AfterAllStartedFunc | None = None,
        cmd_manager: SyncManager | None = None,
    ) -> None:
        def on_startup() -> None:
            if func_after_all_started is not None:
                func_after_all_started(logger)

        super().__init__(logger, app_settings, on_startup=[on_startup])

        self._aiohttp_client: Final = create_aiohttp_client()

        _nicegui_app.logger = self.logger
        _nicegui_app.languages_service = PrivateLangsService(app_settings, self._aiohttp_client, logger)
        _nicegui_app.translation_service = PrivateTranslationService(app_settings, self._aiohttp_client, logger)
        _nicegui_app.recognize_service = PrivateRecognizeService(app_settings, self._aiohttp_client, logger)
        _nicegui_app.rec_languages_service = PrivateRecognizerLangsService(app_settings, self._aiohttp_client, logger)
        _nicegui_app.add_static_files(url_path='/static', local_directory='./static')
        _nicegui_app.settings = app_settings
        _nicegui_app.cmd_manager = cmd_manager

#####################################################################################################
