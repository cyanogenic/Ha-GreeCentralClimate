import logging
from typing import Any
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er, selector

from .const import DOMAIN, CONF_TEMP_STEP, CONF_FAKE_SERVER

_LOGGER = logging.getLogger(__name__)

class OptionsFlowHandler(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="init",
            menu_options=['general', 'binding']
        )
    
    async def async_step_general(self,  user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors = {}

        current_data = self.config_entry.data

        if user_input is not None:
            # 更新配置条目的 data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**current_data, **user_input}
            )
            # 重新加载集成以应用新配置
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            # TODO: 更新host后清空当前实体
            return self.async_abort(reason="options_updated")

        return self.async_show_form(
            step_id="general",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=current_data.get(CONF_HOST, "<broadcast>")): str,
                vol.Optional(CONF_TEMP_STEP, default=current_data.get(CONF_TEMP_STEP, 0.5)): vol.Coerce(float),
                vol.Optional(CONF_SCAN_INTERVAL, default=current_data.get(CONF_SCAN_INTERVAL, 30)): int,
                vol.Optional(CONF_FAKE_SERVER, default=current_data.get(CONF_FAKE_SERVER, "")): str,
            }),
            errors=errors,
        )
    
    async def async_step_binding(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """绑定温度传感器到空调实体"""
        errors = {}
        
        # 获取实体注册表
        entity_registry = er.async_get(self.hass)
        
        # 获取所有属于此配置条目的 climate 实体
        climate_entities = []
        for entity in entity_registry.entities.values():
            if (entity.config_entry_id == self.config_entry.entry_id and 
                entity.domain == "climate"):
                climate_entities.append(entity)
        
        if not climate_entities:
            return self.async_abort(reason="no_climate_entities")
        
        # 获取所有温度传感器实体
        temperature_sensors = []
        for entity in entity_registry.entities.values():
            if entity.domain == "sensor":
                # 获取实体的当前状态以检查是否为数值类型
                state = self.hass.states.get(entity.entity_id)
                if state and state.state not in ("unknown", "unavailable"):
                    try:
                        float(state.state)
                        temperature_sensors.append(entity.entity_id)
                    except (ValueError, TypeError):
                        pass
        
        temperature_sensors.sort()
        
        if user_input is not None:
            # 构建温度传感器绑定配置
            temp_sensor_config = {}
            
            for entity in climate_entities:
                # 从实体 unique_id 中提取 MAC 地址
                # unique_id 格式: com.greecentral.<mac>
                if entity.unique_id and entity.unique_id.startswith("com.greecentral."):
                    mac = entity.unique_id.split("com.greecentral.")[1]
                    sensor_key = f"temp_sensor_{mac}"
                    
                    if sensor_key in user_input and user_input[sensor_key]:
                        if user_input[sensor_key] == "不绑定":
                            _LOGGER.debug(f"Unbinding device {mac} from any sensor")
                            continue
                        _LOGGER.debug(f"Binding {user_input[sensor_key]} to device {mac}")
                        temp_sensor_config[mac] = user_input[sensor_key]
            
            # 更新配置条目的数据
            current_data = self.config_entry.data
            updated_data = {**current_data, "temp_sensor": temp_sensor_config}
            
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_data
            )
            
            # 重新加载集成以应用新配置
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_abort(reason="binding_updated")
        
        # 获取当前的温度传感器绑定配置
        current_temp_sensors = self.config_entry.data.get("temp_sensor", {})
        
        # 构建表单数据架构
        schema_dict = {}
        for entity in climate_entities:
            # 从实体 unique_id 中提取 MAC 地址
            if entity.unique_id and entity.unique_id.startswith("com.greecentral."):
                mac = entity.unique_id.split("com.greecentral.")[1]
                sensor_key = f"temp_sensor_{mac}"
                
                # 获取当前绑定的传感器
                current_sensor = current_temp_sensors.get(mac)
                
                # 创建选择器，允许不选择（None 表示不绑定）
                schema_dict[vol.Required(sensor_key, default=current_sensor)] = selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["不绑定"]+temperature_sensors, mode="dropdown"
                    )
                )
        
        return self.async_show_form(
            step_id="binding",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "climate_count": str(len(climate_entities)),
                "sensor_count": str(len(temperature_sensors))
            }
        )

class GreeCentralConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()

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
