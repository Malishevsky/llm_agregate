#####################################################################################################

from dataclasses import dataclass
from logging import DEBUG, Logger, getLogger
from types import MappingProxyType
from typing import Final

from elasticapm import Client as _ApmClient, get_client as _get_apm_client, set_transaction_outcome, set_transaction_result
from elasticapm.conf.constants import OUTCOME
from elasticapm.handlers.logging import LoggingFilter
from elasticapm.traces import BaseSpan, Transaction

from l7x.configs.apm_context import get_apm_context
from l7x.configs.settings import AppSettings
from l7x.utils.elasticsearch_logger import ElasticAuthType, ElasticHandler, ElasticHost

#####################################################################################################

def _is_enable_apm(app_settings: AppSettings, /) -> bool:
    return app_settings.is_elastic_apm_server_enabled is True

#####################################################################################################

def _is_elastic_log(app_settings: AppSettings, /) -> bool:
    return app_settings.is_send_to_elastic_log_server is True

#####################################################################################################

def init_elastic_log(app_settings: AppSettings, /) -> None:
    if _is_enable_apm(app_settings) and _is_elastic_log(app_settings):
        root_logger: Final = getLogger()
        handler_index = -1
        for index, log_handler in enumerate(root_logger.handlers):
            if isinstance(log_handler, ElasticHandler):
                handler_index = index
                break

        host: Final = app_settings.elastic_log_server_host
        port: Final = app_settings.elastic_log_server_port
        elastic_log_handler: Final = ElasticHandler(
            hosts=(ElasticHost(host=app_settings.elastic_log_server_host, port=port),),
            auth_type=ElasticAuthType.BASIC_AUTH,
            auth_details=(app_settings.elastic_log_server_user, app_settings.elastic_log_server_pass),
            es_index_name='logs-generic-default',
            es_doc_type='log',
            default_timestamp_field_name='@timestamp',
            verify_ssl=False,
            es_additional_fields=MappingProxyType({
                'labels': get_apm_context()._asdict(),  # noqa: WPS437
            }),
        )
        if not elastic_log_handler.test_es_source():
            root_logger.warning(f'Invalid connect to: {host}:{port}')

        elastic_log_handler.addFilter(LoggingFilter())  # type: ignore[no-untyped-call]

        if handler_index >= 0:
            root_logger.handlers[handler_index] = elastic_log_handler
        else:
            root_logger.addHandler(elastic_log_handler)

#####################################################################################################

def init_apm_client(logger: Logger, app_settings: AppSettings, /) -> _ApmClient | None:
    if not _is_enable_apm(app_settings):
        return None
    apm_logger: Final = getLogger('elasticapm')
    apm_logger.setLevel(DEBUG)
    apm_client: _ApmClient | None = _get_apm_client()
    if apm_client is None:
        # apm_instrument()
        apm_client = _ApmClient(service_name=app_settings.service_name)
        apm_client_config: Final = apm_client.config._config  # noqa: WPS437 # pylint: disable=protected-access
        apm_client_config.global_labels = get_apm_context()._asdict()  # noqa: WPS437
        apm_client_config.service_version = app_settings.service_version
        metadata: Final = apm_client.build_metadata()  # type: ignore[no-untyped-call]
        logger.info(f'Apm client connect to: {app_settings.elastic_apm_server_url}, metadata: {metadata}')
    return apm_client

#####################################################################################################

def finish_apm_transaction_failure(apm_client: _ApmClient | None, /, *, is_capture_exception: bool = False) -> None:
    if apm_client is not None:
        if is_capture_exception:
            apm_client.capture_exception()  # type: ignore[no-untyped-call]
        transaction_result: Final[str] = OUTCOME.FAILURE  # type: ignore[attr-defined]
        set_transaction_result(transaction_result)
        set_transaction_outcome(transaction_result)
        apm_client.end_transaction()  # type: ignore[no-untyped-call]

######################################################################################

def finish_apm_transaction_success(apm_client: _ApmClient | None, /) -> None:
    if apm_client is not None:
        transaction_result: Final[str] = OUTCOME.SUCCESS  # type: ignore[attr-defined]
        set_transaction_result(transaction_result)
        set_transaction_outcome(transaction_result)
        apm_client.end_transaction()  # type: ignore[no-untyped-call]

#####################################################################################################

def finish_apm_span_success(span: BaseSpan | None, /) -> None:
    if span is not None:
        span.outcome = OUTCOME.SUCCESS  # type: ignore[attr-defined]
        span.end()

#####################################################################################################

@dataclass(frozen=True)
class TransactionAndSpan:
    transaction: Transaction
    span: BaseSpan

#####################################################################################################

TransactionAndSpans = dict[str, TransactionAndSpan]

#####################################################################################################

def finish_apm_spans_success(transaction_and_spans: TransactionAndSpans, /) -> None:
    for transaction_and_span in transaction_and_spans.values():
        finish_apm_span_success(transaction_and_span.span)

#####################################################################################################

def set_apm_spans_labels(transaction_and_spans: TransactionAndSpans, /, **labels: str | int | bool) -> None:
    for transaction_and_span in transaction_and_spans.values():
        transaction_and_span.span.label(**labels)

#####################################################################################################
