# syntax=docker/dockerfile:1.9.0-labs@sha256:64585ac36e6af50f0078728783f6a874c6f5f63bd31ec94195ca44b69ed1e7f8

ARG UBUNTU_VERSION='22.04'

#######################################################################################

# view packages version: https://packages.ubuntu.com/search?suite=all&searchon=names&keywords=...

########################################################################################

ARG IMAGE_BUILDER_DIGEST='sha256:340d9b015b194dc6e2a13938944e0d016e57b9679963fdeb9ce021daac430221'
ARG IMAGE_BUILDER="ubuntu:${UBUNTU_VERSION}@${IMAGE_BUILDER_DIGEST}"

########################################################################################

ARG IMAGE_RUNNER="ubuntu:${UBUNTU_VERSION}@${IMAGE_BUILDER_DIGEST}"

########################################################################################

# use --build-arg L7X_BUILD_DEVELOPMENT=1 for debug build
ARG L7X_BUILD_DEVELOPMENT

ARG L7X_OPTIMIZATION_LEVEL='3'
ARG L7X_BUILD_MARCH='x86-64-v2'

ARG L7X_PYTHON_BUILDER_USER='python_builder'
ARG L7X_PYTHON_BUILDER_USER_ID='10000'

########################################################################################

FROM ${IMAGE_BUILDER} as builder

ARG L7X_BUILD_DEVELOPMENT
ARG L7X_OPTIMIZATION_LEVEL
ARG L7X_BUILD_MARCH
ARG L7X_PYTHON_BUILDER_USER
ARG L7X_PYTHON_BUILDER_USER_ID

SHELL ["/bin/bash", "-e", "-u", "-o", "pipefail", "-c"]

USER root:root

ADD --link 'https://github.com/ufoscout/docker-compose-wait/releases/download/2.12.1/wait' '/usr/local/bin/wait'
ADD --link 'https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64' '/usr/local/bin/dumb-init'

RUN echo '2241be671073520e028b2f12df1e9ef0419014cffb5670b7a80b2080804be17d */usr/local/bin/wait' > '/usr/local/bin/sha256'; \
    echo 'e874b55f3279ca41415d290c512a7ba9d08f98041b28ae7c2acb19a545f1c4df */usr/local/bin/dumb-init' >> '/usr/local/bin/sha256'; \
    sha256sum -cw --strict < '/usr/local/bin/sha256'; \
    rm -rf '/usr/local/bin/sha256';

RUN chmod +x '/usr/local/bin/wait'; \
    chmod +x '/usr/local/bin/dumb-init'; \
    /usr/local/bin/dumb-init --version; \
    /usr/local/bin/wait --version;

ENV PYTHONOPTIMIZE='1' \
    WORK_DIR='/usr/src/app' \
    PYTHON_BUILDER_USER="${L7X_PYTHON_BUILDER_USER}" \
    PYTHON_BUILDER_USER_ID="${L7X_PYTHON_BUILDER_USER_ID}" \
    BUILD_MARCH="${L7X_BUILD_MARCH}" \
    CXX_STANDARD='17' \
    OPTIMIZATION_LEVEL="${L7X_OPTIMIZATION_LEVEL}"

ENV CFLAGS="${CFLAGS:-} -fPIC -O${OPTIMIZATION_LEVEL} -msse4.1 -DNDEBUG -pipe -flto=auto -std=c${CXX_STANDARD} -march=${BUILD_MARCH}" \
    CXXFLAGS="${CXXFLAGS:-} -fPIC -O${OPTIMIZATION_LEVEL} -msse4.1 -DNDEBUG -pipe -flto=auto -std=c++${CXX_STANDARD} -march=${BUILD_MARCH}" \
    LDFLAGS="${LDFLAGS:-} -fPIC -O${OPTIMIZATION_LEVEL} -msse4.1 -DNDEBUG -pipe -flto=auto -march=${BUILD_MARCH}"

WORKDIR "${WORK_DIR}"

ENV RUN_PYTHON="su - ${PYTHON_BUILDER_USER} -s ${WORK_DIR}/run_python_as_python_builder_user.sh -- "

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    sed -i -e 's/http:\/\/archive/mirror:\/\/mirrors/' -e 's/http:\/\/security/mirror:\/\/mirrors/' -e 's/\/ubuntu\//\/mirrors.txt/' /etc/apt/sources.list; \
    apt-get -q update; \
    NEED_CHECK_PACKAGES='locales'; \
    echo '='; echo 'Actual version for package:'; for PACKAGE in ${NEED_CHECK_PACKAGES}; do PACKAGE_VERSION="$(apt-cache show "${PACKAGE}" | grep -oP '(?<=Version: ).*' | head -n 1)"; echo "'${PACKAGE}=${PACKAGE_VERSION}' \\"; done; echo '='; \
    DEBIAN_FRONTEND='noninteractive' apt-get -q install -y -o Dpkg::Options::='--force-confnew' --no-install-recommends \
        'locales=2.35-0ubuntu3.8' \
        ; \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen; \
    locale-gen;

ENV LANG='en_US.UTF-8' \
    LANGUAGE='en_US:en' \
    LC_ALL='en_US.UTF-8'

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    NEED_CHECK_PACKAGES='ca-certificates software-properties-common gpg-agent binutils build-essential patchelf wget git zlib1g-dev ccache gcc-12 g++-12 libsndfile1'; \
    echo '='; echo 'Actual version for package:'; for PACKAGE in ${NEED_CHECK_PACKAGES}; do PACKAGE_VERSION="$(apt-cache show "${PACKAGE}" | grep -oP '(?<=Version: ).*' | head -n 1)"; echo "'${PACKAGE}=${PACKAGE_VERSION}' \\"; done; echo '='; \
    DEBIAN_FRONTEND='noninteractive' apt-get -q install -y -o Dpkg::Options::='--force-confnew' --no-install-recommends \
        'ca-certificates=20230311ubuntu0.22.04.1' \
        'software-properties-common=0.99.22.9' \
        'gpg-agent=2.2.27-3ubuntu2.1' \
        'binutils=2.38-4ubuntu2.6' \
        'build-essential=12.9ubuntu3' \
        'patchelf=0.14.3-1' \
        'wget=1.21.2-2ubuntu1' \
        'git=1:2.34.1-1ubuntu1.11' \
        'zlib1g-dev=1:1.2.11.dfsg-2ubuntu9.2' \
        'ccache=4.5.1-1' \
        'gcc-12=12.3.0-1ubuntu1~22.04' \
        'g++-12=12.3.0-1ubuntu1~22.04' \
        'libsndfile1=1.0.31-2ubuntu0.1' \
        ; \
    update-alternatives --remove-all cpp; \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 120 --slave /usr/bin/g++ g++ /usr/bin/g++-12 --slave /usr/bin/gcov gcov /usr/bin/gcov-12 --slave /usr/bin/gcc-ar gcc-ar /usr/bin/gcc-ar-12 --slave /usr/bin/gcc-ranlib gcc-ranlib /usr/bin/gcc-ranlib-12 --slave /usr/bin/cpp cpp /usr/bin/cpp-12; \
    ldconfig; \
    ccache -s; \
    git --version; \
    wget --version; \
    gcc -v; \
    g++ -v; \
    gcov -v; \
    ld.gold -v; \
    ld.bfd -v; \
    gcc-ar --version; \
    gcc-ranlib -v; \
    cpp --version;

COPY --link --chown=root:root ./scripts/run_python_as_python_builder_user.sh ./

COPY --link --chown=root:root ./scripts/prepare_build_env.sh ./scripts/
COPY --link --chown=root:root ./poetry.lock ./pyproject.toml ./
COPY --link --chown=root:root ./static/ ./static/
COPY --link --chown=root:root ./alembic.ini ./

RUN find "${WORK_DIR}" \( -type f -exec chmod a=r {} \; \) -o \( -type d -exec chmod a=rx {} \; \); \
    chmod a=rx "${WORK_DIR}/scripts/prepare_build_env.sh"; \
    chmod a=rx "${WORK_DIR}/run_python_as_python_builder_user.sh"; \
    chmod u=rwx "${WORK_DIR}"; \
    ls -la "${WORK_DIR}";

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=cache,target=/home/${PYTHON_BUILDER_USER}/.cache/pip,uid=${PYTHON_BUILDER_USER_ID},gid=${PYTHON_BUILDER_USER_ID} \
    --mount=type=cache,target=/home/${PYTHON_BUILDER_USER}/.cache/compiled_python,uid=${PYTHON_BUILDER_USER_ID},gid=${PYTHON_BUILDER_USER_ID} \
    "${WORK_DIR}/scripts/prepare_build_env.sh"; \
    rm "${WORK_DIR}/scripts/prepare_build_env.sh";

COPY --link --chown=root:root '.yarnrc' 'package.json' 'yarn.lock' 'cspell.json' './'
COPY --link --chown=root:root ./.git/ ./.git/
COPY --link --chown=root:root ./scripts/ ./scripts/
COPY --link --chown=root:root ./patches/ ./patches/

RUN find "${WORK_DIR}" \( -type f -exec chmod a=r {} \; \) -o \( -type d -exec chmod a=rxw {} \; \); ls -la "${WORK_DIR}";

RUN chmod a=rx "${WORK_DIR}/run_python_as_python_builder_user.sh"; \
    chmod a=rx "./scripts/create_build_info.py"; \
    chown -R "${PYTHON_BUILDER_USER}:${PYTHON_BUILDER_USER}" "${WORK_DIR}/.git/"; \
    ${RUN_PYTHON} -m poetry config installer.max-workers 10;

RUN --mount=type=cache,target=/home/${PYTHON_BUILDER_USER}/.cache/compiled_python,uid=${PYTHON_BUILDER_USER_ID},gid=${PYTHON_BUILDER_USER_ID} \
    --mount=type=cache,target=/home/${PYTHON_BUILDER_USER}/.cache/pypoetry/artifacts,uid=10000,gid=10000 \
    --mount=type=cache,target=/home/${PYTHON_BUILDER_USER}/.cache/pypoetry/cache,uid=10000,gid=10000 \
    ${RUN_PYTHON} -m poetry env remove --all; \
    ${RUN_PYTHON} -m poetry install --sync --no-root --no-interaction; \
    ${RUN_PYTHON} -m poetry run bash -c "python3 ./scripts/patch.py";

RUN ls -la /usr/src/app;

RUN mkdir -p "${WORK_DIR}/reports/"; \
    find "${WORK_DIR}" \( -type f -exec chmod a=r {} \; \) -o \( -type d -exec chmod a=rx {} \; \); \
    chmod a=rx "${WORK_DIR}/run_python_as_python_builder_user.sh"; \
    ls -la "${WORK_DIR}";

COPY --link --chown=root:root ./src/ ./src/
COPY --link --chown=root:root scripts/build.sh ./

RUN --mount=type=cache,target=/home/${PYTHON_BUILDER_USER}/.cache/compiled_python,uid=${PYTHON_BUILDER_USER_ID},gid=${PYTHON_BUILDER_USER_ID} \
    ${RUN_PYTHON} -m poetry run bash -c "python3 ./scripts/create_build_info.py" >> "${WORK_DIR}/src/l7x/build_info.py";

RUN chmod a=rxw .; \
    ${RUN_PYTHON} -m poetry run bash "${WORK_DIR}/build.sh";

RUN ${RUN_PYTHON} -m poetry run bash -c "python3 /usr/src/app/src/_download_metric_models.py";

########################################################################################

FROM ${IMAGE_RUNNER}

SHELL ["/bin/bash", "-e", "-u", "-o", "pipefail", "-c"]

USER root:root

ARG L7X_BUILD_DEVELOPMENT

ENV PYTHONDEVMODE="${L7X_BUILD_DEVELOPMENT:+'1'}"
ENV PYTHONDEVMODE="${PYTHONDEVMODE:-''}"

ENV PYTHONNODEBUGRANGES="${L7X_BUILD_DEVELOPMENT:+''}"
ENV PYTHONNODEBUGRANGES="${PYTHONNODEBUGRANGES:-'1'}"

ENV LANG='en_US.UTF-8' \
    LANGUAGE='en_US:en' \
    LC_ALL='en_US.UTF-8' \
    RUN_USER='40300' \
    PYTHONTRACEMALLOC="${PYTHONDEVMODE}" \
    PYTHONUNBUFFERED="${PYTHONDEVMODE}"

ENV RUN_GROUP="${L7X_BUILD_DEVELOPMENT:+'0'}"
ENV RUN_GROUP="${RUN_GROUP:-"${RUN_USER}"}"

ENV WORK_DIR='/usr/src/app' \
    BIN_DIR='/usr/local/bin' \
    ELASTIC_APM_ENVIRONMENT='production'

WORKDIR "${WORK_DIR}"

COPY --link --chown=root:root --from=builder '/usr/local/bin/wait' '/usr/local/bin/dumb-init' "${BIN_DIR}/"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    echo "L7X_BUILD_DEVELOPMENT: ${L7X_BUILD_DEVELOPMENT:-}"; \
    echo "PYTHONDEVMODE: ${PYTHONDEVMODE}"; \
    echo "PYTHONNODEBUGRANGES: ${PYTHONNODEBUGRANGES}"; \
    "${BIN_DIR}/wait" --version; \
    "${BIN_DIR}/dumb-init" --version; \
    apt-get -q update; \
    PACKAGES_FOR_DEBUG=''; \
    if [ "${PYTHONDEVMODE}" = '1' ]; then PACKAGES_FOR_DEBUG='net-tools mc iputils-ping curl wget htop nano'; fi; \
    NEED_CHECK_PACKAGES='locales libsndfile1 ca-certificates'; \
    echo '='; echo 'Actual version for package:'; for PACKAGE in ${NEED_CHECK_PACKAGES}; do PACKAGE_VERSION="$(apt-cache show "${PACKAGE}" | grep -oP '(?<=Version: ).*' | head -n 1)"; echo "'${PACKAGE}=${PACKAGE_VERSION}' \\"; done; echo '='; \
    DEBIAN_FRONTEND='noninteractive' apt-get -q install -y -o Dpkg::Options::='--force-confnew' --no-install-recommends \
        ${PACKAGES_FOR_DEBUG} \
        'locales=2.35-0ubuntu3.8' \
        'libsndfile1=1.0.31-2ubuntu0.1' \
        'ca-certificates=20230311ubuntu0.22.04.1' \
    ; \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen; \
    locale-gen; \
    ldconfig; \
    ldd --version; \
    if [ "${PYTHONDEVMODE}" = '1' ]; then useradd -m -s /bin/bash -u "${RUN_USER}" -g "${RUN_GROUP}" runner; else groupadd -g "${RUN_GROUP}" -r runner; useradd -l -r -M -s /bin/false -u "${RUN_USER}" -g "${RUN_GROUP}" runner; fi; \
    rm -rf /var/lib/log/*

RUN apt-get -q clean autoclean; \
    apt-get -q autoremove --yes; \
    apt-get -q purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    rm -rf /var/lib/apt/lists/*; \
    rm -rf /var/lib/apt/*; \
    rm -rf /var/lib/dpkg/*; \
    rm -rf /var/lib/cache/*; \
    rm -rf /var/lib/log/*;

COPY --link --chown=root:root --from=builder '/usr/src/app/dist/run' "${WORK_DIR}/"
COPY --link --chown=root:root --from=builder '/usr/src/app/static/' "${WORK_DIR}/static"
COPY --link --chown=40300:40300 --from=builder '/usr/src/app/metric_models_dir/' "${WORK_DIR}/metric_models_dir"

USER runner:runner

ENV WAIT_COMMAND='/usr/src/app/run'

ENV USE_PRIVATE_SERVER=true \
    PYTHONOPTIMIZE='2'

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]

# если использовать CMD с [] то не будет работать setproctitle
CMD '/usr/local/bin/wait'

########################################################################################
