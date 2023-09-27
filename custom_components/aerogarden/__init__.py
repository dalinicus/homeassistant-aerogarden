import logging
from datetime import timedelta

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .aerogarden import Aerogarden
from .const import (
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    HOST,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the aerogarden platform from a config entry."""
    _LOGGER.info("Initializing aerogarden platform for %(entry_id)s", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})
    polling_interval = (
        int(entry.data[CONF_POLLING_INTERVAL])
        if CONF_POLLING_INTERVAL in entry.data
        else DEFAULT_POLLING_INTERVAL
    )

    aerogarden = Aerogarden(HOST, entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD])
    coordinator = AerogardenDataUpdateCoordinator(hass, aerogarden, polling_interval)

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading aerogarden platform for %(entry_id)s", entry.entry_id)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AerogardenDataUpdateCoordinator(DataUpdateCoordinator):
    """Handles updating data for the integration"""

    def __init__(self, hass, aerogarden: Aerogarden, polling_interval: int):
        """Constructor"""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

        self._aerogarden = aerogarden

    async def _async_update_data(self):
        """Fetch data from the Aerogarden API"""
        _LOGGER.debug("Refreshing data from data update coordinator")
        try:
            async with async_timeout.timeout(10):
                await self._aerogarden.update()
                return self._aerogarden
        except Exception as e:
            _LOGGER.error("Unable to refresh from data update coordinator", exc_info=e)
            raise UpdateFailed from e

    @property
    def aerogarden(self) -> Aerogarden:
        return self._aerogarden


class AerogardenEntity(CoordinatorEntity):
    def __init__(
        self,
        coordinator: AerogardenDataUpdateCoordinator,
        config_id: int,
        field: str,
        label: str,
        icon: str,
    ):
        super().__init__(coordinator)
        self._aerogarden: Aerogarden = coordinator.aerogarden
        self._config_id: int = config_id
        self._field: str = field
        self._label: str = label
        self._garden_name: str = self._aerogarden.get_garden_name(config_id)

        self._attr_device_info = self._aerogarden.get_device_info(config_id)
        self._attr_name = f"{self._garden_name} {label}"
        self._attr_unique_id = f"{DOMAIN}-{self._config_id}-{field}"
        self._attr_icon = icon
