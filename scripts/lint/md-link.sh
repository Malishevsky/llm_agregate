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
    -type f -name '*.md' | while read -r f
do
    "${NODE_BIN_DIR}/markdown-link-check" --config "${ROOT_DIR}/markdown-link-check-config.json" "${f}"
done

###############################################################################
