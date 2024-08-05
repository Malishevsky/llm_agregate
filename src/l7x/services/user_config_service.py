#####################################################################################################

from logging import Logger
from typing import Final

from pydantic.dataclasses import dataclass

from l7x.db import UserConfigModel
from l7x.db.base_meta import DbBaseMeta
from l7x.db.db_field_names import DB_PRIMARY_UUID_FIELD_NAME
from l7x.db.db_utils import get_fa
from l7x.services.base import BaseService
from l7x.services.langs_service import LangsService, check_language

#####################################################################################################

@dataclass(kw_only=True)
class UserConfig:
    source_lang: str

#####################################################################################################

class UserConfigService(BaseService):
    #####################################################################################################

    def __init__(self, logger: Logger, langs_service: LangsService) -> None:
        self._logger: Final = logger
        self._langs_service = langs_service

    #####################################################################################################

    async def update_user_config(
        self,
        *,
        user_id: str,
        config: UserConfig,
    ) -> None:
        async with DbBaseMeta.database.transaction():

            clause = UserConfigModel.objects.filter(get_fa(UserConfigModel.user_id) == user_id).limit(1)

            entity_id: Final = await clause.values_list(fields=[DB_PRIMARY_UUID_FIELD_NAME], exclude_through=True, flatten=True)

            available_lang_options: Final = await self._langs_service.get_lang_options()
            source_lang: Final = check_language(config.source_lang, available_lang_options)

            user_config: Final = UserConfigModel(
                user_id=user_id,
                source_lang=source_lang,
            )

            if len(entity_id) == 1:
                user_config.primary_uuid = entity_id[0]

            await user_config.upsert()

    #####################################################################################################

    async def find_user_config(self, *, user_id: str) -> UserConfig:
        clause = UserConfigModel.objects.filter(get_fa(UserConfigModel.user_id) == user_id).limit(1)

        user_config: Final = await clause.get_or_none()
        if user_config is None:
            return UserConfig(source_lang='')

        available_lang_options: Final = await self._langs_service.get_lang_options()
        source_lang: Final = check_language(user_config.source_lang, available_lang_options)

        return UserConfig(
            source_lang=source_lang,
        )

#####################################################################################################
