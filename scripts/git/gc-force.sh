#!/usr/bin/env bash

LEVEL_DIR='..'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

printf '\n'
echo 'Cleanup git root'
git gc --aggressive

if [[ -f "${ROOT_DIR}/.gitmodules" ]]; then
    sed -r 's/^[\t\n\v ]*path[\t\n\v ]*=[\t\n\v ]*([^\t\n\v ]+)[\t\n\v ]*$/\1/g;t;d' "${ROOT_DIR}/.gitmodules" | \
    xargs --no-run-if-empty -I % sh -c \
    "printf '\n'; echo 'Cleanup git % submodule'; cd '${ROOT_DIR}/%'; git reflog expire --verbose --expire=all --expire-unreachable=all --stale-fix --rewrite --updateref --all; git -c gc.reflogExpire=0 -c gc.reflogExpireUnreachable=0 -c gc.rerereresolved=0 -c gc.rerereunresolved=0 -c gc.pruneExpire=now gc --aggressive --prune=now;"  # cspell:disable-line
fi

###############################################################################
