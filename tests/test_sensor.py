from asyncio import Future
from typing import Union, cast
from unittest.mock import AsyncMock, MagicMock, NonCallableMagicMock

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from pytest_mock import MockFixture

from custom_components.aerogarden import (
    AerogardenDataUpdateCoordinator,
    AerogardenEntity,
)
from custom_components.aerogarden.aerogarden import Aerogarden
from custom_components.aerogarden.const import (
    DOMAIN,
    GARDEN_KEY_NUTRI_REMIND_DAY,
    GARDEN_KEY_PLANTED_DAY,
    GARDEN_KEY_PUMP_LEVEL,
)
from custom_components.aerogarden.sensor import (
    AerogardenSensor,
    async_setup_entry,
)

MockType = Union[
    MagicMock,
    AsyncMock,
    NonCallableMagicMock,
]
CONFIG_ID = 123456
# noinspection SpellCheckingInspection
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
        self._added_entities: list[AerogardenEntity] = []

    def add_entities_callback(
        self,
        new_entities: list[AerogardenEntity],
    ):
        self._added_entities = new_entities


@pytest.fixture
def setup(mocker: MockFixture):
    future: Future = Future()
    future.set_result(None)

    mocker.patch.object(HomeAssistant, "__init__", return_value=None)
    write_ha_mock = mocker.patch.object(
        Entity, "async_write_ha_state", return_value=None
    )

    ag_service = Aerogarden(HOST, EMAIL, PASSWORD)
    mocker.patch.object(ag_service, "update", return_value=future)

    ag_service._data = {CONFIG_ID: DEVICES[0]}

    hass = HomeAssistant("/path")
    coordinator = AerogardenDataUpdateCoordinator(hass, ag_service, 10)

    hass.data = {DOMAIN: {ENTRY_ID: coordinator}}

    config_entry = ConfigEntry(
        entry_id=ENTRY_ID,
        data={CONF_EMAIL: "unittest@ha.com"},
        domain=DOMAIN,
        minor_version=0,
        source="",
        title="",
        version=0,
    )

    entities = EntitiesTracker()

    return hass, config_entry, entities, write_ha_mock


@pytest.mark.asyncio
class TestSensor:
    @staticmethod
    async def __execute_and_get_sensor(setup, garden_key: str) -> AerogardenSensor:
        entities: EntitiesTracker
        (hass, configEntry, entities, _) = setup

        await async_setup_entry(hass, configEntry, entities.add_entities_callback)

        found = [
            cast(AerogardenSensor, sensor)
            for sensor in entities._added_entities
            if garden_key in sensor.unique_id
        ]
        assert len(found) == 1

        return found[0]

    async def test_async_setup_all_sensors_created(self, setup):
        """All sensors created"""
        entities: EntitiesTracker
        (hass, configEntry, entities, _) = setup

        await async_setup_entry(hass, configEntry, entities.add_entities_callback)

        assert len(entities._added_entities) == 3

    async def test_async_setup_entry_planted_day_created(self, setup):
        """Sensor for how many days since the garden was first planted is created on setup"""

        sensor = await self.__execute_and_get_sensor(setup, GARDEN_KEY_PLANTED_DAY)

        assert sensor.entity_description.translation_key == "planted_days"
        assert sensor.entity_description.icon == "mdi:calendar"
        assert sensor.entity_description.device_class == SensorDeviceClass.DURATION
        assert sensor.entity_description.unit_of_measurement == UnitOfTime.DAYS
        assert sensor.device_info is not None
        assert sensor.aerogarden is not None
        assert sensor.native_value == 43

    async def test_async_setup_entry_nutrient_days_created(self, setup):
        """Sensor for how many days left in the current nutrient cycle is created on setup"""

        sensor = await self.__execute_and_get_sensor(setup, GARDEN_KEY_NUTRI_REMIND_DAY)

        assert sensor.entity_description.translation_key == "nutrient_days"
        assert sensor.entity_description.icon == "mdi:calendar-clock"
        assert sensor.entity_description.device_class == SensorDeviceClass.DURATION
        assert sensor.entity_description.unit_of_measurement == UnitOfTime.DAYS
        assert sensor.device_info is not None
        assert sensor.aerogarden is not None
        assert sensor.native_value == 6

    async def test_async_setup_entry_pump_level_created(self, setup):
        """Sensor for the current reservoir water level is created on setup"""

        sensor = await self.__execute_and_get_sensor(setup, GARDEN_KEY_PUMP_LEVEL)

        assert sensor.entity_description.translation_key == "pump_level"
        assert sensor.entity_description.icon == "mdi:water-percent"
        assert sensor.entity_description.device_class == SensorDeviceClass.ENUM
        assert sensor.device_info is not None
        assert sensor.aerogarden is not None
        assert sensor.native_value == "Medium"

    @pytest.mark.parametrize(
        "field",
        [
            GARDEN_KEY_PLANTED_DAY,
            GARDEN_KEY_NUTRI_REMIND_DAY,
            GARDEN_KEY_PUMP_LEVEL,
        ],
    )
    async def test_async_handle_coordinator_update(self, setup, field):
        """Sensor for if the garden pump is on is created on setup"""

        write_ha_mock: MockType
        (_, _, _, write_ha_mock) = setup
        sensor = await self.__execute_and_get_sensor(setup, field)
        sensor._handle_coordinator_update()

        write_ha_mock.assert_called()
