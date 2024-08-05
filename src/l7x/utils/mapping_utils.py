#####################################################################################################

from collections.abc import Callable, Mapping, Sequence
from logging import DEBUG, Logger
from types import UnionType
from typing import Any, Final, Generic, TypeAlias, TypeVar, cast

#####################################################################################################

_ValueFinderReturnTypes = TypeVar('_ValueFinderReturnTypes', int, float, bool, str, Mapping[Any, Any], Sequence[Any])

#####################################################################################################

class FindValueByKeysSequenceException(RuntimeError):
    """Raise when cannot find key or index..."""

#####################################################################################################

_MAPPING_AND_SEQUENCE_TYPES: Final = (Sequence, Mapping)
_STR_AND_INT_TYPES: Final = (str, int)

_SourceType: TypeAlias = Mapping[str, Any] | Sequence[Any] | Mapping[int, Any] | Mapping[str | int, Any]

#####################################################################################################

_CANNOT_FIND_PATH_MSG: Final = 'Cannot find path {args} in {source}, return None.'

#####################################################################################################

def find_value_or_none_by_keys_sequence(
    source: _SourceType,
    /,
    *args: str | int,
    ret_type: type[_ValueFinderReturnTypes],
    logger: Logger | None = None,
) -> _ValueFinderReturnTypes | None:
    cursor: Any = source
    for key in args:
        if cursor is None:
            if logger is not None and logger.isEnabledFor(DEBUG):
                logger.warning(_CANNOT_FIND_PATH_MSG.format(args=args, source=source))
            return None
        if not isinstance(cursor, _MAPPING_AND_SEQUENCE_TYPES):
            cursor_type = type(cursor)
            raise FindValueByKeysSequenceException(f'Source for find by key must be map or sequence, now is {cursor_type}.')
        if not isinstance(key, _STR_AND_INT_TYPES):
            key_type = type(key)
            raise FindValueByKeysSequenceException(f'Key for find by key must be int or str, now is {key_type}.')
        try:
            cursor = cursor[key]  # type: ignore
        except (IndexError, KeyError):
            if logger is not None and logger.isEnabledFor(DEBUG):
                logger.warning(_CANNOT_FIND_PATH_MSG.format(args=args, source=source))
            return None
    if cursor is None:
        if logger is not None and logger.isEnabledFor(DEBUG):
            logger.warning(_CANNOT_FIND_PATH_MSG.format(args=args, source=source))
        return None
    if not isinstance(cursor, ret_type):
        value_type: Final = type(cursor)
        raise FindValueByKeysSequenceException(f'Return value for find by key must be type {ret_type}. Now is {value_type}')
    return cursor

#####################################################################################################

def find_value_by_keys_sequence(
    source: _SourceType,
    /,
    *args: str | int,
    default: _ValueFinderReturnTypes,
    logger: Logger | None = None,
) -> _ValueFinderReturnTypes:
    ret_value: Final = find_value_or_none_by_keys_sequence(source, *args, ret_type=type(default), logger=logger)
    if ret_value is None:
        if logger is not None and logger.isEnabledFor(DEBUG):
            logger.warning(f'By path {args} in {source} is None, return default {default}.')
        return default
    return ret_value

####################################################################################################

class _AbsentValue:
    """Nothing."""

####################################################################################################

class CacheablePropertiesObject:
    #####################################################################################################

    def __init__(self, *, source: _SourceType, logger: Logger | None = None) -> None:
        self._source: Final = source
        self._logger: Final = logger
        self._cache: Final[dict[tuple[str | int, ...], Any]] = {}

    #####################################################################################################

    def get_value_or_none(self, *args: str | int, ret_type: type[_ValueFinderReturnTypes]) -> _ValueFinderReturnTypes | None:
        cached_result: Final = self._cache.get(args, _AbsentValue)
        if cached_result is _AbsentValue:
            result_by_keys: Final = find_value_or_none_by_keys_sequence(self._source, *args, ret_type=ret_type, logger=self._logger)
            self._cache[args] = result_by_keys
            return result_by_keys

        if cached_result is None:
            return None

        if not isinstance(cached_result, ret_type):
            value_type: Final = type(cached_result)
            raise FindValueByKeysSequenceException(f'Return value for find by key must be type {ret_type}. Now is {value_type}')
        return cached_result

    #####################################################################################################

    def get_value(self, *args: str | int, default: _ValueFinderReturnTypes) -> _ValueFinderReturnTypes:
        ret_value: Final = self.get_value_or_none(*args, ret_type=type(default))
        if ret_value is None:
            logger: Final = self._logger
            if logger is not None and logger.isEnabledFor(DEBUG):
                logger.warning(f'By path {args} in {self._source} is None, return default {default}.')
            return default
        return ret_value

####################################################################################################

_FunSelf = TypeVar('_FunSelf', bound=CacheablePropertiesObject)
_FuncReturn = TypeVar('_FuncReturn')

#####################################################################################################

class CacheableProperty(Generic[_FunSelf, _FuncReturn]):
    #####################################################################################################

    def __init__(self, function: Callable[[_FunSelf], _FuncReturn]) -> None:
        self._function: Final = function
        self._attribute_name: str | None = None

        return_type = function.__annotations__.get('return')
        if not isinstance(return_type, (type, UnionType)):
            raise TypeError('return_type must be type or UnionType')

        self._return_value_type: Final = return_type

    #####################################################################################################

    def __set_name__(self, owner: type[_FuncReturn], name: str) -> None:
        attribute_name: Final = self._attribute_name
        if attribute_name is None:
            self._attribute_name = name
        elif attribute_name != name:
            raise TypeError(f'Cannot assign the same cached_property to two different names ({attribute_name!r} and {name!r}).')

    #####################################################################################################

    def __get__(self, instance: _FunSelf, owner: type[_FunSelf]) -> _FuncReturn:
        if self._attribute_name is None:
            raise TypeError('Cannot use cached_property instance without calling __set_name__ on it.')

        cache: Final = instance._cache  # noqa: WPS437

        cache_key: Final = ('$@property@$', self._attribute_name)
        cached_result: Final = cache.get(cache_key, _AbsentValue)

        if cached_result is _AbsentValue:
            attribute_value: Final = self._function(instance)
            cache[cache_key] = attribute_value
            return attribute_value

        if not isinstance(cached_result, self._return_value_type):
            value_type: Final = type(cached_result)
            raise TypeError(f'Return value for cached property must be type {self._return_value_type}. Now is {value_type}')
        return cast(_FuncReturn, cached_result)

#####################################################################################################
