#####################################################################################################

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

#####################################################################################################

@contextmanager
def with_cleanup(cleanup_func: Callable[[], Any]) -> Iterator[None]:
    try:
        yield
    finally:
        cleanup_func()

#####################################################################################################
