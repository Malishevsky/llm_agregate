#####################################################################################################

from collections.abc import Iterator, Mapping
from typing import Any, Final

#####################################################################################################

class FrozenDict(Mapping[Any, Any]):
    #####################################################################################################

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._warehouse: Final = dict(*args, **kwargs)
        self._hash = None

    #####################################################################################################

    def __str__(self) -> str:
        return str(self._warehouse)

    #####################################################################################################

    def __getitem__(self, key: Any) -> Any:
        return self._warehouse[key]

    #####################################################################################################

    def __iter__(self) -> Iterator[Any]:
        return iter(self._warehouse)

    #####################################################################################################

    def __len__(self) -> int:
        return len(self._warehouse)

    #####################################################################################################

    def __hash__(self) -> int:
        if self._hash is None:
            hash_ = 0
            for key, value in self._warehouse.items():  # noqa: WPS110
                hash_ ^= hash(key)
                hash_ ^= hash(value)
            self._hash = hash_  # type: ignore[assignment]
        return self._hash  # type: ignore[return-value]

    #####################################################################################################

    def __repr__(self) -> str:
        return repr(self._warehouse)

#####################################################################################################
