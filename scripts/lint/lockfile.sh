#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

"${NODE_BIN_DIR}/lockfile-lint" --type yarn --path "${ROOT_DIR}/yarn.lock" --validate-https --allowed-hosts yarn --validate-checksum --validate-integrity --validate-package-names --empty-hostname false

###############################################################################
