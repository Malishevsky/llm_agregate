#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

echo "Looking diff-marker in git root: ${ROOT_DIR}"
git diff --check
#git fsck --full

if [[ -f "${ROOT_DIR}/.gitmodules" ]]; then
    sed -r 's/^[\t\n\v ]*path[\t\n\v ]*=[\t\n\v ]*([^\t\n\v ]+)[\t\n\v ]*$/\1/g;t;d' "${ROOT_DIR}/.gitmodules" | \
    xargs --no-run-if-empty -I % sh -c \
    "echo 'Looking diff-marker in git % submodule'; cd '${ROOT_DIR}/%'; git diff --check;"
fi

###############################################################################
