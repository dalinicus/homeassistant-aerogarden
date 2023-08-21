import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.light import LightEntity

from .aerogarden import Aerogarden
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class AerogardenLight(LightEntity):
    def __init__(self, config_id:int, aerogarden:Aerogarden, field:str, label:str, icon:str):
        # instance variables
        self._aerogarden = aerogarden
        self._config_id = config_id
        self._field = field
        self._label = label
        self._garden_name = self._aerogarden.get_garden_name(config_id)

        # home assistant attributes
        self._attr_name = f"{self._garden_name} {self._label}"
        self._attr_unique_id = f"{DOMAIN}-{self._config_id}-{self._field}"
        self._attr_icon = icon

        _LOGGER.debug("Initialized garden light %s:\n%s", field, vars(self))

    def turn_on(self, **kwargs):
        self._aerogarden.toggle_light(self._config_id)
        self._attr_is_on = 1

    def turn_off(self, **kwargs):
        self._aerogarden.toggle_light(self._config_id)
        self._attr_is_on = 0

    def update(self):
        self._aerogarden.update()
        self._attr_is_on = self._aerogarden.get_garden_property(self._config_id, self._field) == 1


async def async_setup_entry(hass:HomeAssistant, config:ConfigEntry, add_entities_callback:AddEntitiesCallback) -> None:
    aerogarden:Aerogarden = hass.data[DOMAIN][config.entry_id]
    
    lights = []

    for config_id in aerogarden.get_garden_config_ids():
        lights.append(AerogardenLight(config_id, aerogarden, "lightStat", "light"))

    add_entities_callback(lights)