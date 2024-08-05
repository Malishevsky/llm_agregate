#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

bash "${SCRIPTS_DIR}/install/dotenv-linter.sh"

find "${ROOT_DIR}" \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/.mypy_cache/*' \
    -not -path '*/.pytest_cache/*' \
    -not -path '*/.venv/*' \
    -type f -name '.env*' | while read -r f
do
    "${PYTHON_BIN_PATH}/dotenv-linter" --skip UnorderedKey "${f}"
done

###############################################################################
