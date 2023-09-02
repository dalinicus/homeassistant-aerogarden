import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aerogarden import Aerogarden
from .const import (
    DOMAIN,
    GARDEN_KEY_NUTRI_REMIND_DAY,
    GARDEN_KEY_PLANTED_DAY,
    GARDEN_KEY_PUMP_LEVEL,
)

_LOGGER = logging.getLogger(__name__)


class AerogardenSensorBase(SensorEntity):
    def __init__(
        self, config_id: int, aerogarden: Aerogarden, field: str, label: str, icon: str
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
        self._attr_icon = icon


class AerogardenSensor(AerogardenSensorBase):
    def __init__(
        self,
        config_id: int,
        aerogarden: Aerogarden,
        field: str,
        label: str,
        icon: str,
        unit: str,
    ) -> None:
        super().__init__(config_id, aerogarden, field, label, icon)
        self._attr_native_unit_of_measurement = unit

        _LOGGER.info("Initialized aerogarden sensor %s:\n%s", field, vars(self))

    async def async_update(self):
        self._attr_native_value = self._aerogarden.get_garden_property(
            self._config_id, self._field
        )


class AerogardenEnumSensor(AerogardenSensorBase):
    def __init__(
        self,
        config_id: int,
        aerogarden: Aerogarden,
        field: str,
        label: str,
        icon: str,
        enums: dict,
    ) -> None:
        super().__init__(config_id, aerogarden, field, label, icon)

        self._enums = enums
        self._attr_device_class = SensorDeviceClass.ENUM
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
    sensor_fields: dict[str, dict] = {
        GARDEN_KEY_PLANTED_DAY: {
            "label": "Planted Days",
            "icon": "mdi:calendar",
            "unit": UnitOfTime.DAYS,
        },
        GARDEN_KEY_NUTRI_REMIND_DAY: {
            "label": "Nutrient Days",
            "icon": "mdi:calendar-clock",
            "unit": UnitOfTime.DAYS,
        },
    }

    enum_fields: dict[str, dict] = {
        GARDEN_KEY_PUMP_LEVEL: {
            "label": "Pump Level",
            "icon": "mdi:water-percent",
            "enums": {0: "Low", 1: "Medium", 2: "Full"},
        }
    }

    await aerogarden.update()
    for config_id in aerogarden.get_garden_config_ids():
        _LOGGER.info("setting up %(config_id)s", config_id)
        for field, field_def in sensor_fields.items():
            sensors.append(
                AerogardenSensor(
                    config_id,
                    aerogarden,
                    field,
                    field_def["label"],
                    field_def["icon"],
                    field_def["unit"],
                )
            )

        for enum_field, enum_def in enum_fields.items():
            sensors.append(
                AerogardenEnumSensor(
                    config_id,
                    aerogarden,
                    enum_field,
                    enum_def["label"],
                    enum_def["icon"],
                    enum_def["enums"],
                )
            )

    add_entities_callback(sensors)
