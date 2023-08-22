import logging
import aiohttp
import async_timeout
import json

from homeassistant.exceptions import HomeAssistantError
from .const import (
    DOMAIN,
    USER_AGENT_VERSION,
    GARDEN_KEY_CHOOSE_GARDEN,
    GARDEN_KEY_AIR_GUID,
    GARDEN_KEY_USERNAME,
    GARDEN_KEY_PASSWORD,
    GARDEN_KEY_PLANT_CONFIG,
    GARDEN_KEY_USER_ID,
)

_LOGGER = logging.getLogger(__name__)

API_URL_LOGIN = "/api/Admin/Login"
API_URL_QUERY_USER_DEVICE = "/api/CustomData/QueryUserDevice"
API_URL_UPDATE_DEVICE_CONFIG = "/api/Custom/UpdateDeviceConfig"


class AerogardenClient:
    def __init__(self, host: str, username: str, password: str) -> None:
        self._host = host
        self._username = username
        self._password = password

        self._user_id = 0
        self._headers = {
            "User-Agent": f"HA-{DOMAIN}/{USER_AGENT_VERSION}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def is_logged_in(self):
        return self._user_id > 0

    async def login(self):
        """Log into the Aerogarden client using the given credentials, then store the resulting userId"""
        response = await self.__post(
            API_URL_LOGIN,
            {
                GARDEN_KEY_USERNAME: self._username,
                GARDEN_KEY_PASSWORD: self._password,
            },
        )

        code = response["code"]
        if code <= 0:
            if code == -4:
                raise AerogardenApiAuthError("User credentials provided are invalid.")
            elif code == -2:
                raise AerogardenApiAuthError("User account does not exist.")
            else:
                raise AerogardenApiAuthError(f"Login Failed.")

        self._user_id = code

    async def get_user_devices(self):
        """Get a list of device configurations. Requires client to be logged in."""
        if not self.is_logged_in():
            raise AerogardenApiConnectError("Aerogarden client is not logged in.")

        return await self.__post(
            API_URL_QUERY_USER_DEVICE, {GARDEN_KEY_USER_ID: self._user_id}
        )

    async def update_device_config(
        self, airGuid: str, chooseGarden: int, plantConfig: str
    ):
        """Update a garden config using a given plant config patch document. Requires client to be logged in."""
        if not self.is_logged_in():
            raise AerogardenApiConnectError("Aerogarden client is not logged in.")

        response = await self.__post(
            API_URL_UPDATE_DEVICE_CONFIG,
            {
                GARDEN_KEY_USER_ID: self._user_id,
                GARDEN_KEY_AIR_GUID: airGuid,
                GARDEN_KEY_CHOOSE_GARDEN: chooseGarden,
                GARDEN_KEY_PLANT_CONFIG: plantConfig,
            },
        )

        if response["code"] <= 0:
            raise AerogardenApiError("Patching device config was not successful.")

    async def __post(self, path, post_data):
        _LOGGER.debug(
            f"POST - {self._host}{path}"
        )

        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession(
                raise_for_status=False, headers=self._headers
            ) as session:
                async with session.post(
                    f"{self._host}{path}", data=post_data
                ) as response:
                    if response.status >= 400:
                        raise AerogardenApiConnectError(
                            f"HTTP Request was unsuccessful with a status code {response.status}"
                        )

                    return await response.json()


class AerogardenApiError(HomeAssistantError):
    """Error thrown to indicate request was successful but the Aerogarden API returned an error"""


class AerogardenApiConnectError(HomeAssistantError):
    """Error to indicate troubles connecting to the Aerogarden API"""


class AerogardenApiAuthError(HomeAssistantError):
    """Error to indicate authentication or authorization issues with the Aerogarden API"""
