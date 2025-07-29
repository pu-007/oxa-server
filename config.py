# -*- coding: utf-8 -*-
"""
Oxa-Server 全局配置文件

本文件集中管理所有应用程序级别的配置，包括硬件参数、云服务凭据、以及自定义语音指令。
为了方便用户修改，常用配置项（如设备信息、网络地址等）都已拆分为独立的顶级变量，并附有注释。
"""
import asyncio

from oxa_ext.type_defines import SpeakerProtocol, Actions
from oxa_ext.utils import ensure_dependencies, map_all_to, interrupt_xiaoai, map_the_switches

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

# 在这里定义您的自定义异步函数，例如网络唤醒、API调用等。
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


# ==============================================================================
# 指令映射表 (Command Maps)
# ==============================================================================
# 这是整个系统的核心，通过“数据驱动”的方式将语音指令映射到具体操作。

# --- 模式一：直接VAD唤醒指令 ---
# 无需说“小爱同学”，直接说出这些词即可触发。
DIRECT_VAD_WAKEUP_KEYWORDS = ["小智小智"]
DIRECT_VAD_COMMAND_MAP: dict[str, Actions] = {
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
    "风扇定时": ["风扇时间"],
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
XIAOAI_EXTENSION_COMMAND_MAP: dict[str, Actions] = {
    # 示例：先让小爱打开电视，然后执行自定义的遥控模式函数
    "操控电视": ["打开电视", enter_tv_remote_mode],
}


# ==============================================================================
# 事件处理器 (Event Handlers)
# ==============================================================================
async def _before_wakeup(speaker: SpeakerProtocol, text: str,
                         source: str) -> bool:
    """
    设备进入“唤醒”状态前的主回调函数，合并并优化了所有前置指令处理逻辑。

    根据来源（source）判断是直接VAD指令还是小爱对话指令，并执行相应操作。
    通过内部辅助函数处理通用的指令执行逻辑，减少了代码重复。

    Args:
        speaker: 音箱控制协议实例。
        text: 识别到的文本。
        source: 文本来源，'kws' (直接VAD) 或 'xiaoai' (小爱对话)。

    Returns:
        bool: 如果需要唤醒主助理（小智），返回 True；否则返回 False。
    """

    async def _execute_actions(actions: Actions):
        """辅助函数，用于执行一系列指令动作。"""
        for action in actions:
            if isinstance(action, str):
                print(f"  -> 执行小爱原生指令: '{action}'")
                await speaker.ask_xiaoai(text=action, silent=True)
            elif callable(action):
                print(f"  -> 执行自定义函数: {action}")
                await action(speaker)
            await asyncio.sleep(0.2)

    # ---- 主逻辑开始 ----

    if source == "kws":
        # 1. 检查是否为直接VAD的唤醒词
        if text in DIRECT_VAD_WAKEUP_KEYWORDS:
            await speaker.play(text="小智来了")
            return True

        # 2. 检查并处理直接VAD指令
        actions = DIRECT_VAD_COMMAND_MAP.get(text, [])
        if actions:
            print(f"接收到直接VAD指令: '{text}'")
            await _execute_actions(actions)
            await speaker.play(text="已执行")
        return False

    elif source == "xiaoai":
        # 1. 检查是否为通过小爱对话唤醒的关键词
        if text in XIAOAI_WAKEUP_KEYWORDS:
            await interrupt_xiaoai(speaker)
            await speaker.play(text="小智来了")
            return True

        # 2. 检查并处理小爱扩展指令
        actions = XIAOAI_EXTENSION_COMMAND_MAP.get(text, [])
        if actions:
            print(f"接收到小爱扩展指令: '{text}'")
            await interrupt_xiaoai(speaker)
            await _execute_actions(actions)
        return False

    return False


async def _after_wakeup(speaker: SpeakerProtocol):
    """设备从“唤醒”状态退出时调用。"""
    await speaker.play(text="主人再见")


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

#TODO: 封装上面的加载器，将用户配置和APP_CONFIG生成独立开来，方便用户自定义

print("✅ Oxa-Server 配置加载完成。")
