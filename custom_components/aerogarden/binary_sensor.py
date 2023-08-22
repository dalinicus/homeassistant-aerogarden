import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aerogarden import Aerogarden
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AerogardenBinarySensor(BinarySensorEntity):
    def __init__(
        self,
        config_id: int,
        aerogarden: Aerogarden,
        field: str,
        label: str,
        device_class: str,
        icon: str,
    ) -> None:
        # instance variables
        self._aerogarden = aerogarden
        self._config_id = config_id
        self._field = field
        self._label = label
        self._garden_name = self._aerogarden.get_garden_name(config_id)

        # home assistant attributes
        self._attr_device_class = device_class
        self._attr_name = f"{self._garden_name} {self._label}"
        self._attr_unique_id = f"{DOMAIN}-{self._config_id}-{self._field}"
        self._attr_icon = icon

        _LOGGER.info("Initialized aerogarden binary sensor %s:\n%s", field, vars(self))

    async def async_update(self):
        await self._aerogarden.update()
        self._attr_is_on = (
            self._aerogarden.get_garden_property(self._config_id, self._field) == 1
        )


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    aerogarden: Aerogarden = hass.data[DOMAIN][config.entry_id]

    sensors = []
    sensor_fields = {
        "pumpStat": {
            "label": "Pump",
            "deviceClass": BinarySensorDeviceClass.RUNNING,
            "icon": "mdi:water-pump",
        },
        "nutriStatus": {
            "label": "Needs Nutrients",
            "deviceClass": BinarySensorDeviceClass.PROBLEM,
            "icon": "mdi:cup-water",
        },
        "pumpHydro": {
            "label": "Needs Water",
            "deviceClass": BinarySensorDeviceClass.PROBLEM,
            "icon": "mdi:water",
        },
        "lightReadOnly": {
            "label": "Light",
            "deviceClass": BinarySensorDeviceClass.LIGHT,
            "icon": "mdi:lightbulb",
        },
    }

    for config_id in aerogarden.get_garden_config_ids():
        for field, field_def in sensor_fields.items():
            sensors.append(
                AerogardenBinarySensor(
                    config_id,
                    aerogarden,
                    field,
                    field_def["label"],
                    field_def["deviceClass"],
                    field_def["icon"],
                )
            )

    add_entities_callback(sensors)
