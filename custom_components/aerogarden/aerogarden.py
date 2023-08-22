import logging
import base64

from datetime import timedelta

from .const import (
    GARDEN_KEY_CHOOSE_GARDEN,
    GARDEN_KEY_AIR_GUID,
    GARDEN_KEY_PLANTED_NAME,
    GARDEN_KEY_LIGHT_TEMP,
    GARDEN_KEY_CONFIG_ID,
)
from .client import AerogardenClient

from homeassistant.util import Throttle
from homeassistant.helpers.update_coordinator import UpdateFailed

_LOGGER = logging.getLogger(__name__)


class Aerogarden:
    MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

    def __init__(self, host: str, username: str, password: str) -> None:
        self._client = AerogardenClient(host, username, password)
        self._data = {}

    def get_garden_config_ids(self):
        return self._data.keys()

    def get_garden_name(self, config_id):
        planted_name_decoded = base64.b64decode(
            self.get_garden_property(config_id, GARDEN_KEY_PLANTED_NAME)
        ).decode("utf-8")

        is_multi_garden = self.__is_multi_guarden(config_id)
        if not is_multi_garden:
            return planted_name_decoded

        multi_garden_label = (
            "Left"
            if self.get_garden_property(config_id, GARDEN_KEY_CHOOSE_GARDEN) == 0
            else "Right"
        )
        return f"{planted_name_decoded} ({multi_garden_label})"

    def get_garden_property(self, config_id, field):
        if config_id not in self._data or field not in self._data[config_id]:
            return None

        return self._data[config_id][field]

    async def toggle_light(self, config_id):
        """Toggles between Bright, Dimmed, and Off."""

        _LOGGER.debug(f"Recieved request to toggle lights on {config_id}")
        if config_id not in self._data:
            _LOGGER.debug(
                "light_toggle called for config_id %s, but config does not exist",
                vars(self),
            )
            return None

        air_guid = self.get_garden_property(config_id, GARDEN_KEY_AIR_GUID)
        choose_garden = self.get_garden_property(config_id, GARDEN_KEY_CHOOSE_GARDEN)

        # I couldn't find any way to set a specific state, it just cycles between the three.
        plant_config = f'{{ "lightTemp" : {self.get_garden_property(config_id, GARDEN_KEY_LIGHT_TEMP)} }}'

        await self._client.update_device_config(air_guid, choose_garden, plant_config)
        await self.update(no_throttle=True)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update(self):
        try:
            if not self._client.is_logged_in():
                await self._client.login()

            data = {}
            devices = await self._client.get_user_devices()
            for garden in devices:
                config_id = garden[GARDEN_KEY_CONFIG_ID]
                data[config_id] = garden

            self._data = data
        except Exception as ex:
            raise UpdateFailed(ex)

    def __is_multi_guarden(self, config_id: int) -> bool:
        choose_garden = self.get_garden_property(config_id, GARDEN_KEY_CHOOSE_GARDEN)
        if choose_garden > 0:
            return True  # if chooseGuarden is greater than 0, this is the right half of a multi-garden

        # if another garden exists with the same airGuid and a non-zero chooseGarden, this is the left half of a multi-garden
        air_guid = self.get_garden_property(config_id, GARDEN_KEY_AIR_GUID)
        return any(
            garden[GARDEN_KEY_AIR_GUID] == air_guid
            and garden[GARDEN_KEY_CHOOSE_GARDEN] > 0
            for garden in self._data.values()
        )
