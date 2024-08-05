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
    -not -path '*/.vscode/*' \
    -not -path '*/reports/*' \
    -type f \( -name '*.json' -o -name '*.yaml' \) | while read -r f
do
    "${NODE_BIN_DIR}/v8r" "${f}"
done

###############################################################################
