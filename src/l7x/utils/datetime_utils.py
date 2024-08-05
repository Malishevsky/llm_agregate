#####################################################################################################

from datetime import datetime, timedelta, timezone, tzinfo
from re import Pattern, compile
from typing import Any, Final

#####################################################################################################

TIME_OFFSET_VALIDATION_PATTERN: Pattern = compile(r'^[+-]\d{2}:\d{2}$')

#####################################################################################################

class _Utc(tzinfo):
    #####################################################################################################

    _ZERO: Final = timedelta(0)

    __slots__ = ()

    #####################################################################################################

    def utcoffset(self, _: datetime | None) -> timedelta:
        return self._ZERO

    #####################################################################################################

    def dst(self, _: datetime | None) -> timedelta:
        return self._ZERO

    #####################################################################################################

    def tzname(self, _: datetime | None) -> str:
        return 'UTC'

#####################################################################################################

def _get_utc() -> tzinfo:
    try:
        utc: tzinfo | None = timezone.utc
    except AttributeError:
        utc = None

    if utc is None:
        return _Utc()
    return utc

#####################################################################################################

UTC_ZONE: Final = _get_utc()

#####################################################################################################

def now_utc() -> datetime:
    return replace_datetime_timezone_to_utc(datetime.now(UTC_ZONE))

#####################################################################################################

def zero_utc() -> datetime:
    return replace_datetime_timezone_to_utc(datetime.fromtimestamp(0, UTC_ZONE))

#####################################################################################################

def replace_datetime_timezone_to_utc_none(datetime_for_replace: datetime | None) -> datetime | None:
    return replace_datetime_timezone_to_utc(datetime_for_replace) if datetime_for_replace is not None else None

#####################################################################################################

def replace_datetime_timezone_to_utc(datetime_for_replace: datetime) -> datetime:
    return datetime_for_replace.replace(tzinfo=UTC_ZONE) if datetime_for_replace.tzinfo is None else datetime_for_replace

#####################################################################################################

def replace_datetime_timezone_to_utc_in_dict(dict_with_dt: dict[str, Any], *field_names: str) -> None:
    for field_name in field_names:
        datetime_for_replace = dict_with_dt.get(field_name)
        if datetime_for_replace is None:
            continue
        if not isinstance(datetime_for_replace, datetime):
            raise ValueError(f'{field_name} is not datetime')
        dict_with_dt[field_name] = replace_datetime_timezone_to_utc_none(datetime_for_replace)

#####################################################################################################
