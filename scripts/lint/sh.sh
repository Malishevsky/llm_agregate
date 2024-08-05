#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "RUN CHECKER: ${0}"

###############################################################################

bash "${SCRIPTS_DIR}/install/shellcheck.sh"

find "${ROOT_DIR}" \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/.mypy_cache/*' \
    -not -path '*/.pytest_cache/*' \
    -not -path '*/.venv/*' \
    -not -path '*/.tmp-projections/*' \
    -type f \( -name '*.sh' -o -name '*.bash' -o -name '*.zsh' -o -name '*.ksh' \) | while read -r f
do
    "${PYTHON_BIN_PATH}/shellcheck" -x -a -P "${SCRIPTS_DIR}" --check-sourced --enable=all --severity=style --color=auto "${f}"
done

###############################################################################
