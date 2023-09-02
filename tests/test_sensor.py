from asyncio import Future

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from pytest_mock import MockFixture

from custom_components.aerogarden.aerogarden import Aerogarden
from custom_components.aerogarden.const import (
    DOMAIN,
    GARDEN_KEY_NUTRI_REMIND_DAY,
    GARDEN_KEY_PLANTED_DAY,
    GARDEN_KEY_PUMP_LEVEL,
)
from custom_components.aerogarden.sensor import (
    AerogardenEnumSensor,
    AerogardenSensor,
    AerogardenSensorBase,
    async_setup_entry,
)

CONFIG_ID = 123456
DEVICES = [
    {
        "configID": CONFIG_ID,
        "airGuid": "12:34:56:78:10:AB",
        "lightCycle": "08000801",
        "pumpCycle": "00050019",
        "lightTemp": 1,
        "lightStat": 0,
        "clock": "0a0006",
        "pumpStat": 1,
        "pumpHydro": 0,
        "pumpTest": None,
        "pumpDrain": None,
        "pumpDrainState": None,
        "pumpLevel": 1,
        "pumpRemind4Hour": 0,
        "gardenType": 5,
        "plantedType": 10,
        "plantedName": "KCDNocKwIM2cypYgzaHCsCkgSGVsbG8gdGhlcmU=",
        "totalDay": 120,
        "plantedDay": 43,
        "nutriCycle": 7,
        "nutriRemindDay": 6,
        "nutriStatus": 0,
        "alarmAllow": 0,
        "plantedDate": None,
        "nutrientDate": None,
        "updateDate": "2023-08-25T00:27:24",
        "createDate": None,
        "swVersion": "MFW-V0.37",
        "hwVersion": "SW-V1.01",
        "bwVersion": "HW-V5.0",
        "oldPlantedDay": 43,
        "deviceID": "123456789ABCEFG",
        "deviceIP": "http://10.10.2.20",
        "chooseGarden": 0,
        "oldlightCycle": "",
        "vacationMode": 0,
        "bwConnectedSsid": "Pretty Fly for a Wifi",
        "nutriStatusFlag": "0",
        "nutriStatusDate": "2023-08-23T14:05:02",
        "remark": None,
        "imgUrl": None,
        "timezone": "0",
        "audioAlarmStat": 0,
        "audioAlarmCycle": "08001400",
        "audioAlarmCycleSet": 0,
        "clientIP": "555.55.55.5",
        "latlng": None,
        "lightDimming": 0,
        "sunRise": 0,
        "sunSet": 0,
        "sunFunStatus": 0,
        "sunFunSwitch": 0,
        "pumpSafetyMode": 0,
    }
]
HOST = "https://unittest.abcxyz"
EMAIL = "myemail@unittest.com"
PASSWORD = "hunter2"
ENTRY_ID = f"aerogarden-{EMAIL}"


class EntitiesTracker:
    def __init__(self) -> None:
        self._added_entities: list[AerogardenSensorBase] = []

    def add_entities_callback(
        self,
        new_entities: list[AerogardenSensorBase],
        update_before_add: bool = False,
    ):
        self._added_entities = new_entities


@pytest.fixture
def setup(mocker: MockFixture):
    future: Future = Future()
    future.set_result(None)

    mocker.patch.object(Aerogarden, "update", return_value=future)
    mocker.patch.object(ConfigEntry, "__init__", return_value=None)
    mocker.patch.object(HomeAssistant, "__init__", return_value=None)

    aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
    aerogarden._data = {CONFIG_ID: DEVICES[0]}

    hass = HomeAssistant()
    hass.data = {DOMAIN: {ENTRY_ID: aerogarden}}

    configEntry = ConfigEntry()
    configEntry.entry_id = ENTRY_ID

    entities = EntitiesTracker()

    return (hass, configEntry, entities)


@pytest.mark.asyncio
class TestSensor:
    async def __execute_and_get_sensor(
        self, setup, garden_key: str
    ) -> AerogardenSensorBase:
        entities: EntitiesTracker
        (hass, configEntry, entities) = setup

        await async_setup_entry(hass, configEntry, entities.add_entities_callback)

        found = [
            sensor
            for sensor in entities._added_entities
            if garden_key in sensor._attr_unique_id
        ]
        assert len(found) == 1

        return found[0]

    async def test_async_setup_all_sensors_created(self, setup):
        """All sensors created"""
        entities: EntitiesTracker
        (hass, configEntry, entities) = setup

        await async_setup_entry(hass, configEntry, entities.add_entities_callback)

        assert len(entities._added_entities) == 3

    async def test_async_setup_entry_planted_day_created(self, setup):
        """Sensor for how many days since the garden was first planeted is created on setup"""

        sensor = await self.__execute_and_get_sensor(setup, GARDEN_KEY_PLANTED_DAY)

        assert "Planted Days" in sensor._attr_name
        assert sensor._attr_icon == "mdi:calendar"
        assert sensor._attr_native_unit_of_measurement == UnitOfTime.DAYS

    async def test_async_update_planted_day_value_Correct(self, setup):
        """Reported sensor value matches the value in the json payload"""

        sensor: AerogardenSensor = await self.__execute_and_get_sensor(
            setup, GARDEN_KEY_PLANTED_DAY
        )
        await sensor.async_update()

        assert sensor._attr_native_value == 43

    async def test_async_setup_entry_nutrient_days_created(self, mocker, setup):
        """Sensor for how many days left in the current nutrient cycle is created on setup"""

        sensor = await self.__execute_and_get_sensor(setup, GARDEN_KEY_NUTRI_REMIND_DAY)

        assert "Nutrient Days" in sensor._attr_name
        assert sensor._attr_icon == "mdi:calendar-clock"
        assert sensor._attr_native_unit_of_measurement == UnitOfTime.DAYS

    async def test_async_update_nutrient_day_value_Correct(self, setup):
        """Reported sensor value matches the value in the json payload"""

        sensor: AerogardenSensor = await self.__execute_and_get_sensor(
            setup, GARDEN_KEY_NUTRI_REMIND_DAY
        )
        await sensor.async_update()

        assert sensor._attr_native_value == 6

    async def test_async_setup_entry_pump_level_created(self, mocker, setup):
        """Sensor for the current reservoir water level is created on setup"""

        sensor = await self.__execute_and_get_sensor(setup, GARDEN_KEY_PUMP_LEVEL)

        assert "Pump Level" in sensor._attr_name
        assert sensor._attr_icon == "mdi:water-percent"
        assert sensor._attr_device_class == SensorDeviceClass.ENUM

    @pytest.mark.parametrize(
        "pump_level,expected_enum",
        [
            (2, "Full"),
            (1, "Medium"),
            (0, "Low"),
        ],
    )
    async def test_async_update_pump_level_value_Correct(
        self, setup, pump_level, expected_enum
    ):
        """Reported sensor value matches the value in the json payload"""
        DEVICES[0]["pumpLevel"] = pump_level

        sensor: AerogardenEnumSensor = await self.__execute_and_get_sensor(
            setup, GARDEN_KEY_PUMP_LEVEL
        )
        await sensor.async_update()

        assert sensor._attr_native_value == expected_enum
