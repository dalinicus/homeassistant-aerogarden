import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.aerogarden import (
    AerogardenDataUpdateCoordinator,
    AerogardenEntity,
)

from .const import (
    DOMAIN,
    GARDEN_KEY_NUTRI_REMIND_DAY,
    GARDEN_KEY_PLANTED_DAY,
    GARDEN_KEY_PUMP_LEVEL,
)

_LOGGER = logging.getLogger(__name__)


class AerogardenSensor(AerogardenEntity, SensorEntity):
    def __init__(
        self,
        config_id: int,
        coordinator: AerogardenDataUpdateCoordinator,
        field: str,
        label: str,
        icon: str,
        unit: str,
    ) -> None:
        super().__init__(coordinator, config_id, field, label, icon)
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = self._aerogarden.get_garden_property(
            self._config_id, self._field
        )

        _LOGGER.info("Initialized aerogarden sensor %s:\n%s", field, vars(self))

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self._aerogarden.get_garden_property(
            self._config_id, self._field
        )
        self.async_write_ha_state()
        _LOGGER.debug(
            "%s._attr_native_value updated to %s",
            self._attr_unique_id,
            self._attr_native_value,
        )


class AerogardenEnumSensor(AerogardenEntity, SensorEntity):
    def __init__(
        self,
        config_id: int,
        coordinator: AerogardenDataUpdateCoordinator,
        field: str,
        label: str,
        icon: str,
        enums: dict,
    ) -> None:
        super().__init__(coordinator, config_id, field, label, icon)

        self._enums = enums
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = list(enums.values())
        self._attr_native_value = self._enums[self.__get_integer_native_value()]
        _LOGGER.info("Initialized aerogarden enum sensor %s:\n%s", field, vars(self))

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self._enums[self.__get_integer_native_value()]
        self.async_write_ha_state()
        _LOGGER.debug(
            "%s._attr_native_value updated to %s",
            self._attr_unique_id,
            self._attr_native_value,
        )

    def __get_integer_native_value(self):
        return self._aerogarden.get_garden_property(self._config_id, self._field)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    coordinator: AerogardenDataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]

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

    for config_id in coordinator.aerogarden.get_garden_config_ids():
        _LOGGER.info("setting up sensors for  %s", config_id)
        for field, field_def in sensor_fields.items():
            sensors.append(
                AerogardenSensor(
                    config_id,
                    coordinator,
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
                    coordinator,
                    enum_field,
                    enum_def["label"],
                    enum_def["icon"],
                    enum_def["enums"],
                )
            )

    add_entities_callback(sensors)
