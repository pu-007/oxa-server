# -*- coding: utf-8 -*-

from oxa_ext.utils import map_all_to, map_the_switches, off, on, wol, hass_action, AppConfigBuilder
from oxa_ext.type_defines import ActionFunction

lights_balcony = ["台灯", "副灯"]
appliances_extra = ["空调", "风扇", "电视"]

appliances_all = [*lights_balcony, *appliances_extra, "我的电脑"]


async def wake_up_computer(speaker):
    wol(computer_mac="08BFB8A67CE2", broadcast_ip="192.168.100.255")
    await speaker.play(text="正在开启")


# --- Home Assistant 配置 ---
def hass_ctl(**kwargs) -> ActionFunction:
    "paras: domain, service, entity_id"
    HASS_URL = "http://192.168.100.1:8123"  # 替换为你的 HASS 地址
    HASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0OTVlMDdjMDRlYTU0OTYwYjhjMWY4ODhjNTc1MTQxZCIsImlhdCI6MTc2NzQxNTU0NCwiZXhwIjoyMDgyNzc1NTQ0fQ.lTJuOP5XrX6ppVhmOI-jPA8FMTplhlOL6RM35kMOf5c"  # 替换为你的长期访问令牌
    return hass_action(url=HASS_URL, token=HASS_TOKEN, **kwargs)


on_main_light = [
    "打开主灯",
    hass_ctl(domain="input_boolean",
             service="turn_on",
             entity_id="input_boolean.zhu_deng_zhi_neng_kai_guan")
]

off_main_light = [
    "关闭主灯",
    hass_ctl(domain="input_boolean",
             service="turn_off",
             entity_id="input_boolean.zhu_deng_zhi_neng_kai_guan")
]

APP_CONFIG = AppConfigBuilder(
    direct_vad_wakeup_keywords=["小智小智"],
    direct_vad_command_map={
        ######## 批量分组设置
        "灯光全开": [*on(*lights_balcony), *on_main_light],
        "灯光全灭": [*off(*lights_balcony), *off_main_light],
        # 映射所有开关 （主灯单独设置）
        **map_the_switches(*lights_balcony, *appliances_extra),
        "请开主灯":
        on_main_light,
        "请关主灯":
        off_main_light,
        ######## 主灯相关设置
        # 色温调整
        **map_all_to(("调整颜色", "切换色温", "请关夜灯"), ["色温分段"]),
        # 夜灯 （分段色温实际上是米家中的相关手动控制，因为其他词汇可能会造成歧义或者无法被准确识别）
        "请开夜灯": ["分段色温"],
        "点亮阳台":
        on(*lights_balcony),
        "熄灭阳台":
        off(*lights_balcony),
        ######## 分组控制
        "关灯空调": [*off(*lights_balcony, "空调"), *off_main_light],
        "全部关闭": [*off(*appliances_all), *off_main_light],
        "请开电脑": [wake_up_computer],
        "请关电脑": ["关闭我的电脑"],
        "重启电脑": ["我的电脑设置为一"],
        "切换屏幕": ["我的电脑设置为三"],
        "测试电脑": ["我的电脑设置为七"],
        "联合关闭": ["关闭我的电脑", "关闭电视"],
        "联合启动": [wake_up_computer, "打开电视"],
        "空调升速": ["空调风速升高"],
        "空调降速": ["空调风速降低"],
        "空调降温": ["空调温度降低"],
        "空调升温": ["空调温度升高"],
        "风扇定时": ["风扇计时器"],
        "风扇风类": ["调整风类"],
    },
    xiaoai_wakeup_keywords=["召唤小智"],
    xiaoai_extension_command_map={},
    on_execute_play_text="",
    vad_config={
        "boost": 100,
        "threshold": 0.40,
        "min_speech_duration": 300,
        "min_silence_duration": 300,
    },
    xiaozhi_config={
        "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",
        "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",
        "WEBSOCKET_ACCESS_TOKEN": "",
        "DEVICE_ID": "70:70:fc:05:83:fa",
        "VERIFICATION_CODE": "976551",
    }).build()
