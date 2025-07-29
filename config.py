# -*- coding: utf-8 -*-
import asyncio

from oxa_ext.utils import ensure_dependencies, map_all_to, map_the_switches, AppConfigBuilder


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


APP_CONFIG = AppConfigBuilder(
    direct_vad_wakeup_keywords=["小智小智"],
    direct_vad_command_map={
        ## 小爱同学原生指令
        **map_all_to(("切换电视", "请开电视", "请关电视"), ["打开电视"]),
        **map_all_to(("切换主灯", "请开大灯", "请关大灯"), ["请关主灯"]),
        **map_all_to(("调整颜色", "请开夜灯", "请关夜灯"), ["色温分段"]),
        **map_the_switches("空调", "风扇", "台灯", "副灯"),
        "空调升速": ["空调风速升高"],
        "空调降速": ["空调风速降低"],
        "空调降温": ["空调温度降低"],
        "空调升温": ["空调温度升高"],
        "切换色温": ["色温分段"],
        "风扇定时": ["风扇计时器"],
        "风扇风类": ["调整风类"],
        "点亮外面": ["打开台灯", "打开副灯"],
        "熄灭外面": ["关闭台灯", "关闭副灯"],
        "关灯空调": ["关闭主灯", "关闭台灯", "关闭副灯", "关闭空调"],
        "灯光全灭": ["关闭主灯", "关闭台灯", "关闭副灯"],
        "全部关闭": ["关闭空调", "关闭风扇", "关闭主灯", "关闭电视", "关闭我的电脑", "关闭台灯", "关闭副灯"],
        # TODO: 电脑操作与客户端 cut_in_xiaoai 使用 fastapi 通信 / 一键转化配置
        "请开电脑": [wake_up_computer],
        "切换屏幕": ["我的电脑设置为三"],
        "请关电脑": ["关闭我的电脑"],
        "重启电脑": ["我的电脑设置为一"],
        "测试电脑": ["我的电脑设置为七"],
        "联合关闭": ["关闭我的电脑", "关闭电视"],
        "联合启动": [wake_up_computer, "打开电视"],
    },
    xiaoai_wakeup_keywords=["召唤小智"],
    # TODO: 小爱电视遥控器模式 可连续对话
    xiaoai_extension_command_map={},
    vad_config={
        "boost": 200,
        "threshold": 0.1,
        "min_speech_duration": 1000,
        "min_silence_duration": 1000,
    },
    xiaozhi_config={
        "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",
        "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",
        "WEBSOCKET_ACCESS_TOKEN": "",
        "DEVICE_ID": "70:70:fc:05:83:fa",
        "VERIFICATION_CODE": "699244",
    }).build()
