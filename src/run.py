#!/usr/bin/env -S poetry run python

#####################################################################################################

# pylint: disable=wrong-import-position
from sys import argv
from typing import Final

from l7x.logger import setup_logging

# pylint: enable=wrong-import-position

_LOGGER: Final = setup_logging()

#####################################################################################################

from l7x.main import run  # noqa: E402

#####################################################################################################

if __name__ == '__main__':
    run(_LOGGER, tuple(argv[1:]))

#####################################################################################################
