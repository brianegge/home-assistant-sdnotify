"""Binary sensor platform for sdnotify."""

import logging
import os
from datetime import timedelta

import sdnotify

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_scan_interval() -> int:
    """Get scan interval from WATCHDOG_USEC env var."""
    watchdog_usec = os.environ.get("WATCHDOG_USEC")
    if watchdog_usec is not None:
        _LOGGER.debug("WATCHDOG_USEC=%s", watchdog_usec)
        return int(watchdog_usec) // 1_000_000
    return 5


SCAN_INTERVAL = timedelta(seconds=_get_scan_interval())


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sdnotify binary sensor from a config entry."""
    notifier = await hass.async_add_executor_job(sdnotify.SystemdNotifier)
    async_add_entities([SdnotifyBinarySensor(entry, notifier)])


class SdnotifyBinarySensor(BinarySensorEntity):
    """Binary sensor that sends systemd watchdog notifications."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        entry: ConfigEntry,
        notifier: sdnotify.SystemdNotifier,
    ) -> None:
        """Initialize the sensor."""
        self._notifier = notifier
        self._ready = False
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def should_poll(self) -> bool:
        """Poll only when systemd socket is available."""
        return self._notifier.socket is not None

    @property
    def is_on(self) -> bool:
        """Return true if not yet ready (problem state)."""
        return not self._ready

    async def async_update(self) -> None:
        """Send watchdog ping to systemd."""
        if self._notifier.socket is None:
            return
        if not self._ready:
            await self.hass.async_add_executor_job(
                self._notifier.notify, "READY=1"
            )
            self._ready = True
        await self.hass.async_add_executor_job(
            self._notifier.notify, "WATCHDOG=1"
        )
