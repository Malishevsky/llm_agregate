#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

APP_VER='v3.3.0'

APP_PATH="${PYTHON_BIN_PATH}/dotenv-linter"

if [[ ! -f "${APP_PATH}" ]]; then
    wget -q --quiet -c "https://github.com/dotenv-linter/dotenv-linter/releases/download/${APP_VER}/dotenv-linter-linux-x86_64.tar.gz" -O - | \
        tar -xz -C "${PYTHON_BIN_PATH}/"

    "${APP_PATH}" --version
fi

###############################################################################
