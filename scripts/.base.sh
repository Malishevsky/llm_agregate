#!/usr/bin/env bash

###############################################################################

set -Eeuo pipefail

# For debug output uncomment:
# set -Eeuxo pipefail

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

BASE_DIR="$(dirname "${0}")"
BASE_DIR="$(realpath "${BASE_DIR}")"

###############################################################################

SCRIPTS_DIR="$(realpath "${BASE_DIR}/${LEVEL_DIR:?}")"
if [[ ! -f "${SCRIPTS_DIR}/.base.sh" ]]; then
    echo "ERROR: Invalid script dir: '${SCRIPTS_DIR}'"
    exit 1
fi

###############################################################################

ROOT_DIR="$(realpath "${SCRIPTS_DIR}/..")"
cd "${ROOT_DIR}"
if [[ (! -f './pyproject.toml' ) || (! -f './poetry.lock' ) ]]; then
    echo "ERROR: Invalid root dir: '${ROOT_DIR}'"
    exit 1
fi

###############################################################################

REPORTS_DIR="$(realpath "${ROOT_DIR}/reports")"
[[ -d "${REPORTS_DIR}" ]] || mkdir -p "${REPORTS_DIR}"

###############################################################################

if [[ "${2:-}" != 'SKIP_NODEJS_ENV_CHECK' ]]; then
    # shellcheck disable=SC2034  # Unused variables left for readability
    NODE_BIN_DIR="$(realpath "${ROOT_DIR}/node_modules/.bin")"
fi

###############################################################################

PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
RUN_PYTHON="${RUN_PYTHON:-/usr/bin/python${PYTHON_VERSION}}"

###############################################################################

if [[ "${1:-}" != "SKIP_PYTHON_ENV_CHECK" ]]; then
    PYENV_PATH="$(PYTHONOPTIMIZE=1 "${RUN_PYTHON}" -m poetry env info --path)"

    # shellcheck disable=SC2034  # Unused variables left for readability
    SITE_PACKAGES_PATH="${PYENV_PATH}/lib/python${PYTHON_VERSION}/site-packages"

    # shellcheck disable=SC2034  # Unused variables left for readability
    PYTHON_BIN_PATH="${PYENV_PATH}/bin"
fi

###############################################################################
