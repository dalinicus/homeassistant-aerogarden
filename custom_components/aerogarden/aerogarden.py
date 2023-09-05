import base64
import logging
from datetime import timedelta

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import Throttle

from .client import AerogardenClient
from .const import (
    GARDEN_KEY_AIR_GUID,
    GARDEN_KEY_CHOOSE_GARDEN,
    GARDEN_KEY_CONFIG_ID,
    GARDEN_KEY_HW_VERSION,
    GARDEN_KEY_PLANTED_NAME,
    DOMAIN,
    GARDEN_KEY_SW_VERSION,
    MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)


class Aerogarden:
    MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

    def __init__(self, host: str, email: str, password: str) -> None:
        self._client = AerogardenClient(host, email, password)
        self._data: dict = {}

    def get_garden_config_ids(self):
        return self._data.keys()

    def get_garden_name(self, config_id):
        planted_name_decoded = self.__get_decoded_garden_name(config_id)

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

    def get_device_info(self, config_id):
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.get_garden_property(config_id, GARDEN_KEY_AIR_GUID)),
            },
            name=self.__get_decoded_garden_name(config_id),
            hw_version=self.get_garden_property(config_id, GARDEN_KEY_HW_VERSION),
            sw_version=self.get_garden_property(config_id, GARDEN_KEY_SW_VERSION),
            model=MANUFACTURER,
            manufacturer=MANUFACTURER,
        )

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
            raise UpdateFailed from ex

    def __get_decoded_garden_name(self, config_id: int) -> str:
        return base64.b64decode(
            self.get_garden_property(config_id, GARDEN_KEY_PLANTED_NAME)
        ).decode("utf-8")

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
