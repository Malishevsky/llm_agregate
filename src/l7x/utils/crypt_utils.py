#####################################################################################################

from abc import ABC, abstractmethod
from base64 import urlsafe_b64decode, urlsafe_b64encode
from logging import Logger
from os import urandom
from types import MappingProxyType
from typing import Any, Final

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESSIV  # type: ignore
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from l7x.types.errors import AppException

#####################################################################################################

_KEY_LENGTH: Final = 64

_CODE_PAGE: Final = 'utf-8'

#####################################################################################################

def calc_secrets(init_secret: str) -> bytes:
    if not init_secret:
        return b''

    key_iterations: Final = 480000
    key_salt: Final = '#N25SpemH=HnPotpMyrSPYQNqcO0I)0GJZXzGnO8CN7-JRwZWi5(OcPjuQU6n6Yw6'  # cspell:disable-line

    kdf: Final = PBKDF2HMAC(
        algorithm=hashes.SHA3_512(),
        length=_KEY_LENGTH,
        salt=key_salt.encode(encoding='utf-8'),
        iterations=key_iterations,
    )

    return kdf.derive(init_secret.encode(encoding='utf-8'))

#####################################################################################################

class _Cryptographer(ABC):
    #####################################################################################################

    VERSION = '-'

    #####################################################################################################

    @abstractmethod
    def encode(self, original_text: str) -> str:
        raise NotImplementedError()

    #####################################################################################################

    @abstractmethod
    def decode(self, crypt_text: str) -> str:
        raise NotImplementedError()

#####################################################################################################

class _CryptographerVersionWithoutCrypt(_Cryptographer):
    #####################################################################################################

    VERSION = '0'

    #####################################################################################################

    def encode(self, original_text: str) -> str:
        return original_text

    #####################################################################################################

    def decode(self, crypt_text: str) -> str:
        return crypt_text

#####################################################################################################

class _CryptographerVersionWithCrypt1(_Cryptographer):
    #####################################################################################################

    VERSION = '1'
    _VERSION_BINARY: Final = VERSION.encode(encoding=_CODE_PAGE)

    #####################################################################################################

    def __init__(self, key: bytes, logger: Logger) -> None:
        self._aessiv: Final = AESSIV(key=key)
        self._logger = logger

    #####################################################################################################

    def encode(self, original_text: str) -> str:
        nonce: Final = urandom(_KEY_LENGTH)
        associated_data: Final = [
            self._VERSION_BINARY,
            nonce,
        ]
        cipher_text: Final[bytes] = self._aessiv.encrypt(
            data=original_text.encode(encoding=_CODE_PAGE),
            associated_data=associated_data,
        )
        ret_bytes = nonce + cipher_text
        return urlsafe_b64encode(ret_bytes).decode(encoding=_CODE_PAGE)

    #####################################################################################################

    def decode(self, crypt_text: str) -> str:
        crypt_bytes: Final = urlsafe_b64decode(crypt_text.encode(encoding=_CODE_PAGE))

        nonce: Final = crypt_bytes[:_KEY_LENGTH]
        associated_data: Final = [
            self._VERSION_BINARY,
            nonce,
        ]
        original_bytes: Final[bytes] = self._aessiv.decrypt(
            data=crypt_bytes[_KEY_LENGTH:],
            associated_data=associated_data,
        )

        return original_bytes.decode(encoding=_CODE_PAGE)

#####################################################################################################

class Cryptographer:
    #####################################################################################################

    _SEPARATOR: Final = '@'

    #####################################################################################################

    def __init__(self, logger: Logger, key: bytes) -> None:
        self._logger = logger
        cryptographers: Final[dict[str, _Cryptographer]] = {}

        cryptographers[_CryptographerVersionWithoutCrypt.VERSION] = _CryptographerVersionWithoutCrypt()
        self._prefer_encode_cryptographer = cryptographers[_CryptographerVersionWithoutCrypt.VERSION]

        if key != b'':
            cryptographers[_CryptographerVersionWithCrypt1.VERSION] = _CryptographerVersionWithCrypt1(key, logger)
            self._prefer_encode_cryptographer = cryptographers[_CryptographerVersionWithCrypt1.VERSION]

        for cryptographer_version in cryptographers:
            if len(cryptographer_version) != len(cryptographer_version.encode(encoding=_CODE_PAGE)) or len(cryptographer_version) != 1:
                raise AppException(detail=f'Invalid cryptographer version: {cryptographer_version}')

        self._cryptographers = MappingProxyType(cryptographers)

    #####################################################################################################

    def encode(self, original_text: str) -> str:
        cipher_text: Final = self._prefer_encode_cryptographer.encode(original_text)
        return self._prefer_encode_cryptographer.VERSION + self._SEPARATOR + cipher_text

    #####################################################################################################

    def decode(self, crypt_text: str) -> str:
        if crypt_text[1] != self._SEPARATOR:
            raise AppException(detail=f"Can't find crypt separator '{self._SEPARATOR}' in '{crypt_text}'")

        cryptographer_version_needed: Final = crypt_text[0]
        for (cryptographer_version, cryptographer) in self._cryptographers.items():
            if cryptographer_version == cryptographer_version_needed:
                return cryptographer.decode(crypt_text[2:])

        raise AppException(detail=f'Unsupported crypt version: {cryptographer_version_needed}')

    #####################################################################################################

    def encode_with_none(self, original_text: str | None) -> str | None:
        if original_text is None:
            return None
        return self.encode(original_text)

    #####################################################################################################

    def decode_with_none(self, crypt_text: str | None) -> str | None:
        if crypt_text is None:
            return None
        return self.decode(crypt_text)

#####################################################################################################

def crypt_encode_fields_in_dict(cryptographer: Cryptographer, dict_for_encode: dict[str, Any], *field_names: str) -> None:
    for field_name in field_names:
        text_for_replace = dict_for_encode.get(field_name)
        if text_for_replace is None:
            continue
        if not isinstance(text_for_replace, str):
            raise ValueError(f'{field_name} is not string')
        dict_for_encode[field_name] = cryptographer.encode(text_for_replace)

#####################################################################################################

def crypt_decode_fields_in_dict(cryptographer: Cryptographer, dict_for_decode: dict[str, Any], *field_names: str) -> None:
    for field_name in field_names:
        text_for_replace = dict_for_decode.get(field_name)
        if text_for_replace is None:
            continue
        if not isinstance(text_for_replace, str):
            raise ValueError(f'{field_name} is not string')
        dict_for_decode[field_name] = cryptographer.decode(text_for_replace)

#####################################################################################################
