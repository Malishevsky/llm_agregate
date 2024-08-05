#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

bash "${SCRIPTS_DIR}/install/dotenv-linter.sh"
bash "${SCRIPTS_DIR}/install/shellcheck.sh"

###############################################################################
