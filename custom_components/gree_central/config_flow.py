import logging
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from .const import DOMAIN, CONF_TEMP_STEP, CONF_FAKE_SERVER

_LOGGER = logging.getLogger(__name__)

class GreeCentralConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # 检查是否已经配置过该 IP
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                # 云控IP作为title
                title=f"{user_input[CONF_HOST]}", 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="<broadcast>"): str,
                vol.Optional(CONF_TEMP_STEP, default=0.5): vol.Coerce(float),
                vol.Optional(CONF_SCAN_INTERVAL, default=30): int,
                vol.Optional(CONF_FAKE_SERVER, default=""): str,
            }),
            errors=errors,
        )
