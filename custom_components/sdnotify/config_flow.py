"""Config flow for sdnotify integration."""

from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN


class SdnotifyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sdnotify."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="systemd Notify", data={})

        return self.async_show_form(step_id="user")
