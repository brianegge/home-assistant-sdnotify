"""Tests for sdnotify binary sensor."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.sdnotify.const import DOMAIN


def _get_entity_id(hass: HomeAssistant) -> str:
    """Get the sdnotify binary sensor entity id."""
    entity_ids = hass.states.async_entity_ids("binary_sensor")
    assert len(entity_ids) == 1
    return entity_ids[0]


async def test_sensor_created(hass: HomeAssistant) -> None:
    """Test that the binary sensor is created on setup."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    mock_notifier = MagicMock()
    mock_notifier.socket = None

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier",
        return_value=mock_notifier,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    entity_id = _get_entity_id(hass)
    state = hass.states.get(entity_id)
    assert state is not None


async def test_sensor_problem_before_ready(hass: HomeAssistant) -> None:
    """Test that sensor shows problem before ready notification."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    mock_notifier = MagicMock()
    mock_notifier.socket = None

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier",
        return_value=mock_notifier,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    entity_id = _get_entity_id(hass)
    state = hass.states.get(entity_id)
    assert state is not None
    # is_on = True means problem (not ready yet)
    assert state.state == "on"


async def test_sensor_no_poll_without_socket(hass: HomeAssistant) -> None:
    """Test sensor does not poll when no systemd socket."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    mock_notifier = MagicMock()
    mock_notifier.socket = None

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier",
        return_value=mock_notifier,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    entity_id = _get_entity_id(hass)
    state = hass.states.get(entity_id)
    assert state is not None
    # Without a socket, the notifier should not have been called
    mock_notifier.notify.assert_not_called()


async def test_sensor_sends_ready_and_watchdog(hass: HomeAssistant) -> None:
    """Test that update sends READY=1 then WATCHDOG=1."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    mock_notifier = MagicMock()
    mock_notifier.socket = "/run/systemd/notify"

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier",
        return_value=mock_notifier,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Trigger a polling cycle
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
        await hass.async_block_till_done()

    # With a socket, the first update should send READY=1 and WATCHDOG=1
    calls = [c[0][0] for c in mock_notifier.notify.call_args_list]
    assert "READY=1" in calls
    assert "WATCHDOG=1" in calls


async def test_sensor_off_after_ready(hass: HomeAssistant) -> None:
    """Test sensor turns off (no problem) after ready notification."""
    entry = MockConfigEntry(domain=DOMAIN, title="systemd Notify", data={})
    entry.add_to_hass(hass)

    mock_notifier = MagicMock()
    mock_notifier.socket = "/run/systemd/notify"

    with patch(
        "custom_components.sdnotify.binary_sensor.sdnotify.SystemdNotifier",
        return_value=mock_notifier,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Trigger a polling cycle so async_update runs
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
        await hass.async_block_till_done()

    entity_id = _get_entity_id(hass)
    state = hass.states.get(entity_id)
    assert state is not None
    # After successful update with socket, ready=True so is_on=False (no problem)
    assert state.state == "off"


async def test_watchdog_usec_env() -> None:
    """Test that WATCHDOG_USEC environment variable is read."""
    with patch.dict("os.environ", {"WATCHDOG_USEC": "10000000"}):
        from custom_components.sdnotify.binary_sensor import _get_scan_interval

        interval = _get_scan_interval()
        assert interval == 10


async def test_watchdog_usec_default() -> None:
    """Test default scan interval when WATCHDOG_USEC not set."""
    with patch.dict("os.environ", {}, clear=True):
        from custom_components.sdnotify.binary_sensor import _get_scan_interval

        interval = _get_scan_interval()
        assert interval == 5
