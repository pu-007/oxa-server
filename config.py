# -*- coding: utf-8 -*-

from oxa_ext.utils import map_all_to, map_the_switches, off, on, wol, AppConfigBuilder

lights_balcony = ["台灯", "副灯"]
appliances_extra = ["空调", "风扇", "电视"]

lights_all = [*lights_balcony, "主灯"]
appliances_all = [*lights_all, *appliances_extra, "我的电脑"]

wake_up_computer = wol(computer_mac="08BFB8A67CE2",
                       broadcast_ip="192.168.100.255")

APP_CONFIG = AppConfigBuilder(
    direct_vad_wakeup_keywords=["小智小智"],
    direct_vad_command_map={
        ## 小爱同学原生指令
        **map_all_to(("调整颜色", "切换色温", "请关夜灯"), ["色温分段"]),
        # 小爱的自然语言处理会对一些指令无法识别，尤其是手动控制指令，需要换个说法
        "请开夜灯": ["分段色温"],
        **map_the_switches(*lights_all, *appliances_extra),
        "空调升速": ["空调风速升高"],
        "空调降速": ["空调风速降低"],
        "空调降温": ["空调温度降低"],
        "空调升温": ["空调温度升高"],
        "风扇定时": ["风扇计时器"],
        "风扇风类": ["调整风类"],
        "点亮阳台":
        on(*lights_balcony),
        "熄灭阳台":
        off(*lights_balcony),
        "灯光全灭":
        off(*lights_all),
        "关灯空调":
        off(*lights_all, "空调"),
        "全部关闭":
        off(*appliances_all),
        "请开电脑": [wake_up_computer],
        "请关电脑": ["关闭我的电脑"],
        "重启电脑": ["我的电脑设置为一"],
        "切换屏幕": ["我的电脑设置为三"],
        "测试电脑": ["我的电脑设置为七"],
        "联合关闭": ["关闭我的电脑", "关闭电视"],
        "联合启动": [wake_up_computer, "打开电视"],
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
