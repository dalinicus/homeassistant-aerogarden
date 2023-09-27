import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.aerogarden import (
    AerogardenDataUpdateCoordinator,
    AerogardenEntity,
)

from .const import (
    DOMAIN,
    GARDEN_KEY_LIGHT_STAT,
    GARDEN_KEY_NUTRI_STATUS,
    GARDEN_KEY_PUMP_HYDRO,
    GARDEN_KEY_PUMP_STAT,
)

_LOGGER = logging.getLogger(__name__)


class AerogardenBinarySensor(AerogardenEntity, BinarySensorEntity):
    def __init__(
        self,
        config_id: int,
        coordinator: AerogardenDataUpdateCoordinator,
        field: str,
        label: str,
        icon: str,
        device_class: str,
    ) -> None:
        super().__init__(coordinator, config_id, field, label, icon)
        self._attr_device_class = device_class
        self._attr_is_on = (
            self._aerogarden.get_garden_property(self._config_id, self._field) == 1
        )
        _LOGGER.info("Initialized aerogarden binary sensor %s:\n%s", field, vars(self))

    @callback
    def _handle_coordinator_update(self) -> None:
        self._aerogarden.get_garden_property(self._config_id, self._field) == 1
        self.async_write_ha_state()
        _LOGGER.debug(
            "%s._attr_is_on updated to %s", self._attr_unique_id, self._attr_is_on
        )


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    coordinator: AerogardenDataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]

    sensors = []
    sensor_fields = {
        GARDEN_KEY_PUMP_STAT: {
            "label": "Pump",
            "deviceClass": BinarySensorDeviceClass.RUNNING,
            "icon": "mdi:water-pump",
        },
        GARDEN_KEY_NUTRI_STATUS: {
            "label": "Needs Nutrients",
            "deviceClass": BinarySensorDeviceClass.PROBLEM,
            "icon": "mdi:cup-water",
        },
        GARDEN_KEY_PUMP_HYDRO: {
            "label": "Needs Water",
            "deviceClass": BinarySensorDeviceClass.PROBLEM,
            "icon": "mdi:water",
        },
        GARDEN_KEY_LIGHT_STAT: {
            "label": "Light",
            "deviceClass": None,
            "icon": "mdi:lightbulb",
        },
    }

    for config_id in coordinator.aerogarden.get_garden_config_ids():
        _LOGGER.info("setting up binary sensors for %s", config_id)
        for field, field_def in sensor_fields.items():
            sensors.append(
                AerogardenBinarySensor(
                    config_id,
                    coordinator,
                    field,
                    field_def["label"],
                    field_def["icon"],
                    field_def["deviceClass"],
                )
            )

    add_entities_callback(sensors)
