# -*- coding: utf-8 -*-
"""
Oxa-Server 全局配置文件模板

本文件集中管理所有应用程序级别的配置，包括硬件参数、云服务凭据、以及自定义语音指令。
请将此文件复制为 config.py，并填入您自己的配置信息。
"""
import asyncio

from oxa_ext.type_defines import SpeakerProtocol, Actions
from oxa_ext.utils import ensure_dependencies, map_all_to, interrupt_xiaoai

# ==============================================================================
# 主要应用配置 (Primary Application Configuration)
# ==============================================================================
# 请在此处修改您的核心配置信息。

# --- 语音活动检测 (VAD) 配置 ---
# 用于判断用户是否开始或停止说话。
VAD_CONFIG = {
    "boost": 200,  # 音频增益
    "threshold": 0.1,  # 语音检测阈值
    "min_speech_duration": 1000,  # 最短语音时长 (毫秒)
    "min_silence_duration": 1000,  # 语音结束后最短静音时长 (毫秒)
}

# --- 小智云服务配置 ---
# 用于连接小智的云端服务，实现远程控制和OTA更新。
XIAOZHI_CONFIG = {
    "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",  # OTA 更新服务器地址
    "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",  # WebSocket 通信地址
    "WEBSOCKET_ACCESS_TOKEN": "",  # WebSocket 访问令牌 (如果服务需要)
    "DEVICE_ID": "XX:XX:XX:XX:XX:XX",  # 您的设备唯一ID (例如MAC地址)
    "VERIFICATION_CODE": "YYYYYY",  # 设备验证码
}


# ==============================================================================
# 自定义功能实现 (Custom Function Implementations)
# ==============================================================================

# 在这里定义您的自定义异步函数，例如网络唤醒、API调用等。
async def wake_up_computer(_):
    """
    示例：发送网络唤醒 (Wake-on-LAN) 魔法包来启动电脑。
    请确保已安装 'wakeonlan' 库 (`pip install wakeonlan`)，并替换为您的真实 MAC 地址和广播 IP。
    """
    ensure_dependencies(["wakeonlan"])
    # 替换为您的电脑MAC地址
    computer_mac = "08:BF:B8:A6:7C:E2"
    # 替换为您的局域网广播地址
    subnet_broadcast_ip = "192.168.100.255"
    from wakeonlan import send_magic_packet
    await asyncio.to_thread(send_magic_packet,
                            computer_mac,
                            ip_address=subnet_broadcast_ip)
    print(f"已向 {computer_mac} 发送网络唤醒包。")


# ==============================================================================
# 指令映射表 (Command Maps)
# ==============================================================================
# 这是整个系统的核心，通过“数据驱动”的方式将语音指令映射到具体操作。

# --- 模式一：直接VAD唤醒指令 ---
# 无需说“小爱同学”，直接说出这些词即可触发。
DIRECT_VAD_WAKEUP_KEYWORDS = ["小智小智"]
DIRECT_VAD_COMMAND_MAP: dict[str, Actions] = {
    ## 示例：小爱同学原生指令 (单个或多个)
    **map_all_to(("切换电视", "请开电视"), ["打开电视"]),
    "请关空调": ["关闭空调"],

    ## 示例：连续执行多个指令
    "灯光全灭": ["关闭主灯", "关闭台灯", "关闭副灯"],

    ## 示例：执行自定义函数
    "请开电脑": [wake_up_computer],

    ## 示例：混合指令 (原生指令 + 自定义函数)
    "联合启动": [wake_up_computer, "打开电视"],
}


# --- 模式二：小爱对话中继指令 ---
# 在与“小爱同学”对话时说出，用于唤醒小智或扩展小爱功能。
async def enter_tv_remote_mode(speaker: SpeakerProtocol):
    """
    示例函数：进入电视遥控模式。
    这是一个占位符，用于演示如何将复杂功能模块化。
    """
    print("进入电视遥控模式（功能待实现）...")
    await speaker.play("好的正在准备遥控电视")
    # 在此添加您的具体实现
    pass


XIAOAI_WAKEUP_KEYWORDS = ["召唤小智"]
XIAOAI_EXTENSION_COMMAND_MAP: dict[str, Actions] = {
    # 示例：先让小爱打开电视，然后执行自定义的遥控模式函数
    "操控电视": ["打开电视", enter_tv_remote_mode],
}


# ==============================================================================
# 事件处理器 (Event Handlers) - 通常无需修改
# ==============================================================================
async def _handle_direct_vad_command(speaker: SpeakerProtocol,
                                     text: str) -> bool:
    """处理通过直接VAD监听到的指令。"""
    print(f"接收到直接VAD指令: '{text}'")
    actions = DIRECT_VAD_COMMAND_MAP.get(text, [])
    for action in actions:
        if isinstance(action, str):
            print(f"  -> 执行小爱原生指令: '{action}'")
            await speaker.ask_xiaoai(text=action, silent=True)
        elif callable(action):
            print(f"  -> 执行自定义函数: {action.__name__}")
            await action(speaker)
        await asyncio.sleep(0.2)
    await speaker.play(text="已执行")
    return False


async def _handle_xiaoai_command(speaker: SpeakerProtocol, text: str) -> bool:
    """
    处理在小爱对话中捕获的指令。
    返回 True 表示需要唤醒小智，返回 False 表示仅执行扩展功能。
    """
    actions = XIAOAI_EXTENSION_COMMAND_MAP.get(text, [])
    if actions:
        print(f"接收到小爱扩展指令: '{text}'")
        await interrupt_xiaoai(speaker)  # 先打断小爱，确保控制权
        for action in actions:
            if isinstance(action, str):
                print(f"  -> 执行小爱原生指令: '{action}'")
                await speaker.ask_xiaoai(text=action, silent=True)
            elif callable(action):
                print(f"  -> 执行自定义函数: {action.__name__}")
                await action(speaker)
            await asyncio.sleep(0.2)
    return False


async def _before_wakeup(speaker: SpeakerProtocol, text: str,
                         source: str) -> bool:
    """
    设备进入“唤醒”状态前的主回调函数。
    """
    if source == "kws":
        if text in DIRECT_VAD_WAKEUP_KEYWORDS:
            await speaker.play(text="小智来了")
            return True
        return await _handle_direct_vad_command(speaker, text)
    elif source == "xiaoai":
        if text in XIAOAI_WAKEUP_KEYWORDS:
            await interrupt_xiaoai(speaker)
            await speaker.play(text="小智来了")
            return True
        return await _handle_xiaoai_command(speaker, text)

    return False


async def _after_wakeup(speaker: SpeakerProtocol):
    """设备从“唤醒”状态退出时调用。"""
    await speaker.play(text="主人再见")


# ==============================================================================
# 最终配置组装 (Final Configuration Assembly) - 通常无需修改
# ==============================================================================

# 注册所有需要被 VAD 监听的关键词
ALL_VAD_KEYWORDS = [
    *DIRECT_VAD_WAKEUP_KEYWORDS, *list(DIRECT_VAD_COMMAND_MAP.keys())
]

# 唤醒和指令处理配置
WAKEUP_CONFIG = {
    "keywords": ALL_VAD_KEYWORDS,
    "timeout": 5,
    "before_wakeup": _before_wakeup,
    "after_wakeup": _after_wakeup,
}

# 合成最终的 APP_CONFIG
APP_CONFIG = {
    "vad": VAD_CONFIG,
    "xiaozhi": XIAOZHI_CONFIG,
    "wakeup": WAKEUP_CONFIG,
}

print("✅ Oxa-Server 配置模板加载完成。请复制为 config.py 并修改。")
