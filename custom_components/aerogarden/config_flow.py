"""Config flow for the Aerogarden integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST

from .const import DOMAIN, CONFIG_SCHEMA
from .client import AerogardenClient, AerogardenApiAuthError, AerogardenApiConnectError

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for aerogarden."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                client = AerogardenClient(user_input[CONF_HOST])
                client.login(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
                _ = client.get_user_devices()
            except AerogardenApiConnectError:
                errors["base"] = "cannot_connect"
            except AerogardenApiAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f'aerogarden-{user_input[CONF_USERNAME]}')
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=f'Aerogarden ({user_input[CONF_USERNAME]})', data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )
