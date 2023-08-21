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
    def __init__(self, config_id:int, aerogarden:Aerogarden, field:str, label:str, device_class:str, icon:str, unit:str):
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
        self._attr_unit_of_measurement = unit

        _LOGGER.debug("Initialized garden sensor %s:\n%s", field, vars(self))

    def update(self):
        self._aerogarden.update()
        self._attr_native_value = self._aerogarden.get_garden_property(self._config_id, self._field)

class AerogardenEnumSensor(SensorEntity):
    def __init__(self, config_id:int, aerogarden:Aerogarden, field:str, label:str, icon:str, enums:dict):
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
        self._attr_options = enums.values()

        _LOGGER.debug("Initialized garden sensor %s:\n%s", field, vars(self))

    def update(self):
        self._aerogarden.update()
        pump_level:int = self._aerogarden.get_garden_property(self._config_id, self._field)
        self._attr_native_value = self._enums[pump_level]

async def async_setup_entry(hass:HomeAssistant, config:ConfigEntry, add_entities_callback:AddEntitiesCallback) -> None:
    aerogarden:Aerogarden = hass.data[DOMAIN][config.entry_id]
    
    sensors = []
    sensor_fields = {
        "plantedDay": {
            "label": "Planted Days", 
            "icon": "mdi:calendar", 
            "deviceClass": SensorDeviceClass.DURATION,
            "unit": UnitOfTime.DAYS
        },
        "nutriRemindDay": {
            "label": "Nutrient Days",
            "icon": "mdi:calendar-clock",
            "deviceClass": SensorDeviceClass.DURATION,
            "unit": UnitOfTime.DAYS
        }
    }

    enum_fields = {
        "pumpLevel": {
            "label": "Pump Level",
            "icon": "mdi:water-percent",
            "enums": {
                0: "Low",
                1: "Medium",
                2: "Full"
            }
        }
    }

    for config_id in aerogarden.get_garden_config_ids():
        for field in sensor_fields.keys():
            sensor_def = sensor_fields[field]
            sensors.append(
                AerogardenSensor(
                    config_id, aerogarden, field, sensor_def["label"], sensor_def["deviceClass"], sensor_def["icon"], sensor_def["unit"]
                )
            )

        for field in enum_fields.keys():
            sensor_def = sensor_fields[field]
            sensors.append(
                AerogardenEnumSensor(
                    config_id, aerogarden, field, sensor_def["label"],  sensor_def["icon"], sensor_def["enums"]
                )
            )
    
    add_entities_callback(sensors)