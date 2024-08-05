#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

find "${ROOT_DIR}" \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/.mypy_cache/*' \
    -not -path '*/.pytest_cache/*' \
    -not -path '*/.venv/*' \
    -type f -name 'Dockerfile*' | while read -r f
do
    if ! grep -Pq '^[ \n\r\v\t]*INCLUDE\+[ \n\r\v\t]+' "${f}" ; then
        "${NODE_BIN_DIR}/dockerfilelint" "${f}"
    fi
done

###############################################################################
