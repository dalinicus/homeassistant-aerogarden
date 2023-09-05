import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_mock import MockFixture
from pytest_mock.plugin import MockType

from custom_components.aerogarden.aerogarden import Aerogarden
from custom_components.aerogarden.client import AerogardenClient
from custom_components.aerogarden.const import (
    DOMAIN,
    GARDEN_KEY_CONFIG_ID,
    GARDEN_KEY_GARDEN_TYPE,
    MANUFACTURER,
)

HOST = "https://unittest.abcxyz"
EMAIL = "myemail@unittest.com"
PASSWORD = "hunter2"

CONFIG_ID = 123456
MAC_ADDR = "12:34:56:78:10:AB"
DEVICES = [
    {
        "configID": CONFIG_ID,
        "airGuid": "12:98:56:AB:E0:AB",
        "plantedName": "V2UndmUgQmVlbiBUcnlpbmcgVG8gUmVhY2ggWW91IEFib3V0IFlvdXIgQ2FyJ3MgRXh0ZW5kZWQgV2FycmFudHk=",
        "chooseGarden": 0,
    },
    {
        "airGuid": "54:34:56:78:10:CD",
        "configID": CONFIG_ID + 1,
        "chooseGarden": 0,
        "plantedName": "VW5pdCBUZXN0IEdhcmRlbg==",
    },
    {
        "airGuid": "98:34:56:78:10:3F",
        "configID": CONFIG_ID + 2,
        "chooseGarden": 0,
        "plantedName": "VGhpcyBUZXN0IFNoYWxsIFBhc3M=",
    },
    {
        "airGuid": "98:34:56:78:10:3F",
        "configID": CONFIG_ID + 3,
        "chooseGarden": 1,
        "plantedName": "VGhpcyBUZXN0IFNoYWxsIFBhc3M=",
        "swVersion": "MFW-V0.20",
    },
    {
        "configID": CONFIG_ID + 4,
        "airGuid": MAC_ADDR,
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
    },
]

DATA = {
    DEVICES[0]["configID"]: DEVICES[0],
    DEVICES[1]["configID"]: DEVICES[1],
    DEVICES[2]["configID"]: DEVICES[2],
    DEVICES[3]["configID"]: DEVICES[3],
    DEVICES[4]["configID"]: DEVICES[4],
}


@pytest.mark.asyncio
class TestAerogarden:
    async def test_get_garden_config_ids_returns_ids(self):
        """get_garden_config_ids returns ids for all gardens on account"""

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        aerogarden._data = DATA

        ids = aerogarden.get_garden_config_ids()
        assert len(ids) == 5
        assert CONFIG_ID in ids
        assert CONFIG_ID + 1 in ids
        assert CONFIG_ID + 2 in ids
        assert CONFIG_ID + 3 in ids
        assert CONFIG_ID + 4 in ids

    async def test_get_garden_config_ids_returns_empty_list(self):
        """get_garden_config_ids still returns an empty array when no devices are in the account (or before data has been updated)"""

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)

        ids = aerogarden.get_garden_config_ids()
        assert ids is not None
        assert len(ids) == 0

    async def test_get_garden_name_single_garden(self):
        """get_garden_name returns the unencoded garden name for the config id passed. For a single garden, it should be verbadum"""

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        aerogarden._data = DATA

        name = aerogarden.get_garden_name(CONFIG_ID + 1)

        assert name == "Unit Test Garden"

    @pytest.mark.parametrize("index,suffix", [(2, "Left"), (3, "Right")])
    async def test_get_garden_name_multi_garden(self, index, suffix):
        """get_garden_name returns the unencoded garden name for the config id passed. For a multi garden, it should be suffixed
        with either left or right
        """

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        aerogarden._data = DATA

        name = aerogarden.get_garden_name(CONFIG_ID + index)

        assert name == f"This Test Shall Pass ({suffix})"

    @pytest.mark.parametrize(
        "config_id,field,value",
        [
            (CONFIG_ID + 4, "bwConnectedSsid", "Pretty Fly for a Wifi"),
            (CONFIG_ID + 4, "swVersion", "MFW-V0.37"),
            (CONFIG_ID + 3, "swVersion", "MFW-V0.20"),
        ],
    )
    async def test_get_property_returns_property(self, config_id, field, value):
        """get_property should return the correct value for the given config_id"""

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        aerogarden._data = DATA

        result = aerogarden.get_garden_property(config_id, field)
        assert value == result

    @pytest.mark.parametrize(
        "field, config_id",
        [(GARDEN_KEY_CONFIG_ID, "232161"), ("MyFakeField", CONFIG_ID)],
    )
    async def test_get_device_property_returns_null_properly(self, field, config_id):
        """the absence of a value should return None instead of keyerror"""
        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        aerogarden._data = DATA

        result = aerogarden.get_garden_property(config_id, field)
        assert result is None

    async def test_update_logged_in_should_not_be_called_if_not_necessary(
        self, mocker: MockFixture
    ):
        """if client is already logged in, than log in should not be called"""

        mocker.patch.object(AerogardenClient, "is_logged_in", return_value=False)
        mocker.patch.object(AerogardenClient, "get_user_devices", return_value=DEVICES)
        mockLogin: MockType = mocker.patch.object(AerogardenClient, "login")

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        await aerogarden.update()

        assert mockLogin.called

    async def test_update_logged_in_should_called_if_not_logged_in(
        self, mocker: MockFixture
    ):
        """if client is not already logged in, than log in should be called"""

        mocker.patch.object(AerogardenClient, "is_logged_in", return_value=True)
        mocker.patch.object(AerogardenClient, "get_user_devices", return_value=DEVICES)
        mockLogin: MockType = mocker.patch.object(AerogardenClient, "login")

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        await aerogarden.update()

        assert not mockLogin.called

    async def test_update_data_set(self, mocker: MockFixture):
        """data should be set once update is called"""

        mocker.patch.object(AerogardenClient, "is_logged_in", return_value=True)
        mocker.patch.object(AerogardenClient, "get_user_devices", return_value=DEVICES)
        mocker.patch.object(AerogardenClient, "login")

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        await aerogarden.update()

        assert len(aerogarden._data) == 5

    async def test_update_update_failed_trhwon(self, mocker: MockFixture):
        mocker.patch.object(AerogardenClient, "is_logged_in", return_value=True)
        mocker.patch.object(
            AerogardenClient,
            "get_user_devices",
            return_value=DEVICES,
            side_effect=Exception("unit test"),
        )
        mocker.patch.object(AerogardenClient, "login")

        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        with pytest.raises(UpdateFailed):
            await aerogarden.update()

    @pytest.mark.parametrize(
        "garden_type,expected_model",
        [(5, "Aerogarden Bounty"), (3, "Aerogarden Type 3")],
    )
    async def test_ac_infinity_device_has_correct_device_info(
        self, garden_type: int, expected_model: str
    ):
        """getting device returns an model object that contains correct device info for the device registry"""
        aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
        aerogarden._data = DATA
        aerogarden._data[CONFIG_ID + 4][GARDEN_KEY_GARDEN_TYPE] = garden_type

        device_info = aerogarden.get_device_info(CONFIG_ID + 4)

        assert device_info
        assert (DOMAIN, MAC_ADDR) in device_info.get("identifiers")
        assert device_info.get("hw_version") == "SW-V1.01"
        assert device_info.get("sw_version") == "MFW-V0.37"
        assert device_info.get("name") == "( ͡° ͜ʖ ͡°) Hello there"
        assert device_info.get("manufacturer") == MANUFACTURER
        assert device_info.get("model") == expected_model
