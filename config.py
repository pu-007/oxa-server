# -*- coding: utf-8 -*-
import asyncio

from oxa_ext.utils import ensure_dependencies, map_all_to, map_the_switches, off, on, AppConfigBuilder


async def wake_up_computer(_):
    """
    发送网络唤醒 (Wake-on-LAN) 魔法包来启动电脑。
    请确保已安装 'wakeonlan' 库，并替换为您的 MAC 地址和广播 IP。
    """
    ensure_dependencies(["wakeonlan"])
    computer_mac = "08BFB8A67CE2"
    subnet_broadcast_ip = "192.168.100.255"
    from wakeonlan import send_magic_packet
    await asyncio.to_thread(send_magic_packet,
                            computer_mac,
                            ip_address=subnet_broadcast_ip)
    print(f"已向 {computer_mac} 发送网络唤醒包。")


lights_balcony = ["台灯", "副灯"]
appliances_extra = ["空调", "风扇", "电视"]

lights_all = [*lights_balcony, "主灯"]
appliances_all = [*lights_all, *appliances_extra, "我的电脑"]

APP_CONFIG = AppConfigBuilder(
    direct_vad_wakeup_keywords=["小智小智"],
    direct_vad_command_map={
        ## 小爱同学原生指令
        **map_all_to(("调整颜色", "切换色温", "请开夜灯", "请关夜灯"), ["色温分段"]),
        **map_the_switches(*lights_all, *appliances_extra),
        "空调升速": ["空调风速升高"],
        "空调降速": ["空调风速降低"],
        "空调降温": ["空调温度降低"],
        "空调升温": ["空调温度升高"],
        "风扇定时": ["风扇计时器"],
        "风扇风类": ["调整风类"],
        "点亮阳台": on(*lights_balcony),
        "熄灭阳台": off(*lights_balcony),
        "灯光全灭": off(*lights_all),
        "关灯空调": off(*lights_all, "空调"),
        "全部关闭": off(*appliances_all),
        # TODO: 电脑操作与客户端 cut_in_xiaoai 使用 fastapi 通信 / 一键转化配置
        "请开电脑": [wake_up_computer],
        "请关电脑": ["关闭我的电脑"],
        "重启电脑": ["我的电脑设置为一"],
        "切换屏幕": ["我的电脑设置为三"],
        "测试电脑": ["我的电脑设置为七"],
        "联合关闭": ["关闭我的电脑", "关闭电视"],
        "联合启动": [wake_up_computer, "打开电视"],
    },
    xiaoai_wakeup_keywords=["召唤小智"],
    # TODO: 小爱电视遥控器模式 可连续对话
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
