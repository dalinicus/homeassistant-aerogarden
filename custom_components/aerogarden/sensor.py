from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
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
    GARDEN_KEY_NUTRI_REMIND_DAY,
    GARDEN_KEY_PLANTED_DAY,
    GARDEN_KEY_PUMP_LEVEL,
)


@dataclass
class AerogardenSensorDescriptionMixin:
    """Mixin for adding required values to entity descriptions"""

    value_fn: Callable[[Aerogarden, int], StateType]


@dataclass
class AerogardenSensorDescription(
    SensorEntityDescription, AerogardenSensorDescriptionMixin
):
    """Describes Aerogarden Sensor Entities."""


WATER_LEVEL_OPTIONS = ["Low", "Medium", "Full"]
SENSOR_DESCRIPTIONS: list[AerogardenSensorDescription] = [
    AerogardenSensorDescription(
        key=GARDEN_KEY_PLANTED_DAY,
        translation_key="planted_days",
        device_class=SensorDeviceClass.DURATION,
        unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:calendar",
        value_fn=lambda aerogarden, config_id: (
            aerogarden.get_garden_property(config_id, GARDEN_KEY_PLANTED_DAY)
        ),
    ),
    AerogardenSensorDescription(
        key=GARDEN_KEY_NUTRI_REMIND_DAY,
        translation_key="nutrient_days",
        device_class=SensorDeviceClass.DURATION,
        unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:calendar-clock",
        value_fn=lambda aerogarden, config_id: (
            aerogarden.get_garden_property(config_id, GARDEN_KEY_NUTRI_REMIND_DAY)
        ),
    ),
    AerogardenSensorDescription(
        key=GARDEN_KEY_PUMP_LEVEL,
        translation_key="pump_level",
        device_class=SensorDeviceClass.ENUM,
        options=WATER_LEVEL_OPTIONS,
        icon="mdi:water-percent",
        value_fn=lambda aerogarden, config_id: (
            WATER_LEVEL_OPTIONS[
                aerogarden.get_garden_property(config_id, GARDEN_KEY_PUMP_LEVEL)
            ]
        ),
    ),
]


class AerogardenSensor(AerogardenEntity, SensorEntity):
    entity_description: AerogardenSensorDescription

    def __init__(
        self,
        coordinator: AerogardenDataUpdateCoordinator,
        description: AerogardenSensorDescription,
        config_id: int,
    ) -> None:
        super().__init__(coordinator, config_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.entity_description.value_fn(self.aerogarden, self._config_id)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, add_entities_callback: AddEntitiesCallback
) -> None:
    coordinator: AerogardenDataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]

    sensors = []
    for config_id in coordinator.aerogarden.get_garden_config_ids():
        for description in SENSOR_DESCRIPTIONS:
            sensors.append(AerogardenSensor(coordinator, description, config_id))

    add_entities_callback(sensors)
