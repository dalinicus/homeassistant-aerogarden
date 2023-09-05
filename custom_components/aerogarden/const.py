"""Constants for the Aerogarden integration."""
from homeassistant.const import Platform

MANUFACTURER = "Aerogarden"
DOMAIN = "aerogarden"
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]
USER_AGENT_VERSION = "1.0.0"
DEFAULT_HOST = "https://app3.aerogarden.com:8443"

GARDEN_KEY_USER_ID = "userID"
GARDEN_KEY_CONFIG_ID = "configID"
GARDEN_KEY_CHOOSE_GARDEN = "chooseGarden"
GARDEN_KEY_AIR_GUID = "airGuid"
GARDEN_KEY_PLANTED_NAME = "plantedName"
GARDEN_KEY_LIGHT_TEMP = "lightTemp"
GARDEN_KEY_LIGHT_STAT = "lightStat"
GARDEN_KEY_PLANT_CONFIG = "plantConfig"
GARDEN_KEY_PLANTED_DAY = "plantedDay"
GARDEN_KEY_NUTRI_REMIND_DAY = "nutriRemindDay"
GARDEN_KEY_PUMP_LEVEL = "pumpLevel"
GARDEN_KEY_PUMP_STAT = "pumpStat"
GARDEN_KEY_PUMP_HYDRO = "pumpHydro"
GARDEN_KEY_NUTRI_STATUS = "nutriStatus"
GARDEN_KEY_HW_VERSION = "hwVersion"
GARDEN_KEY_SW_VERSION = "swVersion"

GARDEN_KEY_EMAIL = "mail"
GARDEN_KEY_PASSWORD = "userPwd"
