#####################################################################################################

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from logging import Logger
from re import MULTILINE, UNICODE, Match, compile as _re_compile
from typing import Final

from l7x.types.language import LKey
from l7x.types.mapping import FrozenDict

#####################################################################################################
# AUTOGENERATE_BEGIN
# !!! dont change manually, use
#   ./src/_l10n.py sync

# pylint: disable=line-too-long, too-many-lines

#####################################################################################################

_REC_ERROR_MSG_MAP: Final = FrozenDict({})

#####################################################################################################
# AUTOGENERATE_END
#####################################################################################################

_NOTRANSLATE_WRAP_PATTERN: Final = _re_compile(r'(\[@(?P<non_translated>.*?)@\])', MULTILINE | UNICODE)

#####################################################################################################

def _get_notranslate_group(match: Match[str]) -> str:
    return match.group('non_translated')

#####################################################################################################

def _clean_notranslate_wraps(text: str) -> str:
    return _NOTRANSLATE_WRAP_PATTERN.sub(_get_notranslate_group, text)

#####################################################################################################

@dataclass(frozen=True)
class _LocalizedSentence:
    default_text: str
    localized_sentences: Mapping[LKey, str] = field(default_factory=lambda: FrozenDict({}))

    #####################################################################################################

    def __call__(self, logger: Logger, locale: LKey = LKey.EN, **kwargs: str | int | bool) -> str:
        localized_sentence = self.localized_sentences.get(locale, '')
        if not localized_sentence:
            logger.warning(f'Cannot find localized sentence for "{locale.value}". Use default text: "{self.default_text}"')
            localized_sentence = _clean_notranslate_wraps(self.default_text)
        return localized_sentence.format(**kwargs)

#####################################################################################################

class TKey(_LocalizedSentence, Enum):
    REC_ERROR_MSG = 'Speech recognition failed. Please try again.', _REC_ERROR_MSG_MAP

#####################################################################################################
