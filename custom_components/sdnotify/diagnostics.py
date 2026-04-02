"""Diagnostics support for sdnotify."""

from __future__ import annotations

import os
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    watchdog_usec = os.environ.get("WATCHDOG_USEC")
    notify_socket = os.environ.get("NOTIFY_SOCKET")

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
        },
        "environment": {
            "watchdog_usec": watchdog_usec,
            "notify_socket": "**REDACTED**" if notify_socket else None,
            "watchdog_interval_seconds": (
                int(watchdog_usec) // 1_000_000 if watchdog_usec else 5
            ),
        },
    }
