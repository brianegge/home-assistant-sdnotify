"""Tests for sdnotify integration setup."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sdnotify.const import DOMAIN


async def test_setup_entry(hass: HomeAssistant) -> None:
    """Test setting up the integration."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier"
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED


async def test_unload_entry(hass: HomeAssistant) -> None:
    """Test unloading the integration."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier"
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.async_unload(entry.entry_id)

    assert result is True
    assert entry.state is ConfigEntryState.NOT_LOADED
