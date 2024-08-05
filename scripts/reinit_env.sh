#!/usr/bin/env bash

LEVEL_DIR='.'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh" 'SKIP_PYTHON_ENV_CHECK' 'SKIP_NODEJS_ENV_CHECK'

###############################################################################

bash "${SCRIPTS_DIR}/clean.sh"

###############################################################################

export LANG=en_US.UTF-8
export LANGUAGE=en_US:en
export LC_ALL=en_US.UTF-8

###############################################################################

if [[ -d "${ROOT_DIR}/node_modules" ]]; then
    rm -rf "${ROOT_DIR}/node_modules"
fi

yarn install --frozen-lockfile --check-files --non-interactive --ignore-scripts --ignore-optional --prefer-offline

###############################################################################

# for python3.10:
#   python3.10 -m ensurepip --upgrade --user
# for python3.11:
#   read this https://peps.python.org/pep-0668/ and use standard operating system tools for installation pip.
${RUN_PYTHON} -m pip -V

${RUN_PYTHON} -m pip install --user --break-system-packages --upgrade pip poetry requests poethepoet keyring

${RUN_PYTHON} -m poetry config installer.max-workers 10

${RUN_PYTHON} -m poetry env remove --all

${RUN_PYTHON} -m poetry install --sync --no-root

"${SCRIPTS_DIR}/patch.py"

###############################################################################

echo ''
echo 'All have been done successfully.'
echo ''

###############################################################################
