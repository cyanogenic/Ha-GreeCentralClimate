""" Gree Central Climate """

from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """设置集成条目"""
    await hass.config_entries.async_forward_entry_setups(entry, ["climate"])
    return True

async def async_unload_entry(hass, entry):
    """卸载集成条目"""
    return await hass.config_entries.async_unload_platforms(entry, ["climate"])

