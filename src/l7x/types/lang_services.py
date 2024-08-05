from types import MappingProxyType
from typing import Final, TypedDict

from pydantic.dataclasses import dataclass

#####################################################################################################

class LangInfo(TypedDict):
    code_alpha_1: str  # noqa: WPS114
    codeName: str  # noqa: N815
    rtl: bool

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class LanguageDetail:
    code: str
    rtl: bool

#####################################################################################################

EMPTY_LANGS: Final = MappingProxyType[str, LanguageDetail]({})

#####################################################################################################
