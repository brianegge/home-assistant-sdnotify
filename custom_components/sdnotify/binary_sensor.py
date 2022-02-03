import os
import logging
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.util import Throttle
import homeassistant.util.dt as dt_util

REQUIREMENTS = ["sdnotify"]

__version__ = "0.1"

_LOGGER = logging.getLogger(__name__)


def get_scan_interval():
    watchdog_usec = os.environ.get("WATCHDOG_USEC")
    if watchdog_usec is not None:
        _LOGGER.debug("WATCHDOG_USEC=%s", watchdog_usec)
        watchdog_sec = int(watchdog_usec) / 1000 / 1000
        return watchdog_sec


DOMAIN = "sdnotify"
SCAN_INTERVAL = timedelta(seconds=get_scan_interval() or 5)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Initialise SDNotifier."""
    async_add_entities([Notifier(hass)], True)


class Notifier(BinarySensorEntity):
    def __init__(self, hass):
        import sdnotify

        self.notifier = sdnotify.SystemdNotifier()
        self.ready = False
        self.attributes = {}

    def _notify(self, message):
        self.notifier.notify(message)
        _LOGGER.debug("sdnotify: %s", message)

    @property
    def should_poll(self):
        """Determine if polling needed."""
        return self.notifier.socket is not None

    @property
    def name(self):
        """Return the name of the sensor."""
        return "systemd Service"

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        if self.notifier.socket is not None:
            self.attributes["last_updated"] = str(dt_util.now())
            if not self.ready:
                self._notify("READY=1")
                self.ready = True
            self._notify("WATCHDOG=1")

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return not self.ready

    @property
    def device_class(self):
        """Return the class of this device."""
        return "problem"

    @property
    def extra_state_attributes(self):
        """Attributes."""
        return self.attributes
