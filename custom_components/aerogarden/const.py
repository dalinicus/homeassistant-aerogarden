"""Constants for the Aerogarden integration."""
from homeassistant.const import Platform

DOMAIN = "aerogarden"
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.LIGHT]
USER_AGENT_VERSION = "1.0.0"
DEFAULT_HOST = "https://app3.aerogarden.com:8443"

GARDEN_KEY_USER_ID = "userID"
GARDEN_KEY_CONFIG_ID = "configID"
GARDEN_KEY_CHOOSE_GARDEN = "chooseGarden"
GARDEN_KEY_AIR_GUID = "airGuid"
GARDEN_KEY_PLANTED_NAME = "plantedName"
GARDEN_KEY_LIGHT_TEMP = "lightTemp"
GARDEN_KEY_PLANT_CONFIG = "plantConfig"

GARDEN_KEY_USERNAME = "mail"
GARDEN_KEY_PASSWORD = "userPwd"
