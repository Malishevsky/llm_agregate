#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

"${NODE_BIN_DIR}/jscpd" --output "${REPORTS_DIR}/jscpd" --config "${ROOT_DIR}/.jscpd.json" --pattern '**/*.py' "${ROOT_DIR}"

###############################################################################
