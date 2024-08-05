#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

"${NODE_BIN_DIR}/editorconfig-checker" --exclude 'node_modules|.git|.mypy_cache|.pytest_cache|.venv|models|.vscode|.benchmarks|reports'

###############################################################################
