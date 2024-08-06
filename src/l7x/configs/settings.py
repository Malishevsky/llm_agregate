#####################################################################################################

from collections.abc import Mapping
from multiprocessing import cpu_count
from os import getenv
from pathlib import Path
from sys import flags
from typing import Any, Final, Protocol, TypeVar
from urllib.parse import urlparse

from environs import Env
from orjson import loads as orjson_loads
from pydantic.dataclasses import dataclass

from l7x.utils.config_utils import get_app_build_info
# from l7x.utils.crypt_utils import calc_secrets
from l7x.utils.orjson_utils import orjson_dumps_to_str_pretty

#####################################################################################################

def load_env() -> Env:
    env: Final = Env()

    env_file: Final = './.env'
    if Path(env_file).exists():
        env.read_env(env_file, override=True)

    return env

#####################################################################################################

def _resolve_path(path: str) -> Path | None:
    return Path(path).resolve() if path != '' else None

#####################################################################################################

_AppSettingsExt = TypeVar('_AppSettingsExt', bound='AppSettings')

@dataclass(frozen=True, kw_only=True)
class AppSettings:  # pylint: disable=too-many-instance-attributes
    #####################################################################################################

    service_name: str
    service_version: str
    service_branch: str
    service_commit_hash: str
    service_build_timestamp: str

    is_dev_mode: bool

    port: int
    worker_count: int
    server_url: str

    # TODO: вынести логику с apm в паблик-бот
    is_elastic_apm_server_enabled: bool
    elastic_apm_server_url: str

    is_send_to_elastic_log_server: bool
    elastic_log_server_host: str
    elastic_log_server_port: int
    elastic_log_server_user: str
    elastic_log_server_pass: str

    localtunnel_user: str
    localtunnel_pass: str

    translate_api_url: str
    translate_api_langs_cache_expire_sec: int

    recognizer_api_url: str
    recognizer_api_langs_cache_expire_sec: int

    max_upload_file_size_in_byte: int

    storage_secret: str

    certificate_path: Path | None
    private_key_path: Path | None

    dark_mode: bool

    prompts_per_language: dict[str, str | list[str]]

    llm_model_id: str
    models_cache_dir: Path | None

    #####################################################################################################

    def __str__(self, /) -> str:
        obj_for_output: Final = self._get_fields_for_output()
        return orjson_dumps_to_str_pretty(obj_for_output)

    #####################################################################################################

    def _get_fields_for_output(self) -> Mapping[str, Any]:
        obj_for_output = {
            'SERVICE_NAME': self.service_name,
            'SERVICE_VERSION': self.service_version,

            'SERVER_PORT': self.port,
            'WORKER_COUNT': self.worker_count,
            'SERVER_EXTERNAL_URL': self.server_url,

            'TRANSLATE_API_URL': self.translate_api_url,
            'TRANSLATE_API_LANGS_CACHE_EXPIRE_SEC': self.translate_api_langs_cache_expire_sec,

            'MAX_UPLOAD_FILE_SIZE_IN_BYTE': self.max_upload_file_size_in_byte,
        }

        if self.is_dev_mode:
            obj_for_output.update({
                '_IS_DEV_MODE_': self.is_dev_mode,

                'SERVICE_BRANCH': self.service_branch,
                'SERVICE_COMMIT_HASH': self.service_commit_hash,
                'SERVICE_BUILD_TIMESTAMP': self.service_build_timestamp,

                'ELASTIC_APM_SERVER_ENABLED': self.is_elastic_apm_server_enabled,
                'ELASTIC_APM_SERVER_URL': self.elastic_apm_server_url,

                'IS_SEND_TO_ELASTIC_LOG_SERVER': self.is_send_to_elastic_log_server,
                'ELASTIC_LOG_SERVER_HOST': self.elastic_log_server_host,
                'ELASTIC_LOG_SERVER_PORT': self.elastic_log_server_port,
                'ELASTIC_LOG_SERVER_USER': self.elastic_log_server_user,
                'ELASTIC_LOG_SERVER_PASS': self.elastic_log_server_pass,

                'LOCALTUNNEL_USER': self.localtunnel_user,
                'LOCALTUNNEL_PASS': self.localtunnel_pass,
            })
        return obj_for_output

    #####################################################################################################

    def cast(self, app_settings_class: type[_AppSettingsExt]) -> _AppSettingsExt:
        if not isinstance(self, app_settings_class):
            raise TypeError(f'Settings cant cast to "{app_settings_class}"')
        return self

#####################################################################################################

class _AppSettingsProtocol(Protocol):
    def __call__(self, include_db_admin_credentials: bool = False) -> AppSettings:
        raise NotImplementedError()

#####################################################################################################

def _create_app_settings() -> _AppSettingsProtocol:
    dev_translate_api_url = None

    def _app_settings(include_db_admin_credentials: bool = False) -> AppSettings:
        env: Final = load_env()

        translate_api_url = urlparse(getenv('L7X_TRANSLATE_API_URL', '')).geturl()
        recognizer_api_url = urlparse(getenv('L7X_RECOGNIZER_API_URL', '')).geturl()

        nonlocal dev_translate_api_url  # noqa: WPS420
        if dev_translate_api_url is None:
            dev_translate_api_url = translate_api_url  # noqa: WPS442

        run_translation_server: Final = env.bool('L7X_RUN_TRANSLATION_SERVER', False)  # noqa: WPS425
        is_dev_mode: Final = flags.dev_mode is True

        if is_dev_mode and run_translation_server:
            translate_api_url = dev_translate_api_url
        else:
            translate_api_url = urlparse(env.str('L7X_TRANSLATE_API_URL', '')).geturl()

        prompts_per_language: Final = orjson_loads(env.str('L7X_DEFAULT_PARAMS_PER_LANGUAGE', '{}'))

        app_build_info: Final = get_app_build_info()

        hf_token = env.str('L7X_HF_TOKEN')
        if hf_token is not None:
            from huggingface_hub import login
            login(hf_token)

        return AppSettings(
            service_name=env.str('L7X_SERVICE_NAME', app_build_info.app_name).strip(),
            service_version=app_build_info.app_version,
            service_branch=app_build_info.app_branch,
            service_commit_hash=app_build_info.app_commit_hash,
            service_build_timestamp=app_build_info.app_build_timestamp,

            is_dev_mode=is_dev_mode,

            port=env.int('L7X_SERVER_PORT', 8080),  # noqa: WPS432
            worker_count=env.int('L7X_WORKER_COUNT', (cpu_count() * 2) + 1),
            server_url=urlparse(env.str('L7X_SERVER_EXTERNAL_URL')).geturl(),

            is_elastic_apm_server_enabled=env.bool('L7X_ELASTIC_APM_SERVER_ENABLED', False),  # noqa: WPS425
            elastic_apm_server_url=urlparse(env.str('L7X_ELASTIC_APM_SERVER_URL', '')).geturl(),

            is_send_to_elastic_log_server=env.bool('L7X_IS_SEND_TO_ELASTIC_LOG_SERVER', False),  # noqa: WPS425
            elastic_log_server_host=urlparse(env.str('L7X_ELASTIC_LOG_SERVER_HOST', '')).geturl(),
            elastic_log_server_port=env.int('L7X_ELASTIC_LOG_SERVER_PORT', 9200),  # noqa: WPS432
            elastic_log_server_user=env.str('L7X_ELASTIC_LOG_SERVER_USER', 'elastic').strip(),
            elastic_log_server_pass=env.str('L7X_ELASTIC_LOG_SERVER_PASS', 'changeme').strip(),

            localtunnel_user=env.str('L7X_LOCALTUNNEL_USER', '').strip(),
            localtunnel_pass=env.str('L7X_LOCALTUNNEL_PASS', '').strip(),

            translate_api_url=translate_api_url,
            translate_api_langs_cache_expire_sec=env.int('L7X_TRANSLATE_API_LANGS_CACHE_EXPIRE_SEC', 60 * 60),

            recognizer_api_url=recognizer_api_url,
            recognizer_api_langs_cache_expire_sec=env.int('L7X_RECOGNIZER_API_LANGS_CACHE_EXPIRE_SEC', 60 * 60),

            max_upload_file_size_in_byte=env.int('L7X_MAX_UPLOAD_FILE_SIZE_IN_BYTE', 50 * 1024 * 1024),  # noqa: WPS432

            storage_secret=env.str('L7X_STORAGE_SECRET', ''),

            certificate_path=_resolve_path(env.str('L7X_SSL_CERTIFICATE_PATH', '')),
            private_key_path=_resolve_path(env.str('L7X_SSL_PRIVATE_KEY_PATH', '')),
            dark_mode=env.bool('L7X_DARK_MODE', False),

            prompts_per_language=prompts_per_language,

            llm_model_id=env.str('L7X_LLM_MODEL_ID', ''),
            models_cache_dir=_resolve_path(env.str('L7X_MODELS_CACHE_DIR', '')),
        )

    return _app_settings

#####################################################################################################

create_app_settings = _create_app_settings()

#####################################################################################################
