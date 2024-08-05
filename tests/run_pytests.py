#!/usr/bin/env -S poetry run python

#####################################################################################################

from os import environ
from pathlib import Path
from re import sub
from sys import argv, path

import pytest

#####################################################################################################

if __name__ == '__main__':
    environ['TESTMON_DATAFILE'] = './.cache/.testmondata'  # cspell:disable-line
    path.append(str(Path(__file__).parent))

    path.append('.')
    path.append('./src')

    argv[0] = sub(r'(-script\.pyw|\.exe)?$', '', argv[0])
    argv.append('--html-report=./reports/test-report.html')
    argv.append('--benchmark-storage=file://./.cache/.benchmarks')
    exit(pytest.console_main())  # pylint: disable=consider-using-sys-exit

#####################################################################################################
