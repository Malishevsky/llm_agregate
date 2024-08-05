#!/usr/bin/env bash

###############################################################################

set -Eeuo pipefail  # cspell:disable-line

# For debug output uncomment:
# set -Eeuxo pipefail  # cspell:disable-line

###############################################################################

CUR_DIR="${PWD}"

###############################################################################

function exit_handler () {
    # For debug output uncomment:
    # env

    cd "${CUR_DIR}"
}

trap exit_handler ERR
trap exit_handler EXIT

###############################################################################

BASE_DIR="$(dirname "$0")"
BASE_DIR="$(realpath "${BASE_DIR}")"

###############################################################################

ROOT_DIR="$(realpath "${BASE_DIR}/..")"
cd "${ROOT_DIR}"

###############################################################################

find . -maxdepth 1 -type d -name '*.build' -exec rm -r -f {} +
find . -maxdepth 1 -type d -name 'build' -exec rm -r -f {} +

find . -maxdepth 1 -type d -name '*.dist' -exec rm -r -f {} +
find . -maxdepth 1 -type d -name 'dist' -exec rm -r -f {} +

find . -maxdepth 1 -type f -name '*.spec' -delete

###############################################################################

find . -maxdepth 1 -type d -name 'reports' -exec rm -r -f {} +

find . -maxdepth 1 -type d -name '.*_cache' -exec rm -r -f {} +

###############################################################################

find . -type f -name '*.py[co]' -delete -o -type d -name '__pycache__' -delete

###############################################################################
