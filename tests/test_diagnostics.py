"""Tests for sdnotify diagnostics."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sdnotify.const import DOMAIN
from custom_components.sdnotify.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_with_watchdog(hass: HomeAssistant) -> None:
    """Test diagnostics when WATCHDOG_USEC is set."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    with patch.dict(
        "os.environ",
        {"WATCHDOG_USEC": "5000000", "NOTIFY_SOCKET": "/run/systemd/notify"},
    ):
        result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["environment"]["watchdog_usec"] == "5000000"
    assert result["environment"]["notify_socket"] == "**REDACTED**"
    assert result["environment"]["watchdog_interval_seconds"] == 5
    assert result["entry"]["entry_id"] == entry.entry_id


async def test_diagnostics_without_watchdog(hass: HomeAssistant) -> None:
    """Test diagnostics when no systemd env vars are set."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    with patch.dict("os.environ", {}, clear=True):
        result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["environment"]["watchdog_usec"] is None
    assert result["environment"]["notify_socket"] is None
    assert result["environment"]["watchdog_interval_seconds"] == 5
