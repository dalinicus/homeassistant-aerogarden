import logging

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_EMAIL
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .aerogarden import Aerogarden

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the aerogarden platform from a config entry."""
    _LOGGER.info(f"Initializing aerogarden platform for {entry.entry_id}")

    aerogarden = Aerogarden(
        entry.data[CONF_HOST], entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD]
    )
    await aerogarden.update()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = aerogarden

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info(f"Unloading aerogarden platform for {entry.entry_id}")

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
