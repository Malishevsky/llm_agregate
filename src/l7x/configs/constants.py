#####################################################################################################

from typing import Final

#####################################################################################################

DEFAULT_TRANSLATION_SERVER_PORT: Final = 8081
TRANSLATE_API_LANGS_CACHE_EXPIRE_WHEN_LIST_EMPTY_SEC: Final[float] = 5.0
RECONGIZER_MIME_TYPES = frozenset([
    'audio/wav',
    'audio/x-ms-wma',
    'audio/mpeg',
    'audio/ogg',
    'audio/mp4',
    'audio/x-m4a',
    'video/x-flv',
    'video/x-msvideo',
    'video/mp4',
    'video/quicktime',
    'video/x-matroska'
])

#####################################################################################################
