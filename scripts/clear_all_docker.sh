#!/usr/bin/env bash

LEVEL_DIR='.'
# shellcheck source=.base.sh
source "$(dirname "${0}")/${LEVEL_DIR}/.base.sh"

###############################################################################

sudo DOCKER_BUILDKIT=1 docker system prune --force --all --volumes

mapfile -t DOCKER_CONTAINERS_IDS < <(sudo DOCKER_BUILDKIT=1 docker container ls --all --quiet || true)
if [[ "${DOCKER_CONTAINERS_IDS[0]:-}" != "" ]]; then
    sudo DOCKER_BUILDKIT=1 docker container rm -f "${DOCKER_CONTAINERS_IDS[@]}"
    sudo DOCKER_BUILDKIT=1 docker system prune --force --all --volumes
fi

###############################################################################
