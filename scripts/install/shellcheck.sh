#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

APP_VER='v0.9.0'

APP_PATH="${PYTHON_BIN_PATH}/shellcheck"

APP_SIZE=$(if [[ -f "${APP_PATH}" ]]; then stat -c%s "${APP_PATH}"; else echo '0'; fi)

if [[ "${APP_SIZE}" -lt 100 ]]; then
    wget -q --quiet -c "https://github.com/koalaman/shellcheck/releases/download/${APP_VER}/shellcheck-${APP_VER}.linux.x86_64.tar.xz" -O - | \
        tar -Jxv -C "${PYTHON_BIN_PATH}/"

    DOWNLOAD_DIR="${PYTHON_BIN_PATH}/shellcheck-${APP_VER}"
    mv "${DOWNLOAD_DIR}/shellcheck" "${APP_PATH}"
    rm -rf "${DOWNLOAD_DIR}"

    "${APP_PATH}" --version
fi

###############################################################################
