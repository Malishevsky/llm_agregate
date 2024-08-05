#####################################################################################################

from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from logging import Handler, LogRecord
from socket import gethostbyname, gethostname
from threading import Lock, Timer
from types import MappingProxyType
from typing import Any, Final, Literal

from elastic_transport import NodeConfig
from elasticsearch import Elasticsearch, helpers as _elastic_search_helpers
from elasticsearch.serializer import JSONSerializer
from pydantic.dataclasses import dataclass

#####################################################################################################

class _ElasticSerializer(JSONSerializer):
    """JSON serializer inherited from the elastic search JSON serializer.

    Allows to serialize logs for a elasticsearch use.
    Manage the record.exc_info containing an exception type.
    """

    # Default overrides the elasticsearch default method. Allows to transform unknown types into strings.
    def default(self, data: Any) -> Any:  # noqa: WPS110
        try:
            if isinstance(data, set):
                return list(data)
            return super().default(data)
        except TypeError:
            return str(data)

#####################################################################################################

class ElasticAuthType(Enum):
    NO_AUTH = 0
    BASIC_AUTH = 1

#####################################################################################################

@dataclass(frozen=True, kw_only=True)
class ElasticHost:
    scheme: Literal['http', 'https'] = 'http'
    host: str
    port: int

#####################################################################################################

_DEFAULT_ELASTICSEARCH_PORT: Final = 9200

# Defaults for the class
_DEFAULT_ELASTICSEARCH_HOST: Final = frozenset((ElasticHost(host='localhost', port=_DEFAULT_ELASTICSEARCH_PORT),))
_DEFAULT_AUTH_USER: Final = ''
_DEFAULT_AUTH_PASSWD: Final = ''
_DEFAULT_VERIFY_SSL: Final = True
_DEFAULT_AUTH_TYPE: Final = ElasticAuthType.NO_AUTH
_DEFAULT_BUFFER_SIZE: Final = 1000
_DEFAULT_FLUSH_FREQ_IN_SEC: Final = 1
_DEFAULT_ADDITIONAL_FIELDS: Final = MappingProxyType[str, Any]({})
_DEFAULT_ES_INDEX_NAME: Final = 'python_logger'
_DEFAULT_ES_DOC_TYPE: Final = 'python_log'
_DEFAULT_RAISE_ON_EXCEPTION: Final = False
_DEFAULT_TIMESTAMP_FIELD_NAME: Final = 'timestamp'

#####################################################################################################

_LOGGING_FILTER_FIELDS: Final = (
    'msecs',
    'relativeCreated',
    'levelno',  # cspell:disable-line
    'created',
)

#####################################################################################################

def _convert_to_es_datetime_str(timestamp: float, /) -> str:
    current_date: Final = datetime.utcfromtimestamp(timestamp)
    date_part1: Final = current_date.strftime('%Y-%m-%dT%H:%M:%S')
    date_part2: Final = int(current_date.microsecond / 1000)
    return f'{date_part1!s}.{date_part2:03d}Z'

#####################################################################################################

class ElasticHandler(Handler):
    #####################################################################################################

    def __init__(
        self,
        *,
        hosts: Iterable[ElasticHost] = _DEFAULT_ELASTICSEARCH_HOST,
        auth_details: tuple[str, str] = (_DEFAULT_AUTH_USER, _DEFAULT_AUTH_PASSWD),
        auth_type: ElasticAuthType = _DEFAULT_AUTH_TYPE,
        verify_ssl: bool = _DEFAULT_VERIFY_SSL,
        buffer_size: int = _DEFAULT_BUFFER_SIZE,
        flush_frequency_in_sec: int = _DEFAULT_FLUSH_FREQ_IN_SEC,
        es_index_name: str = _DEFAULT_ES_INDEX_NAME,
        es_doc_type: str = _DEFAULT_ES_DOC_TYPE,
        es_additional_fields: MappingProxyType[str, Any] = _DEFAULT_ADDITIONAL_FIELDS,
        raise_on_indexing_exceptions: bool = _DEFAULT_RAISE_ON_EXCEPTION,
        default_timestamp_field_name: str = _DEFAULT_TIMESTAMP_FIELD_NAME,
    ):
        Handler.__init__(self)

        self.hosts: Final = hosts
        self.auth_details: Final = auth_details
        self.auth_type: Final = auth_type
        self.verify_certs: Final = verify_ssl
        self.buffer_size: Final = buffer_size
        self.flush_frequency_in_sec: Final = flush_frequency_in_sec
        self.es_index_name: Final = es_index_name
        self.es_doc_type: Final = es_doc_type

        self.es_additional_fields: Final = es_additional_fields.copy()
        self.es_additional_fields.update({
            'host': gethostname(),
            'host_ip': gethostbyname(gethostname()),
        })

        self.raise_on_indexing_exceptions: Final = raise_on_indexing_exceptions
        self.default_timestamp_field_name: Final = default_timestamp_field_name

        self._client: Elasticsearch | None = None
        self._buffer: list[dict[str, Any]] = []
        self._buffer_lock: Final = Lock()
        self._timer: Timer | None = None
        self.serializer: Final = _ElasticSerializer()

    #####################################################################################################

    def test_es_source(self, /) -> bool:
        return self._get_es_client().ping()

    #####################################################################################################

    def flush(self) -> None:
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None

        if self._buffer:
            try:
                with self._buffer_lock:
                    logs_buffer: Final = self._buffer
                    self._buffer = []
                actions = (  # pragma: no cover  # TODO: покрыть тестами в дальнейшем
                    {
                        '_index': self.es_index_name,
                        '_type': self.es_doc_type,
                        '_source': log_record,
                        '_op_type': 'create',
                    }
                    for log_record in logs_buffer
                )
                _elastic_search_helpers.bulk(
                    client=self._get_es_client(),
                    actions=actions,
                    stats_only=True,
                )
            except BaseException as exception:  # noqa: PIE786, WPS424 # pylint: disable=broad-except
                if self.raise_on_indexing_exceptions:
                    raise exception

    #####################################################################################################

    def close(self) -> None:
        if self._timer is not None:
            self.flush()
        self._timer = None

    #####################################################################################################

    def emit(self, record: LogRecord) -> None:
        self.format(record)

        rec: Final = self.es_additional_fields.copy()

        for key, value_for_send in record.__dict__.items():
            if key not in _LOGGING_FILTER_FIELDS:
                if key == 'args':
                    value_for_send = tuple(str(arg) for arg in value_for_send)
                rec[key] = '' if value_for_send is None else value_for_send

        rec[self.default_timestamp_field_name] = _convert_to_es_datetime_str(record.created)

        with self._buffer_lock:
            self._buffer.append(rec)

        if len(self._buffer) >= self.buffer_size:
            self.flush()
        else:
            self._schedule_flush()

    #####################################################################################################

    def _schedule_flush(self, /) -> None:
        if self._timer is None:
            self._timer = Timer(self.flush_frequency_in_sec, self.flush)
            self._timer.daemon = True
            self._timer.start()

    #####################################################################################################

    def _get_es_client(self, /) -> Elasticsearch:
        hosts: Final[list[NodeConfig]] = []
        for conf in self.hosts:
            hosts.append(NodeConfig(scheme=conf.scheme, host=conf.host, port=conf.port))

        if self.auth_type == ElasticAuthType.NO_AUTH:
            if self._client is None:
                self._client = Elasticsearch(
                    hosts=hosts,
                    verify_certs=self.verify_certs,
                    serializer=self.serializer,
                )
            return self._client

        if self.auth_type == ElasticAuthType.BASIC_AUTH:
            if self._client is None:
                return Elasticsearch(
                    hosts=hosts,
                    http_auth=self.auth_details,
                    verify_certs=self.verify_certs,
                    serializer=self.serializer,
                )
            return self._client

        raise ValueError('Authentication method not supported')

#####################################################################################################
