# -*- coding: utf-8 -*-
"""
Oxa-Server 全局配置文件

本文件集中管理所有应用程序级别的配置，包括硬件参数、云服务凭据、以及自定义语音指令。
为了方便用户修改，常用配置项（如设备信息、网络地址等）都已拆分为独立的顶级变量，并附有注释。
"""
import asyncio
import os
import subprocess
from typing import Dict, List, Callable, Awaitable

from oxa_ext.speaker_protocol import SpeakerProtocol

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
    "WEBSOCKET_ACCESS_TOKEN": "",  # WebSocket 访问令牌 (如有)
    "DEVICE_ID": "70:70:fc:05:83:fa",  # 您的设备唯一ID (MAC地址)
    "VERIFICATION_CODE": "699244",  # 设备验证码
}

# ==============================================================================
# 自定义功能实现 (Custom Function Implementations)
# ==============================================================================
Action = Callable[[SpeakerProtocol], Awaitable[None]]


# 在这里定义您的自定义异步函数，例如网络唤醒、API调用等。
async def wake_up_computer(_):
    """
    发送网络唤醒 (Wake-on-LAN) 魔法包来启动电脑。
    请确保已安装 'wakeonlan' 库，并替换为您的 MAC 地址和广播 IP。
    """
    _ensure_dependencies(["wakeonlan"])
    computer_mac = "08BFB8A67CE2"
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
DIRECT_VAD_COMMAND_MAP: Dict[str, List[str | Action]] = {
    ## 小爱同学原生指令
    "切换电视": ["打开电视"],
    "请开电视": ["打开电视"],
    "请关电视": ["关闭电视"],
    "请开空调": ["打开空调"],
    "请关空调": ["关闭空调"],
    "空调升速": ["空调风速升高"],
    "空调降速": ["空调风速降低"],
    "请开风扇": ["打开风扇"],
    "请关风扇": ["关闭风扇"],
    "切换主灯": ["打开主灯"],
    "请开大灯": ["打开主灯"],
    "请关大灯": ["关闭主灯"],
    "请开台灯": ["打开台灯"],
    "请关台灯": ["关闭台灯"],
    "请关副灯": ["关闭副灯"],
    "请开副灯": ["打开副灯"],
    "切换色温": ["色温分段"],
    "调整颜色": ["色温分段"],
    "打开夜灯": ["昏暗模式"],
    "空调降温": ["空调温度降低"],
    "空调升温": ["空调温度升高"],
    "风扇定时": ["定时风扇"],
    "风扇风类": ["调整风类"],
    ## 连续指令
    "点亮外面": ["打开台灯", "打开副灯"],
    "熄灭外面": ["关闭台灯", "关闭副灯"],
    "关灯空调": ["关闭主灯", "关闭台灯", "关闭副灯", "关闭空调"],
    "灯光全灭": ["关闭主灯", "关闭台灯", "关闭副灯"],
    "全部关闭": ["关闭空调", "关闭风扇", "关闭主灯", "关闭电视", "关闭我的电脑", "关闭台灯", "关闭副灯"],
    ## 电脑控制指令（函数指令）
    # TODO:完善电脑上的客户端，目前通过巴法 mqtt 方式控制电脑。
    # 考虑以后使用 fastapi 直接通信，或者提供一键转换脚本
    "请开电脑": [wake_up_computer],
    "切换屏幕": ["我的电脑设置为三"],
    "请关电脑": ["关闭我的电脑"],
    "重启电脑": ["我的电脑设置为一"],
    "测试电脑": ["我的电脑设置为七"],
    "联合关闭": ["关闭我的电脑", "关闭电视"],
    ## 混合指令
    "联合启动": [wake_up_computer, "打开电视"],
}


# --- 模式二：小爱对话中继指令 ---
# 在与“小爱同学”对话时说出，用于唤醒小智或扩展小爱功能。
async def enter_tv_remote_mode(speaker: SpeakerProtocol):
    """
    示例函数：进入电视遥控模式。
    这是一个占位符，用于演示如何将复杂功能模块化。
    """
    # TODO: 此功能的完整实现未来可以放在一个独立的 'tv_control.py' 文件中，
    # 并在此处导入和调用，以保持 config.py 的整洁。
    print("进入电视遥控模式（功能待实现）...")
    await speaker.play("好的正在准备遥控电视")

    pass


XIAOAI_WAKEUP_KEYWORDS = ["召唤小智"]
XIAOAI_EXTENSION_COMMAND_MAP: Dict[str, List[str | Action]] = {
    # 示例：先让小爱打开电视，然后执行自定义的遥控模式函数
    "操控电视": ["打开电视", enter_tv_remote_mode],
}


# ==============================================================================
# 事件处理器 (Event Handlers)
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
        await _interrupt_xiaoai(speaker)  # 先打断小爱，确保控制权
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
            await _interrupt_xiaoai(speaker)
            await speaker.play(text="小智来了")
            return True
        return await _handle_xiaoai_command(speaker, text)

    return False


async def _after_wakeup(speaker: SpeakerProtocol):
    """设备从“唤醒”状态退出时调用。"""
    await speaker.play(text="主人再见")


# ==============================================================================
# 辅助函数 (Helper Functions)
# ==============================================================================


def _ensure_dependencies(requirements: list[str]):
    """
    检查并安装缺失的 Python 依赖包。
    确保在执行需要特定库的函数前，这些库是可用的。
    """
    import importlib.util
    missing_packages = [
        pkg for pkg in requirements if not importlib.util.find_spec(pkg)
    ]

    if not missing_packages:
        return

    print(f"检测到缺失的依赖: {missing_packages}，正在尝试安装...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_executable = os.path.join(script_dir, '.venv', "bin", 'python')
    if not os.path.exists(python_executable):
        import sys
        python_executable = sys.executable
        print(f"未找到虚拟环境，使用系统 Python: {python_executable}")

    subprocess.run([python_executable, "-m", "ensurepip"], check=False)
    subprocess.run(
        [python_executable, "-m", "pip", "install", *missing_packages],
        check=True)
    print("依赖安装完成。")


async def _interrupt_xiaoai(speaker):
    """
    中断小爱同学当前的对话或播放，并等待其服务重启。
    这是一个公共函数，用于在自定义指令执行前“清场”。
    """
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)


# ==============================================================================
# 最终配置组装 (Final Configuration Assembly)
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

print("✅ Oxa-Server 配置加载完成。")
