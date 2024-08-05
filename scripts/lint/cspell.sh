#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

"${NODE_BIN_DIR}/cspell" lint \
    --config "${ROOT_DIR}/cspell.json" \
    --show-suggestions \
    --unique \
    --relative \
    --show-context \
    --locale 'en,ru' \
    "**/*.{py,md,json,yaml,txt,js,ts,sh}"

###############################################################################
