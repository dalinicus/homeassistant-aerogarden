import logging
import aiohttp
import async_timeout
import json

from homeassistant.exceptions import HomeAssistantError
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

API_URL_LOGIN = "/api/Admin/Login"
API_URL_QUERY_USER_DEVICE = "/api/CustomData/QueryUserDevice"
API_URL_UPDATE_DEVICE_CONFIG = "/api/Custom/UpdateDeviceConfig"

class AerogardenClient:
    def __init__(self, host):
        self._host = host

        with open('manifest.json') as file:
            manifest = json.load(file)
            
        self._headers = {
            "User-Agent": f"HA-{DOMAIN}/{manifest['version']}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    
    def login(self, username:str, password:str):
        """Log into the Aerogarden client using the given credentials, then store the resulting userId"""
        url = f"{self._host}{API_URL_LOGIN}"
        post_data = f"mail={username}&userPwd={password}"

        _LOGGER.debug(f"POST - {url}, post data: {self.__clean_password(str(post_data), password)}, headers: {self._headers}")
        response = self.__post(url, post_data, self._headers)

        code = response["code"]
        if code <= 0:
            if code == -4:
                raise AerogardenApiAuthError("User credentials provided are invalid.")
            elif code == -2:
                raise AerogardenApiAuthError("User account does not exist.")
            else:
                raise AerogardenApiAuthError("Login Failed.")
            
        self._user_id = code        
    
    def get_user_devices(self):
        """Get a list of device configurations. Requires client to be logged in."""
        if self._user_id <= 0:
            raise AerogardenApiConnectError("Aerogarden client is not logged in.")
        
        url = f"{self._host}{API_URL_LOGIN}"
        post_data = f"userID={self._user_id}"
    
        _LOGGER.debug(f"POST - url: {url}, post data: {post_data}, headers: {self._headers}")
        return self.__post(url, post_data, self._headers)


    def update_device_config(self, airGuid:str, chooseGarden:int, plantConfig:str):
        """Update a garden config using a given plant config patch document. Requires client to be logged in."""
        if self._user_id <= 0:
            raise AerogardenApiConnectError("Aerogarden client is not logged in.")
        
        url = f"{self._host}{API_URL_LOGIN}"
        post_data = f"userID={self._user_id}&airGuid={airGuid}&chooseGarden={chooseGarden}&plantConfig={plantConfig}"

        _LOGGER.debug(f"POST - url: {url}, post data: {post_data}, headers: {self._headers}")
        response = self.__post(url, post_data, self._headers)

        if response["code"] <= 0:
            raise AerogardenApiError("Patching device config was not successful.")
    
    def __clean_password(text, password):
        """cleanPassword assumes there is one or zero instances of password in the text
        Replaces the password with <password>
        """
        password_length = len(password)
        if password_length == 0:
            return text
        replace_text = "<password>"
        for i in range(len(text) + 1 - password_length):
            if text[i : (i + password_length)] == password:
                rest_of_string = text[(i + password_length) :]
                text = text[:i] + replace_text + rest_of_string
                break
        return text
    
    async def __post(self, path, post_data):
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession(raise_for_status=False, headers=self._headers) as session:
                async with session.post(f"{self._host}/{path}", data=post_data) as response:
                    if response.status != 200:
                        raise AerogardenApiConnectError(f"HTTP Request was unsuccessful with a status code {response.status}")
                    
                    return await response.json()

class AerogardenApiError(HomeAssistantError):
    """Error thrown to indicate request was successful but the Aerogarden API returned an error"""

class AerogardenApiConnectError(HomeAssistantError):
    """Error to indicate troubles connecting to the Aerogarden API"""

class AerogardenApiAuthError(HomeAssistantError):
    """Error to indicate authentication or authorization issues with the Aerogarden API"""