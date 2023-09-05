import logging

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aerogarden import Aerogarden
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


########
# This platform is currently disabled pending figuring out a more elegant way to toggle lighting.
# A binary sensor for light state has been added in its place.
########


class AerogardenLight(LightEntity):
    def __init__(
        self, config_id: int, aerogarden: Aerogarden, field: str, label: str
    ) -> None:
        # instance variables
        self._aerogarden = aerogarden
        self._config_id = config_id
        self._field = field
        self._label = label
        self._garden_name = self._aerogarden.get_garden_name(config_id)

        # home assistant attributes
        self._attr_name = f"{self._garden_name} {self._label}"
        self._attr_unique_id = f"{DOMAIN}-{self._config_id}-{self._field}"
        self._attr_device_info = aerogarden.get_device_info(config_id)

        _LOGGER.info("Initialized aerogarden light %s:\n%s", field, vars(self))

    async def async_update(self):
        await self._aerogarden.update()
        self._attr_is_on = (
            self._aerogarden.get_garden_property(self._config_id, self._field) == 1
        )


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    aerogarden: Aerogarden = hass.data[DOMAIN][config.entry_id]

    lights = []

    for config_id in aerogarden.get_garden_config_ids():
        lights.append(AerogardenLight(config_id, aerogarden, "lightStat", "light"))

    add_entities_callback(lights)
