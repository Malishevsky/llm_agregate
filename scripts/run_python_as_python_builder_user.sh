#!/usr/bin/env bash

###############################################################################

set -Eeuo pipefail  # cspell:disable-line

# For debug output uncomment:
# set -Eeuxo pipefail  # cspell:disable-line

###############################################################################

CUR_DIR="${PWD}"

###############################################################################

function exit_handler () {
    # For debug output uncomment:
    # env

    cd "${CUR_DIR}"
}

trap exit_handler ERR
trap exit_handler EXIT

###############################################################################

if grep -sq 'systemd' /proc/1/sched | head -n 1
then
    echo 'run_python_as_python_builder_user.sh must call only in docker build env'
    exit 1
fi

###############################################################################

cd /usr/src/app

export LANG=en_US.UTF-8
export LANGUAGE=en_US:en
export LC_ALL=en_US.UTF-8

export PYTHONPYCACHEPREFIX="/home/python_builder/.cache/compiled_python"

export PATH="/usr/lib/ccache:/home/python_builder/.local/bin:/usr/local/bin:${PATH}"

# export PYTHONOPTIMIZE=1 # TODO: сделать возможность отключения этого параметра для запуска тестов

###############################################################################

if [[ -f /usr/local/bin/python3.11 ]] || [[ -L /usr/local/bin/python3.11 ]]; then
    /usr/local/bin/python3.11 "$@"
else
    /usr/bin/python3.11 "$@"
fi

###############################################################################
