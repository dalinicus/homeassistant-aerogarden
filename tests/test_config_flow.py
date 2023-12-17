import asyncio
from asyncio import Future
from datetime import timedelta
from unittest.mock import ANY, MagicMock

import pytest
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant, ServiceRegistry
from pytest_mock import MockFixture

from custom_components.aerogarden import AerogardenDataUpdateCoordinator
from custom_components.aerogarden.aerogarden import Aerogarden
from custom_components.aerogarden.client import (
    AerogardenApiAuthError,
    AerogardenApiConnectError,
    AerogardenApiError,
    AerogardenClient,
)
from custom_components.aerogarden.config_flow import (
    CONFIG_SCHEMA,
    ConfigFlow,
    OptionsFlow,
)
from custom_components.aerogarden.const import (
    CONF_POLLING_INTERVAL,
    CONF_UPDATE_PASSWORD,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
)

HOST = "https://unittest.abcxyz"
EMAIL = "myemail@unittest.com"
PASSWORD = "hunter2"

USER_INPUT = {CONF_HOST: HOST, CONF_EMAIL: EMAIL, CONF_PASSWORD: PASSWORD}


@pytest.fixture
def setup_mocks(mocker: MockFixture):
    mocker.patch.object(HomeAssistant, "__init__", return_value=None)
    mocker.patch.object(ConfigEntry, "__init__", return_value=None)

    hass = HomeAssistant("/path")
    aerogarden = Aerogarden(HOST, EMAIL, PASSWORD)
    coordinator = AerogardenDataUpdateCoordinator(hass, aerogarden, 10)

    config_entry = ConfigEntry()
    config_entry.entry_id = "ac_infinity-myemail@unittest.com"
    config_entry.data = {CONF_EMAIL: "unittest@ha.com"}

    hass.data = {DOMAIN: {config_entry.entry_id: coordinator}}

    update_entry = mocker.patch.object(
        config_entries.ConfigEntries, "async_update_entry"
    )

    async_call = mocker.patch.object(ServiceRegistry, "async_call")

    options_flow = OptionsFlow(config_entry)
    options_flow.hass = hass
    options_flow.hass.config_entries = MagicMock()
    options_flow.hass.config_entries.async_update_entry = update_entry
    options_flow.hass.services = MagicMock()
    options_flow.hass.services.async_call = async_call

    return (hass, coordinator, config_entry, options_flow)


@pytest.fixture
def setup_options_flow(mocker: MockFixture):
    future: Future = asyncio.Future()
    future.set_result(None)

    mocker.patch.object(config_entries.OptionsFlow, "async_show_form")
    mocker.patch.object(config_entries.OptionsFlow, "async_show_menu")
    mocker.patch.object(config_entries.OptionsFlow, "async_create_entry")

    return mocker


@pytest.fixture
def setup(mocker: MockFixture):
    future: Future = Future()
    future.set_result(None)

    mocker.patch.object(config_entries.ConfigFlow, "async_show_form")
    mocker.patch.object(config_entries.ConfigFlow, "async_create_entry")
    mocker.patch.object(config_entries.ConfigFlow, "async_set_unique_id")
    mocker.patch.object(config_entries.ConfigFlow, "_abort_if_unique_id_configured")
    mocker.patch.object(AerogardenClient, "login", return_value=future)
    mocker.patch.object(AerogardenClient, "get_user_devices", return_value=future)

    return mocker


@pytest.mark.asyncio
class TestConfigFlow:
    async def test_async_step_user_form_shown(self, setup):
        """When a user hasn't given any input yet, show the form"""

        flow = ConfigFlow()
        await flow.async_step_user()

        flow.async_show_form.assert_called_with(
            step_id="user", data_schema=CONFIG_SCHEMA, errors={}
        )
        flow.async_create_entry.assert_not_called()

    async def test_async_step_user_form_reshown_shown_on_connect_error(self, setup):
        """When a connect error occurs on login, reshow the form with error message"""
        setup.patch.object(
            AerogardenClient, "login", side_effect=AerogardenApiConnectError
        )

        flow = ConfigFlow()
        await flow.async_step_user(USER_INPUT)

        flow.async_show_form.assert_called_with(
            step_id="user", data_schema=CONFIG_SCHEMA, errors={"base": "cannot_connect"}
        )
        flow.async_create_entry.assert_not_called()

    async def test_async_step_user_form_reshown_shown_on_auth_error(self, setup):
        """When an auth error occurs on login, reshow the form with error message"""
        setup.patch.object(
            AerogardenClient, "login", side_effect=AerogardenApiAuthError
        )

        flow = ConfigFlow()
        await flow.async_step_user(USER_INPUT)

        flow.async_show_form.assert_called_with(
            step_id="user", data_schema=CONFIG_SCHEMA, errors={"base": "invalid_auth"}
        )
        flow.async_create_entry.assert_not_called()

    async def test_async_step_user_form_reshown_shown_on_unknown_error(self, setup):
        """When an unknown error occurs on login, reshow the form with error message"""
        setup.patch.object(AerogardenClient, "login", side_effect=AerogardenApiError)

        flow = ConfigFlow()
        await flow.async_step_user(USER_INPUT)

        flow.async_show_form.assert_called_with(
            step_id="user", data_schema=CONFIG_SCHEMA, errors={"base": "unknown"}
        )
        flow.async_create_entry.assert_not_called()

    async def test_async_step_user_config_entry_created_on_success(self, setup):
        """If client successfully logs in and gets data, then commit the config"""

        flow = ConfigFlow()
        await flow.async_step_user(USER_INPUT)

        flow.async_create_entry.assert_called()
        flow.async_show_form.assert_not_called()

    @pytest.mark.parametrize("user_input", [5, 600, DEFAULT_POLLING_INTERVAL])
    async def test_options_flow_handler_update_config_and_data_coordinator(
        self, mocker: MockFixture, setup_options_flow, user_input, setup_mocks
    ):
        """If provided polling interval is valid, update config and data coordinator with new value"""
        (hass, coordinator, config_entry, options_flow) = setup_mocks

        config_entry.data = {}

        await options_flow.async_step_init({CONF_POLLING_INTERVAL: user_input})

        options_flow.async_show_form.assert_not_called()
        options_flow.hass.config_entries.async_update_entry.assert_called()

        assert coordinator.update_interval == timedelta(seconds=user_input)

    async def test_async_get_options_flow_returns_options_flow(
        self, mocker: MockFixture
    ):
        """options flow returned from static method"""
        config_entry = mocker.patch.object(
            config_entries.ConfigEntry, "data", return_value={}
        )
        result = ConfigFlow.async_get_options_flow(config_entry)

        assert result is not None

    @pytest.mark.parametrize(
        "existing_value,expected_value",
        [(None, DEFAULT_POLLING_INTERVAL), (5, 5), (600, 600)],
    )
    async def test_options_flow_handler_show_form(
        self, mocker: MockFixture, setup_options_flow, existing_value, expected_value
    ):
        """If no user input provided, async_setup_init should show form with correct value"""

        config_entry = mocker.patch.object(
            config_entries.ConfigEntry,
            "data",
            return_value={CONF_POLLING_INTERVAL: existing_value},
        )
        flow = OptionsFlow(config_entry)
        await flow.async_step_init()

        flow.async_show_form.assert_called_with(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                    ): int,
                    vol.Optional(CONF_UPDATE_PASSWORD): str,
                }
            ),
            errors={},
        )
        flow.async_create_entry.assert_not_called()

    async def test_options_flow_handler_show_form_uninitalized(
        self, mocker: MockFixture, setup_options_flow
    ):
        """If no user input provided, and no interval exists in settings, async_setup_init should show form with default value"""

        config_entry = mocker.patch.object(
            config_entries.ConfigEntry, "data", return_value={}
        )
        flow = OptionsFlow(config_entry)
        await flow.async_step_init()

        flow.async_show_form.assert_called_with(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                    ): int,
                    vol.Optional(CONF_UPDATE_PASSWORD): str,
                }
            ),
            errors={},
        )
        flow.async_create_entry.assert_not_called()

    @pytest.mark.parametrize("polling_interval", [0, -5, 4])
    async def test_options_flow_handler_show_form_with_error_polling_interval(
        self, mocker: MockFixture, setup_options_flow, polling_interval, setup_mocks
    ):
        """If provided polling interval is not valid, show form with error"""

        (_, _, _, flow) = setup_mocks
        await flow.async_step_init({CONF_POLLING_INTERVAL: polling_interval})

        flow.async_show_form.assert_called_with(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                    ): int,
                    vol.Optional(CONF_UPDATE_PASSWORD): str,
                }
            ),
            errors={CONF_POLLING_INTERVAL: "invalid_polling_interval"},
        )
        flow.hass.config_entries.async_update_entry.assert_not_called()
        flow.async_create_entry.assert_not_called()

    @pytest.mark.parametrize(
        "error,expected",
        [
            (AerogardenApiConnectError, "cannot_connect"),
            (AerogardenApiAuthError, "invalid_auth"),
            (AerogardenApiError, "unknown"),
        ],
    )
    async def test_options_flow_handler_show_form_with_error_bad_password(
        self,
        mocker: MockFixture,
        setup_options_flow,
        setup,
        setup_mocks,
        error,
        expected,
    ):
        """If provided polling interval is not valid, show form with error"""
        setup.patch.object(AerogardenClient, "login", side_effect=error)

        (_, _, _, flow) = setup_mocks

        await flow.async_step_init({CONF_UPDATE_PASSWORD: "hunter2"})

        flow.async_show_form.assert_called_with(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                    ): int,
                    vol.Optional(CONF_UPDATE_PASSWORD): str,
                }
            ),
            errors={CONF_UPDATE_PASSWORD: expected},
        )
        flow.hass.config_entries.async_update_entry.assert_not_called()
        flow.async_create_entry.assert_not_called()

    async def test_options_flow_handler_update_password_restart_dialog_shown(
        self, mocker: MockFixture, setup_options_flow, setup, setup_mocks
    ):
        """If provided password is not valid, show form with error"""

        flow: OptionsFlow
        (_, _, _, flow) = setup_mocks

        await flow.async_step_init({CONF_UPDATE_PASSWORD: "hunter2"})

        flow.async_show_menu.assert_called_with(
            step_id="notify_restart", menu_options=["restart_yes", "restart_no"]
        )
        flow.async_create_entry.assert_not_called()

    async def test_options_flow_handler_update_values_set_on_config(
        self, mocker: MockFixture, setup_options_flow, setup, setup_mocks
    ):
        """Values provided should be updated via hass"""

        flow: OptionsFlow
        (_, _, _, flow) = setup_mocks

        await flow.async_step_init(
            {CONF_POLLING_INTERVAL: 10, CONF_UPDATE_PASSWORD: "hunter2"}
        )

        flow.hass.config_entries.async_update_entry.assert_called_with(
            ANY,
            data={
                CONF_EMAIL: "unittest@ha.com",
                CONF_POLLING_INTERVAL: 10,
                CONF_PASSWORD: "hunter2",
            },
        )
        flow.async_create_entry.assert_not_called()

    async def test_restart_yes_sends_restart_signal(
        self, mocker: MockFixture, setup_options_flow, setup, setup_mocks
    ):
        """The signal for restarting home assistant is called when user selects Restart Now"""
        flow: OptionsFlow
        (_, _, _, flow) = setup_mocks

        await flow.async_step_restart_yes(None)
        flow.hass.services.async_call.assert_called_with("homeassistant", "restart")

    async def test_restart_no_does_not_send_restart_signal(
        self, mocker: MockFixture, setup_options_flow, setup, setup_mocks
    ):
        """The signal for restarting home assistant is called when user selects Restart Later"""
        flow: OptionsFlow
        (_, _, _, flow) = setup_mocks

        await flow.async_step_restart_no(None)
        flow.hass.services.async_call.assert_not_called()
