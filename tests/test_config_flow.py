"""Tests for sdnotify config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.sdnotify.const import DOMAIN


async def test_user_flow(hass: HomeAssistant) -> None:
    """Test the user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier"
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "systemd Notify"
    assert result["data"] == {}


async def test_already_configured(hass: HomeAssistant) -> None:
    """Test that only one instance can be configured."""
    # Create a first entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier"
    ):
        await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )

    # Try to create a second - should abort
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"
