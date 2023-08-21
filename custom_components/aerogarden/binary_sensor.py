import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aerogarden import Aerogarden
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class AerogardenBinarySensor(BinarySensorEntity):
    def __init__(self, config_id:int, aerogarden:Aerogarden, field:str, label:str, icon:str):
        # instance variables
        self._aerogarden = aerogarden
        self._config_id = config_id
        self._field = field
        self._label = label
        self._garden_name = self._aerogarden.garden_name(config_id)

        # home assistant attributes
        self._attr_name = f"{self._garden_name} {self._label}"
        self._attr_unique_id = f"{DOMAIN}-{self._config_id}-{self._field}"
        self._attr_icon = icon

        _LOGGER.debug("Initialized garden binary sensor %s:\n%s", field, vars(self))

    def update(self):
        self._aerogarden.update()
        self._attr_is_on = self._aerogarden.garden_property(self._config_id, self._field) == 1

async def async_setup_entry(hass:HomeAssistant, config:ConfigEntry, add_entities_callback:AddEntitiesCallback) -> None:
    aerogarden:Aerogarden = hass.data[DOMAIN][config.entry_id]
    
    sensors = []
    sensor_fields = {
        "pumpStat": {
            "label": "pump",
            "icon": "mdi:water-pump",
        },
        "nutriStatus": {
            "label": "Needs nutrients",
            "icon": "mdi:cup-water",
        },
        "pumpHydro": {
            "label": "Needs water",
            "icon": "mdi:water",
        }
    }

    for config_id in aerogarden.get_garden_config_ids():
        for field in sensor_fields.keys():
            sensor_def = sensor_fields[field]
            sensors.append(
                AerogardenBinarySensor(
                    config_id, aerogarden, field, sensor_def["label"], sensor_def["icon"]
                )
            )

    add_entities_callback(sensors)