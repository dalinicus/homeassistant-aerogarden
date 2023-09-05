import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .aerogarden import Aerogarden
from .const import DOMAIN, HOST, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the aerogarden platform from a config entry."""
    _LOGGER.info("Initializing aerogarden platform for %(entry_id)s", entry.entry_id)

    aerogarden = Aerogarden(HOST, entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD])
    await aerogarden.update()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = aerogarden

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading aerogarden platform for %(entry_id)s", entry.entry_id)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
