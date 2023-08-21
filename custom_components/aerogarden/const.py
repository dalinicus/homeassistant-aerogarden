"""Constants for the Aerogarden integration."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import Platform
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST

DOMAIN = "aerogarden"
PLATFORMS = [ 
    Platform.SENSOR, 
    Platform.BINARY_SENSOR, 
    Platform.LIGHT 
]
DEFAULT_HOST = "https://app3.aerogarden.com:8443"
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string
})

GARDEN_KEY_CONFIG_ID = "configID"
GARDEN_KEY_CHOOSE_GARDEN = "chooseGarden"
GARDEN_KEY_AIR_GUID = "airGuid"
GARDEN_KEY_PLANTED_NAME = "plantedName"
GARDEN_KEY_LIGHT_TEMP = "lightTemp"