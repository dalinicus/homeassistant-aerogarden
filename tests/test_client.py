import pytest
from aioresponses import aioresponses

from custom_components.aerogarden.client import (
    AerogardenClient,
    AerogardenApiConnectError,
    AerogardenApiAuthError,
    API_URL_LOGIN,
    API_URL_QUERY_USER_DEVICE,
    API_URL_UPDATE_DEVICE_CONFIG,
)

HOST = "https://unittest.abcxyz"
EMAIL = "myemail@unittest.com"
PASSWORD = "hunter2"

USER_ID = 123456
CONFIG_ID = 987654
AIR_GUID = "12:34:56:78:10:AB"
CHOOSE_GARDEN = (0,)
PLANT_CONFIG = '{{ "lightTemp": 1 }}'

DEVICES_PAYLOAD = [
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


@pytest.mark.asyncio
class TestClient:
    async def test_is_logged_in_returns_false_if_not_logged_in(self):
        """when a client has not been logged in, is_logged_in should return false"""
        client = AerogardenClient(HOST, EMAIL, PASSWORD)

        assert client.is_logged_in() is False

    async def test_is_logged_in_returns_true_if_logged_in(self):
        """when a client has not been logged in, is_logged_in should return false"""

        client = AerogardenClient(HOST, EMAIL, PASSWORD)
        client._user_id = USER_ID

        assert client.is_logged_in() is True

    async def test_login_user_id_set_on_success(self):
        """When login is called and is successful, the user id to make future requests should be set"""

        with aioresponses() as mocked:
            mocked.post(
                f"{HOST}{API_URL_LOGIN}",
                status=200,
                payload={"code": USER_ID, "msg": "用户登陆成功。"},
            )

            client = AerogardenClient(HOST, EMAIL, PASSWORD)
            await client.login()

            assert client._user_id > 0

    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500])
    async def test_login_api_connect_error_raised_on_http_error(self, status_code):
        """When login is called and returns a non-succesful status code, connect error should be raised"""

        with aioresponses() as mocked:
            mocked.post(
                f"{HOST}{API_URL_LOGIN}",
                status=status_code,
                payload={
                    "Message": "This is a unit test error message",
                    "MessageDetail": "This is a unit test error detail",
                },
            )

            client = AerogardenClient(HOST, EMAIL, PASSWORD)
            with pytest.raises(AerogardenApiConnectError):
                await client.login()

    @pytest.mark.parametrize("code", [-4, -2, -1])
    async def test_login_api_auth_error_on_failed_login(self, code):
        """When login is called and returns a non-succesful status code, connect error should be raised"""

        with aioresponses() as mocked:
            mocked.post(
                f"{HOST}{API_URL_LOGIN}",
                status=200,
                payload={"code": code, "msg": "账号不存在，登陆失败。"},
            )

            client = AerogardenClient(HOST, EMAIL, PASSWORD)
            with pytest.raises(AerogardenApiAuthError):
                await client.login()

    async def test_get_user_devices_returns_user_devices(self):
        """When logged in, user devices should return a list of user devices"""
        client = AerogardenClient(HOST, EMAIL, PASSWORD)
        client._user_id = USER_ID

        with aioresponses() as mocked:
            mocked.post(
                f"{HOST}{API_URL_QUERY_USER_DEVICE}",
                status=200,
                payload=DEVICES_PAYLOAD,
            )

            result = await client.get_user_devices()

            assert result is not None
            assert result[0]["configID"] == 987654

    async def test_get_user_devices_connect_error_on_not_logged_in(self):
        """When not logged in, get user devices should throw a connect error"""
        client = AerogardenClient(HOST, EMAIL, PASSWORD)
        with pytest.raises(AerogardenApiConnectError):
            await client.get_user_devices()

    async def test_update_device_config(self):
        """When logged in, user devices should return a list of user devices"""
        client = AerogardenClient(HOST, EMAIL, PASSWORD)
        client._user_id = USER_ID

        with aioresponses() as mocked:
            mocked.post(
                f"{HOST}{API_URL_UPDATE_DEVICE_CONFIG}",
                status=200,
                payload={"code": 1, "msg": ""},
            )

            await client.update_device_config(AIR_GUID, CHOOSE_GARDEN, PLANT_CONFIG)

            mocked.assert_called_with(
                f"{HOST}{API_URL_UPDATE_DEVICE_CONFIG}",
                method="POST",
                data={
                    "userID": USER_ID,
                    "airGuid": AIR_GUID,
                    "chooseGarden": CHOOSE_GARDEN,
                    "plantConfig": PLANT_CONFIG,
                },
            )

    async def test_update_device_config_connect_error_on_not_logged_in(self):
        """When not logged in, get user devices should throw a connect error"""

        client = AerogardenClient(HOST, EMAIL, PASSWORD)
        with pytest.raises(AerogardenApiConnectError):
            await client.update_device_config(AIR_GUID, CHOOSE_GARDEN, PLANT_CONFIG)
