#!/usr/bin/env -S poetry run python

#####################################################################################################

import argparse
import os
import re
from collections import OrderedDict
from collections.abc import Iterable, Mapping, Sequence
from logging import INFO, Logger, StreamHandler, getLogger
from pathlib import Path
from typing import Any, Final, cast

from dotenv import load_dotenv
# pylint: disable-next=no-name-in-module
from orjson import OPT_INDENT_2, OPT_SORT_KEYS
from pydantic.dataclasses import dataclass
from redbaron import RedBaron
from redbaron.nodes import AssignmentNode
from wlc import Translation, Weblate, WeblateException

from l7x.configs.settings import create_app_settings
from l7x.types.language import LKey
from l7x.types.localization import TKey
from l7x.utils.orjson_utils import orjson_default, orjson_dumps, orjson_loads

#####################################################################################################

_LOGGER: Final = getLogger(__name__)
_STREAM_HANDLER: Final = StreamHandler()
_LOGGER.addHandler(_STREAM_HANDLER)
_LOGGER.setLevel(INFO)

#####################################################################################################

load_dotenv()

#####################################################################################################

_APP_SETTINGS: Final = create_app_settings()

_WEBLATE_API_KEY: Final = os.getenv('L7X_WEBLATE_API_KEY')
_WEBLATE_API_URL: Final = os.getenv('L7X_WEBLATE_API_URL')

_WEBLATE_PROJECT_NAME: Final = _APP_SETTINGS.service_name
_WEBLATE_COMPONENT_NAME: Final = f'{_WEBLATE_PROJECT_NAME}-localization'

#####################################################################################################

weblate_client = Weblate(key=_WEBLATE_API_KEY, url=_WEBLATE_API_URL)

#####################################################################################################

def _get_project_info(logger: Logger) -> Mapping[str, Any] | None:
    try:
        return weblate_client.get_project(_WEBLATE_PROJECT_NAME)  # type: ignore
    except WeblateException as exc:
        logger.error(f'Cannot get project info for "{_WEBLATE_PROJECT_NAME}". Error: {exc}')
        return None

#####################################################################################################

def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return re.sub('^-+|-+$', '', slug)

#####################################################################################################

def _create_project(logger: Logger) -> Mapping[str, Any] | None:
    try:
        return weblate_client.create_project(  # type: ignore
            name=_WEBLATE_PROJECT_NAME,
            slug=_slugify(_WEBLATE_PROJECT_NAME),
            website='',
        )
    except WeblateException as exc:
        logger.error(f'Cannot create project "{_WEBLATE_PROJECT_NAME}". Error: {exc}')
        return None

#####################################################################################################

def _get_component_info(logger: Logger) -> Mapping[str, Any] | None:
    try:
        return weblate_client.get_component(f'{_WEBLATE_PROJECT_NAME}/{_WEBLATE_COMPONENT_NAME}')  # type: ignore
    except WeblateException as exc:
        logger.error(f'Cannot get component info for "{_WEBLATE_COMPONENT_NAME}". Error: {exc}')
        return None

#####################################################################################################

def _convert_enum_to_bytes(source: type[TKey]) -> bytes:
    enum_dict: Final = {localization_key.name: localization_key.default_text for localization_key in source}
    return orjson_dumps(enum_dict, option=OPT_INDENT_2 | OPT_SORT_KEYS, default=orjson_default)

#####################################################################################################

def _create_component(logger: Logger) -> Mapping[str, Any] | None:
    try:
        return weblate_client.create_component(  # type: ignore
            project=_WEBLATE_PROJECT_NAME,
            name=_WEBLATE_COMPONENT_NAME,
            slug=_slugify(_WEBLATE_COMPONENT_NAME),
            file_format='json',
            filemask='*.json',  # cspell:disable-line
            repo='',
            template='en.json',
            docfile=_convert_enum_to_bytes(TKey),  # cspell:disable-line
            edit_template=True,
        )
    except WeblateException as exc:
        logger.error(f'Cannot create component in {_WEBLATE_PROJECT_NAME}. Error: {exc}')
        return None

#####################################################################################################

def _create_translation(language: LKey, logger: Logger) -> Mapping[str, Any] | None:
    payload: Final = {'language_code': language.value}
    try:
        return weblate_client.post(  # type: ignore
            f'components/{_WEBLATE_PROJECT_NAME}/{_WEBLATE_COMPONENT_NAME}/translations/',
            **payload,
        )
    except WeblateException as exc:
        logger.error(f'Cannot create translation for language "{language.value}". Error: {exc}')
        return None

#####################################################################################################

class _LanguageNotAddedError(Exception):
    """NOTHING."""

#####################################################################################################

def _create_translations(logger: Logger) -> None:
    for language in LKey:
        if language == LKey.EN:  # Skip source language
            continue

        response = _create_translation(language, logger)
        if response is None:
            raise _LanguageNotAddedError

        logger.info(f'Language "{language.value}" was added into component "{_WEBLATE_COMPONENT_NAME}"')

#####################################################################################################

class _ComponentNotCreatedError(Exception):
    """NOTHING."""

#####################################################################################################

def _create_component_with_languages(logger: Logger) -> None:
    create_component_response: Final = _create_component(logger)
    if create_component_response is None:
        raise _ComponentNotCreatedError

    try:
        _create_translations(logger)
    except _LanguageNotAddedError as exc:
        logger.error(f'Component "{_WEBLATE_COMPONENT_NAME}" was not configured')
        raise _ComponentNotCreatedError from exc

    logger.info(f'Component "{_WEBLATE_COMPONENT_NAME}" was configured successfully')

#####################################################################################################

_DEFAULT_LANGUAGE: Final = LKey.EN.value

#####################################################################################################

@dataclass(kw_only=True, frozen=True)
class _ComponentUnit:
    unit_id: int
    key: str
    text: str

#####################################################################################################

def _get_component_source_translation(logger: Logger) -> Mapping[str, _ComponentUnit] | None:
    default_units: Final = {}
    url = f'translations/{_WEBLATE_PROJECT_NAME}/{_WEBLATE_COMPONENT_NAME}/{_DEFAULT_LANGUAGE}/units/'

    while True:
        try:
            units_response = weblate_client.get(url)
        except WeblateException as exc:
            logger.error(f'Cannot get units in component "{_WEBLATE_COMPONENT_NAME}". Error: {exc}')
            return None

        units_raw = units_response.get('results', [])
        for unit in units_raw:
            unit_key = unit['context']
            default_units.update({unit_key: _ComponentUnit(text=unit['source'][0], unit_id=unit['id'], key=unit_key)})

        next_page = units_response.get('next')
        if not next_page:
            break
        url = next_page

    return default_units

#####################################################################################################

class _SourceStringNotAddedError(Exception):
    """NOTHING."""

#####################################################################################################

def _add_source_string(localization_key: TKey, logger: Logger) -> None:
    try:
        weblate_client.add_source_string(
            project=_WEBLATE_PROJECT_NAME,
            component=_WEBLATE_COMPONENT_NAME,
            msgid=localization_key.name,
            msgstr=localization_key.default_text,
            source_language=_DEFAULT_LANGUAGE,
        )
        logger.info(f'Source "{localization_key.name}" was added to component "{_WEBLATE_COMPONENT_NAME}"')
    except WeblateException as exc:
        logger.error(f'Cannot add source "{localization_key.name}" to component "{_WEBLATE_COMPONENT_NAME}". Error: {exc}')
        raise _SourceStringNotAddedError from exc

#####################################################################################################

def _update_source_string(unit_id: int, key: str, new_text: str, logger: Logger) -> Mapping[str, Any] | None:
    payload: Final = {
        'state': 20,  # https://docs.weblate.org/en/latest/api.html#patch--api-units-(int-id)-
        'target': [new_text],
    }
    try:
        return weblate_client.patch(f'units/{unit_id}/', **payload)  # type: ignore
    except WeblateException as exc1:
        logger.error(f'Cannot update source string "{key}". Error: {exc1}')

    return None

#####################################################################################################

def _check_localizations(component_source_translation: Mapping[str, _ComponentUnit], logger: Logger) -> None:
    for localization_key in TKey:
        key_name = localization_key.name
        if key_name not in component_source_translation:
            _add_source_string(localization_key, logger)
            continue
        weblate_source_translation = component_source_translation[key_name]
        if localization_key.default_text != weblate_source_translation.text:
            update_response = _update_source_string(weblate_source_translation.unit_id, key_name, localization_key.default_text, logger)
            if update_response is None:
                raise _SourceStringNotAddedError

#####################################################################################################

def _get_project_languages(logger: Logger) -> Iterable[str] | None:
    try:
        languages_response: Final = weblate_client.get(f'components/{_WEBLATE_PROJECT_NAME}/{_WEBLATE_COMPONENT_NAME}/translations/')
        return (lang['language']['code'] for lang in languages_response.get('results', []))
    except WeblateException as exc:
        logger.error(f'Cannot get languages from {_WEBLATE_PROJECT_NAME}. Error: {exc}')
        return None

#####################################################################################################

def _check_languages(logger: Logger) -> None:
    weblate_project_languages: Final = _get_project_languages(logger)
    if weblate_project_languages is None:
        return

    languages: Final = (language.value for language in LKey)
    lang_diff: Final = set(languages).difference(weblate_project_languages)

    if lang_diff:
        logger.warning(f'There is a difference between languages: {lang_diff}')

#####################################################################################################

def _translate_component_to_single_language(language: LKey, logger: Logger) -> Mapping[str, Any] | None:
    payload: Final = {
        'mode': 'translate',
        'filter_type': 'todo',  # TODO: Сейчас включен перевод только новых фраз
        'auto_source': 'mt',
        'threshold': '80',
        'engines': ['custom-google-translate'],
    }
    try:
        return weblate_client.post(  # type: ignore
            f'translations/{_WEBLATE_PROJECT_NAME}/{_WEBLATE_COMPONENT_NAME}/{language.value}/autotranslate/',  # cspell:disable-line
            **payload,
        )
    except WeblateException as exc:
        logger.error(f'Cannot translate component "{_WEBLATE_COMPONENT_NAME}" to language {language}. Error: {exc}')
        return None

#####################################################################################################

class _ComponentNotTranslatedError(Exception):
    """NOTHING."""

#####################################################################################################

def _translate_project(logger: Logger) -> None:
    for language in LKey:
        if language == LKey.EN:  # Skip source language
            continue

        logger.info(f'Translating component "{_WEBLATE_COMPONENT_NAME}" into "{language}" language...')
        translate_response = _translate_component_to_single_language(language, logger)

        if translate_response is None:
            raise _ComponentNotTranslatedError

        details = translate_response.get('details', {})
        message = details.get('message')
        logger.info(f'Status: {message}')

#####################################################################################################

def _get_translation(language: LKey, logger: Logger) -> Translation | None:
    try:
        return weblate_client.get_translation(path=f'{_WEBLATE_PROJECT_NAME}/{_WEBLATE_COMPONENT_NAME}/{language.value}')
    except WeblateException as exc:
        logger.error(f'Cannot get translation for "{language.value}" language in component "{_WEBLATE_COMPONENT_NAME}". Error: {exc}')
        return None

#####################################################################################################

def _parse_translation(translation: Translation, logger: Logger) -> str | None:
    try:
        body: Final = translation.download()
    except Exception as exc:  # noqa: PIE786  # pylint: disable=broad-exception-caught
        logger.error(f'Cannot get translation body. Error: {exc}')
        return None

    return body.decode()  # type: ignore

#####################################################################################################

_WRAP_PATTERN: Final = re.compile(r'(\[@(?P<non_translated>.*?)@\])', re.MULTILINE)

#####################################################################################################

def _unwrap(match: re.Match[str]) -> str:
    return match.group('non_translated')

#####################################################################################################

def _clean_wraps(text: str) -> str:
    return _WRAP_PATTERN.sub(_unwrap, text)

#####################################################################################################

def _download_translations(logger: Logger) -> Mapping[str, Mapping[str, str]] | None:
    component_translations: Final = {}

    for language in LKey:
        logger.info(f'Getting "{language.value}" translation for component "{_WEBLATE_COMPONENT_NAME}"...')
        translation = _get_translation(language, logger)
        if translation is None:
            return None

        if translation.translated_percent != 100:
            logger.error(f'WARNING: Translation "{language}" is translated only {translation.translated_percent}%')
            return None

        translated_body = _parse_translation(translation, logger)
        if translated_body is None:
            return None

        if language == LKey.EN:
            translated_body = _clean_wraps(translated_body)

        unsorted_language_translation = orjson_loads(translated_body)
        sorted_language_translation = OrderedDict(sorted(unsorted_language_translation.items()))
        component_translations[language.value] = sorted_language_translation
        logger.info(f'Got "{language.value}" translation for component "{_WEBLATE_COMPONENT_NAME}"')
    return component_translations

#####################################################################################################

_SUBSTITUTE_PATTERN: Final = re.compile('{.+?}')

#####################################################################################################

def _regroup_single_localization_key_map(
    localization_key: TKey,
    project_translations: Mapping[str, Mapping[str, str]],
    logger: Logger,
) -> Mapping[str, str] | None:
    localization_key_map: Final = {}
    substitute_params: Final = set(_SUBSTITUTE_PATTERN.findall(localization_key.default_text))

    for language, translations in project_translations.items():
        localized_sentence = translations.get(localization_key.name, '')
        if not localized_sentence:
            logger.error(f'Cannot find localized sentence for "{localization_key.name}" in "{language}" section')
            return None

        if substitute_params:
            substitute_localized_params = set(_SUBSTITUTE_PATTERN.findall(localized_sentence))
            if substitute_params != substitute_localized_params:
                logger.error(f'Cannot find params to substitute in localized string for "{language}:{localization_key.name}"')
                return None

        localization_key_map[language] = localized_sentence

    return localization_key_map

#####################################################################################################

def _regroup_localization_key_maps(translations: Mapping[str, Mapping[str, str]], logger: Logger) -> Mapping[str, Mapping[str, str]] | None:
    localization_key_maps: Final = {}
    for localization_key in TKey:
        localization_key_map = _regroup_single_localization_key_map(localization_key, translations, logger)
        if localization_key_map is None:
            return None
        localization_key_maps[localization_key.name] = localization_key_map
    return localization_key_maps

#####################################################################################################

def _find_map_node(map_pattern: str, source_nodes: RedBaron) -> Any:  # TODO: Возможно поправить тайпхинт с Any
    return next((node for node in source_nodes.data if isinstance(node[0], AssignmentNode) and node[0].target.value == map_pattern), None)

#####################################################################################################

def _replace_quotes(text: str) -> str:
    if "'" in text:
        if '"' in text:
            text = text.replace("'", "\\'")  # noqa: WPS342
            return f"'{text}'"
        return f'"{text}"'
    return f"'{text}'"

#####################################################################################################

def _build_single_localized_string_nodes(language: LKey, localized_sentence: str, indent: str) -> Sequence[Mapping[str, Any]]:
    localized_sentence = _replace_quotes(localized_sentence)
    return [
        {
            'type': 'dictitem',  # cspell:disable-line
            'first_formatting': [],
            'second_formatting': [
                {
                    'type': 'space',
                    'value': ' ',
                },
            ],
            'key': {
                'type': 'atomtrailers',  # cspell:disable-line
                'value': [
                    {
                        'type': 'name',
                        'value': 'LKey',
                    },
                    {
                        'type': 'dot',
                        'first_formatting': [],
                        'second_formatting': [],
                    },
                    {
                        'type': 'name',
                        'value': language.name,
                    },
                ],
            },
            'value': {
                'type': 'string',
                'value': localized_sentence,
                'first_formatting': [],
                'second_formatting': [],
            },
        },
        {
            'type': 'comma',
            'first_formatting': [],
            'second_formatting': [
                {
                    'type': 'endl',  # cspell:disable-line
                    'value': '\n',
                    'indent': indent,
                    'formatting': [],
                },
            ],
        },
    ]

#####################################################################################################

_INDENT_FOUR_SPACES: Final = ' ' * 4
_NO_INDENT: Final = ''

#####################################################################################################

def _build_localization_map_node(localized_sentences: Mapping[str, str]) -> Mapping[str, Any]:
    localized_string_nodes: Final[list[Mapping[str, Any]]] = []
    total_languages_count: Final = len(LKey)

    for idx, language in enumerate(sorted(LKey), start=1):
        language = cast(LKey, language)
        indent = _NO_INDENT if idx == total_languages_count else _INDENT_FOUR_SPACES
        localized_sentence = localized_sentences[language.value]
        single_localized_string_nodes = _build_single_localized_string_nodes(language, localized_sentence, indent)
        localized_string_nodes.extend(single_localized_string_nodes)

    return {
        'type': 'atomtrailers',  # cspell:disable-line
        'value': [
            {
                'type': 'name',
                'value': 'FrozenDict',
            },
            {
                'type': 'call',
                'first_formatting': [],
                'second_formatting': [],
                'value': [
                    {
                        'type': 'call_argument',
                        'first_formatting': [],
                        'second_formatting': [],
                        'target': {},
                        'value': {
                            'type': 'dict',
                            'first_formatting': [],
                            'second_formatting': [
                                {
                                    'type': 'endl',  # cspell:disable-line
                                    'value': '\n',
                                    'indent': _INDENT_FOUR_SPACES,
                                    'formatting': [],
                                },
                            ],
                            'value': localized_string_nodes,
                            'third_formatting': [],
                            'fourth_formatting': [],
                        },
                    },
                ],
                'third_formatting': [],
                'fourth_formatting': [],
            },
        ],
    }

#####################################################################################################

def _update_source_nodes(
    source_nodes: RedBaron,
    localization_key_maps: Mapping[str, Mapping[str, str]],
    logger: Logger,
) -> RedBaron | None:
    for localization_key in TKey:
        key_name = localization_key.name
        node = _find_map_node(map_pattern=f'_{key_name}_MAP', source_nodes=source_nodes)

        if node is None:
            logger.error(f'Cannot find node for {key_name}')
            return None

        node[0].value = _build_localization_map_node(localization_key_maps[key_name])

    return source_nodes

#####################################################################################################

_CURRENT_DIR: Final = Path(__file__).parent.resolve()
_LOCALIZATION_TYPES_MODULE_PATH: Final = _CURRENT_DIR.joinpath('l7x', 'types', 'localization.py')

#####################################################################################################

def _sync_command(logger: Logger) -> None:
    # Check project or create
    project_info: Final = _get_project_info(logger)
    if project_info is None:
        create_project_response: Final = _create_project(logger)
        if create_project_response is None:
            return

    # Check component or create
    component_info: Final = _get_component_info(logger)
    if component_info is None:
        try:
            _create_component_with_languages(logger)
        except _ComponentNotCreatedError:
            return

    # Get weblate en source data
    component_source_translation: Final = _get_component_source_translation(logger)
    if component_source_translation is None:
        return

    # Add necessary keys or update changes
    # TODO: Добавить возможность удаления устаревших ключей
    try:
        _check_localizations(component_source_translation, logger)
    except _SourceStringNotAddedError:
        return

    # TODO: Добавить добавление языков
    _check_languages(logger)

    # Try to translate
    try:
        _translate_project(logger)
    except _ComponentNotTranslatedError:
        logger.error(f'Project "{_WEBLATE_PROJECT_NAME}" was not translated')
        return

    # Download translations
    project_translations: Final = _download_translations(logger)
    if project_translations is None:
        return

    localization_key_maps: Final = _regroup_localization_key_maps(project_translations, logger)
    if localization_key_maps is None:
        return

    with open(_LOCALIZATION_TYPES_MODULE_PATH, encoding='utf-8') as source:
        source_code_nodes: Final = RedBaron(source.read())

    target_nodes: Final = _update_source_nodes(source_code_nodes, localization_key_maps, logger)
    if target_nodes is None:
        return

    with open(_LOCALIZATION_TYPES_MODULE_PATH, 'w', encoding='utf-8') as target:
        target.write(target_nodes.dumps())

    logger.info('Done...')

#####################################################################################################

def main(logger: Logger) -> None:
    parser: Final = argparse.ArgumentParser()
    subparsers: Final = parser.add_subparsers()

    # sync command parser
    sync_parser: Final = subparsers.add_parser(name='sync')
    sync_parser.set_defaults(func=_sync_command)

    args: Final = parser.parse_args()
    args.func(logger)

#####################################################################################################

if __name__ == '__main__':
    main(_LOGGER)

#####################################################################################################
