#####################################################################################################
from typing import Final

from nicegui import ui
from starlette.requests import Request

from l7x.configs.settings import AppSettings
from l7x.utils.fastapi_utils import AppFastAPI

#####################################################################################################

async def _show_mainpage(request: Request) -> None:
    app: Final = request.app
    settings: Final[AppSettings] = app.app_settings
    with ui.column():
        ui.upload(label='Audio file', auto_upload=True, max_file_size=settings.max_upload_file_size_in_byte)
        ui.label('Select text style postprocessing')
        ui.radio(['FORMAL', 'INFORMAL', 'OFF'])
        ui.textarea(label='Recognized text')
        ui.textarea(label='Summary text')


#####################################################################################################

def mainpage_listener_registrar(app: AppFastAPI, /) -> None:
    ui.page('/', response_timeout=30)(_show_mainpage)

#####################################################################################################

