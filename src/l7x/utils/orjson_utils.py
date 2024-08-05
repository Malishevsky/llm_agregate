#####################################################################################################

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Final

# pylint: disable-next=no-name-in-module, unused-import
from orjson import OPT_INDENT_2, OPT_SORT_KEYS, JSONDecodeError, dumps as orjson_dumps, loads as orjson_loads  # noqa: F401

#####################################################################################################

def orjson_default(obj_for_dumps: Any) -> Any:
    if isinstance(obj_for_dumps, Mapping):
        return dict(obj_for_dumps)
    if isinstance(obj_for_dumps, set | Sequence | Iterable):
        return tuple(obj_for_dumps)
    if isinstance(obj_for_dumps, object):
        obj_for_dumps_type: Final = type(obj_for_dumps)
        if obj_for_dumps_type.__str__ is not object.__str__:  # noqa: WPS609

            return str(obj_for_dumps)
        if obj_for_dumps_type.__repr__ is not object.__repr__:  # noqa: WPS609
            return repr(obj_for_dumps)
        return vars(obj_for_dumps)  # noqa: WPS421
    raise TypeError()

#####################################################################################################

def orjson_dumps_to_str(obj_for_dump: Any) -> str:
    return orjson_dumps(obj_for_dump, default=orjson_default).decode(encoding='utf-8')

#####################################################################################################

def orjson_dumps_to_str_pretty(obj_for_dump: Any) -> str:
    return orjson_dumps(obj_for_dump, option=OPT_INDENT_2 | OPT_SORT_KEYS, default=orjson_default).decode(encoding='utf-8')

#####################################################################################################

def orjson_dumps_to_bytes_pretty(obj_for_dump: Any) -> bytes:
    return orjson_dumps(obj_for_dump, option=OPT_INDENT_2, default=orjson_default)

#####################################################################################################
