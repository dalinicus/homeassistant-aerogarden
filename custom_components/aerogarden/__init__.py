import logging
from datetime import timedelta

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
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
    """Set up the aerogarden platform from a config entry."""
    _LOGGER.info("Initializing aerogarden platform for %(entry_id)s", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})
    polling_interval = (
        int(entry.data[CONF_POLLING_INTERVAL])
        if CONF_POLLING_INTERVAL in entry.data
        else DEFAULT_POLLING_INTERVAL
    )

    ag_service = Aerogarden(HOST, entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD])
    coordinator = AerogardenDataUpdateCoordinator(hass, ag_service, polling_interval)

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


class AerogardenDataUpdateCoordinator(DataUpdateCoordinator[Aerogarden]):
    """Handles updating data for the integration"""

    def __init__(
        self, hass: HomeAssistant, ag_service: Aerogarden, polling_interval: int
    ) -> None:
        """Constructor"""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

        self._aerogarden = ag_service

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


class AerogardenEntity(CoordinatorEntity[AerogardenDataUpdateCoordinator]):
    def __init__(
        self, coordinator: AerogardenDataUpdateCoordinator, config_id: int, key: str
    ) -> None:
        super().__init__(coordinator)
        self._config_id = config_id
        self._key = key

    _attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return f"{DOMAIN}-{self._config_id}-{self._key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about Aerogarden device."""
        return self.coordinator.aerogarden.get_device_info(self._config_id)

    @property
    def aerogarden(self) -> Aerogarden:
        """Returns the underlying aerogarden api object from the assigned coordinator"""
        return self.coordinator.aerogarden
