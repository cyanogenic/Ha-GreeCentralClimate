import logging
from datetime import timedelta

from homeassistant.const import (CONF_SCAN_INTERVAL, CONF_HOST)
from .const import CONF_TEMP_STEP, CONF_FAKE_SERVER

from .bridge import GreeBridge
from .fake_server import FakeServer

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """从 Config Entry 启动 (UI 方式)"""
    config = entry.data
    host = config.get(CONF_HOST)
    fake_server = config.get(CONF_FAKE_SERVER)
    # config_flow 传进来的是整数，这里转回 timedelta
    scan_interval = timedelta(seconds=config.get(CONF_SCAN_INTERVAL, 30))
    temp_step = config.get(CONF_TEMP_STEP)
    
    # 从 config.data 获取温度传感器配置（旧方式/yaml配置）
    temp_sensor = config.get("temp_sensor", {})

    _LOGGER.info(f"Setting up Gree climate via Config Flow: {host}")

    if fake_server:
        server = FakeServer(hass, fake_server, 1812, 'dis.gree.com')
    bridge = GreeBridge(hass, host, scan_interval,
                        temp_sensor, temp_step, async_add_entities)
