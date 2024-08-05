#####################################################################################################

from collections.abc import Callable, Iterable
from typing import Final, TypeAlias

from l7x.app import App
from l7x.listeners.mainpage_listener import mainpage_listener_registrar

#####################################################################################################

ListenersRegistrars: TypeAlias = Iterable[Callable[[App], None]]

#####################################################################################################

def _get_app_listeners_registrars() -> ListenersRegistrars:
    return [
        mainpage_listener_registrar,
    ]

#####################################################################################################

APP_LISTENERS_REGISTRARS: Final[ListenersRegistrars] = tuple(_get_app_listeners_registrars())

#####################################################################################################
