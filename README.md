# Ha-GreeCentralClimate

格力中央空调 Home Assistant 插件，通过与格力云控交互控制云控下的中央空调

本项目基于 [xcy1231/Ha-GreeCentralClimate](https://github.com/xcy1231/Ha-GreeCentralClimate) 开发，感谢原作者的支持！

## 安装

### 通过HACS自动安装

[![通过HACS安装集成](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cyanogenic&repository=Ha-GreeCentralClimate&category=integration)

### 手动安装

下载并复制 `custom_components/gree_central` 文件夹到HomeAssistant根目录下的 `custom_components` 文件夹即可

## 配置

配置 > 设备与服务 >  集成 >  添加集成 > 搜索 `Gree Central Climate`

或者点击: [![添加集成](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=gree_central)

### 配置说明

|配置项| 说明 |
| --- | --- |
| host | 格力云控的IP地址 |
| scan_interval  | 同步时间，默认为30秒 |
| temp_step  | 温度的调节精度，必须为0.5的倍数，默认为1 |

## 调试
在 `configuration.yaml` 中加入以下配置来打开调试日志。

```yaml
logger:
  default: info
  logs:
    custom_components.gree_central.config_flow: debug
```

## 开发计划

- [Fake Server](https://github.com/xcy1231/Ha-GreeCentralClimate?tab=readme-ov-file#%E6%9C%80%E6%96%B0%E4%BF%AE%E6%94%B9%E9%9B%86%E6%88%90fake-gree-server%E9%80%9A%E8%BF%87%E8%AF%A5server%E8%BF%9B%E8%A1%8C%E4%BA%91%E6%8E%A7%E7%9A%84%E7%8A%B6%E6%80%81%E8%8E%B7%E5%8F%96%E4%B8%8E%E6%8E%A7%E5%88%B6) 支持
- 多语言支持