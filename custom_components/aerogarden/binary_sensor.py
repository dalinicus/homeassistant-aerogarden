from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from custom_components.aerogarden import (
    AerogardenDataUpdateCoordinator,
    AerogardenEntity,
)
from custom_components.aerogarden.aerogarden import Aerogarden

from .const import (
    DOMAIN,
    GARDEN_KEY_LIGHT_STAT,
    GARDEN_KEY_NUTRI_REMIND_DAY,
    GARDEN_KEY_NUTRI_STATUS,
    GARDEN_KEY_PUMP_HYDRO,
    GARDEN_KEY_PUMP_STAT,
)


@dataclass
class AerogardenBinarySensorDescriptionMixin:
    """Mixin for adding required values to entity descriptions"""

    value_fn: Callable[[Aerogarden, int], StateType]


@dataclass
class AerogardenBinarySensorDescription(
    BinarySensorEntityDescription, AerogardenBinarySensorDescriptionMixin
):
    """Describes Aerogarden Sensor Entities."""


SENSOR_DESCRIPTIONS: list[AerogardenBinarySensorDescription] = [
    AerogardenBinarySensorDescription(
        key=GARDEN_KEY_PUMP_STAT,
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:water-pump",
        translation_key="pump_status",
        value_fn=lambda aerogarden, config_id: (
            aerogarden.get_garden_property(config_id, GARDEN_KEY_PUMP_STAT)
        ),
    ),
    AerogardenBinarySensorDescription(
        # Old data key that turned out incorrect. Logic uses a new key, but retained as entity key for backwards compatibility.
        key=GARDEN_KEY_NUTRI_STATUS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:cup-water",
        translation_key="needs_nutrients",
        value_fn=lambda aerogarden, config_id: (
            aerogarden.get_garden_property(config_id, GARDEN_KEY_NUTRI_REMIND_DAY) < 1
        ),
    ),
    AerogardenBinarySensorDescription(
        key=GARDEN_KEY_PUMP_HYDRO,
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:water",
        translation_key="needs_water",
        value_fn=lambda aerogarden, config_id: (
            aerogarden.get_garden_property(config_id, GARDEN_KEY_PUMP_HYDRO)
        ),
    ),
    AerogardenBinarySensorDescription(
        key=GARDEN_KEY_LIGHT_STAT,
        # We want this to read ON or OFF. BinarySensorDeviceClass.Light would result in LIGHT_DETECTED and NO_LIGHT
        device_class=None,
        icon="mdi:lightbulb",
        translation_key="light_status",
        value_fn=lambda aerogarden, config_id: (
            aerogarden.get_garden_property(config_id, GARDEN_KEY_LIGHT_STAT)
        ),
    ),
]


class AerogardenBinarySensor(AerogardenEntity, BinarySensorEntity):
    entity_description: AerogardenBinarySensorDescription

    def __init__(
        self,
        coordinator: AerogardenDataUpdateCoordinator,
        description: AerogardenBinarySensorDescription,
        config_id: int,
    ) -> None:
        super().__init__(coordinator, config_id, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.aerogarden, self._config_id)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    coordinator: AerogardenDataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]

    sensors = []
    for config_id in coordinator.aerogarden.get_garden_config_ids():
        for description in SENSOR_DESCRIPTIONS:
            sensors.append(
                AerogardenBinarySensor(
                    coordinator,
                    description,
                    config_id,
                )
            )

    add_entities_callback(sensors)
