#!/usr/bin/env bash

ENV_FOLDER="$(poetry run poetry env info -p)"
echo env folder "${ENV_FOLDER}"

poetry run pyinstaller ./src/run.py --name run \
    --collect-data nicegui \
    --hidden-import databases.backends \
    --hidden-import databases.backends.postgres \
    --hidden-import asyncpg.protocol.protocol \
    --hidden-import asyncpg.pgproto.pgproto \
    --hidden-import scipy._lib.array_api_compat.numpy.fft \
    --hidden-import scipy.special._special_ufuncs \
    --hidden-import orjson.orjson \
    --hidden-import transformers.models.gemma2.configuration_gemma2 \
    --hidden-import sacrebleu.tokenizers.tokenizer_13a \
    --collect-data fairseq2 \
    --collect-data sonar \
    --collect-data torch \
    --collect-data dateutil \
    --add-binary /usr/lib/python3.11/config-3.11-x86_64-linux-gnu/libpython3.11.so:lib \
    --add-binary "${ENV_FOLDER}/lib/libtbb.so.12:lib" \
    --add-data ./src/l7x/utils/audio_recorder.vue:l7x/utils/

ENV_DIST_PTL_FOLDER_PATH="${ENV_FOLDER}/lib/python3.11/site-packages/pytorch_lightning"
DIST_PTL_FOLDER_PATH="$(realpath './dist/run/_internal/pytorch_lightning')"

mkdir -p "${DIST_PTL_FOLDER_PATH}"

if [[ -f "${ENV_DIST_PTL_FOLDER_PATH}/version.info" ]]; then
    cp "${ENV_DIST_PTL_FOLDER_PATH}/version.info" "${DIST_PTL_FOLDER_PATH}"
else
    echo 'version.info not found!'
fi

if [[ -f "${ENV_DIST_PTL_FOLDER_PATH}/__version__.py" ]]; then
    cp "${ENV_DIST_PTL_FOLDER_PATH}/__version__.py" "${DIST_PTL_FOLDER_PATH}"
else
    echo '__version__.py not found!'
fi

ls -l "${DIST_PTL_FOLDER_PATH}"
