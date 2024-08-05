#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

printf '\n'
echo 'Fsck git root'
git fsck --full --strict --unreachable --dangling --name-objects --root --tags

if [[ -f "${ROOT_DIR}/.gitmodules" ]]; then
    sed -r 's/^[\t\n\v ]*path[\t\n\v ]*=[\t\n\v ]*([^\t\n\v ]+)[\t\n\v ]*$/\1/g;t;d' "${ROOT_DIR}/.gitmodules" | \
    xargs --no-run-if-empty -I % sh -c \
    "printf '\n'; echo 'Fsck git % submodule'; cd '${ROOT_DIR}/%'; git fsck --full --strict --unreachable --dangling --name-objects --root --tags;"
fi

###############################################################################
