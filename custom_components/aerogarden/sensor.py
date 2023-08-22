import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import UnitOfTime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from .aerogarden import Aerogarden
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AerogardenSensor(SensorEntity):
    def __init__(
        self,
        config_id: int,
        aerogarden: Aerogarden,
        field: str,
        label: str,
        device_class: str,
        icon: str,
        unit: str,
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
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

        _LOGGER.info("Initialized aerogarden sensor %s:\n%s", field, vars(self))

    async def async_update(self):
        self._attr_native_value = self._aerogarden.get_garden_property(
            self._config_id, self._field
        )


class AerogardenEnumSensor(SensorEntity):
    def __init__(
        self,
        config_id: int,
        aerogarden: Aerogarden,
        field: str,
        label: str,
        icon: str,
        enums: dict,
    ) -> None:
        # instance variables
        self._aerogarden = aerogarden
        self._config_id = config_id
        self._field = field
        self._label = label
        self._enums = enums
        self._garden_name = self._aerogarden.get_garden_name(config_id)

        # home assistant attributes
        self._attr_name = f"{self._garden_name} {self._label}"
        self._attr_unique_id = f"{DOMAIN}-{self._config_id}-{self._field}"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_icon = icon
        self._attr_options = list(enums.values())

        _LOGGER.info("Initialized aerogarden enum sensor %s:\n%s", field, vars(self))

    async def async_update(self):
        await self._aerogarden.update()
        pump_level: int = self._aerogarden.get_garden_property(
            self._config_id, self._field
        )
        self._attr_native_value = self._enums[pump_level]


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    aerogarden: Aerogarden = hass.data[DOMAIN][config.entry_id]

    sensors = []
    sensor_fields = {
        "plantedDay": {
            "label": "Planted Days",
            "icon": "mdi:calendar",
            "deviceClass": None,
            "unit": UnitOfTime.DAYS,
        },
        "nutriRemindDay": {
            "label": "Nutrient Days",
            "icon": "mdi:calendar-clock",
            "deviceClass": None,
            "unit": UnitOfTime.DAYS,
        },
    }

    enum_fields = {
        "pumpLevel": {
            "label": "Pump Level",
            "icon": "mdi:water-percent",
            "enums": {0: "Low", 1: "Medium", 2: "Full"},
        }
    }

    await aerogarden.update()
    for config_id in aerogarden.get_garden_config_ids():
        _LOGGER.info(f"setting up {config_id}")
        for field, field_def in sensor_fields.items():
            sensors.append(
                AerogardenSensor(
                    config_id,
                    aerogarden,
                    field,
                    field_def["label"],
                    field_def["deviceClass"],
                    field_def["icon"],
                    field_def["unit"],
                )
            )

        for field, field_def in enum_fields.items():
            sensors.append(
                AerogardenEnumSensor(
                    config_id,
                    aerogarden,
                    field,
                    field_def["label"],
                    field_def["icon"],
                    field_def["enums"],
                )
            )

    add_entities_callback(sensors)
