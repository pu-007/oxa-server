# -*- coding: utf-8 -*-
"""
Oxa-Server 配置模板

欢迎使用 Oxa-Server！这是一个功能强大的小爱同学增强工具。
请将此文件复制为 `config.py`，然后根据您的需求修改其中的配置。

核心理念是“数据驱动”：您只需修改本文件中的 Python 字典和列表，
即可轻松定制免唤醒指令、组合指令和自定义函数，无需深入代码细节。
"""
import asyncio

# 从扩展模块导入必要的工具函数和类型定义
# - SpeakerProtocol: 音箱控制接口的类型提示，用于自定义函数。
# - Actions: 指令动作的类型，可以是字符串或异步函数。
# - ensure_dependencies: 自动安装缺失的 Python 库。
# - map_all_to: 将多个语音指令映射到同一组动作。
# - map_the_switches: 快速为设备生成“开/关”指令。
# - interrupt_xiaoai: 在执行自定义指令前，中断小爱同学的当前任务。
from oxa_ext.type_defines import SpeakerProtocol, Actions
from oxa_ext.utils import ensure_dependencies, map_all_to, map_the_switches, interrupt_xiaoai


# ==============================================================================
#  sección 1: 主要应用配置 (Primary Application Configuration)
# ==============================================================================
# 请在此处修改您的核心配置信息。

# --- 语音活动检测 (VAD) 配置 ---
# 用于判断用户是否开始或停止说话，通常无需修改。
VAD_CONFIG = {
    "boost": 200,  # 音频增益
    "threshold": 0.1,  # 语音检测阈值
    "min_speech_duration": 1000,  # 最短语音时长 (毫秒)
    "min_silence_duration": 1000,  # 语音结束后最短静音时长 (毫秒)
}

# --- 小智云服务配置 ---
# 用于连接 open-xiaoai 的云端服务。
# 重要：请务必将 DEVICE_ID 替换为您的真实设备ID。
XIAOZHI_CONFIG = {
    "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",  # OTA 更新服务器地址
    "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",  # WebSocket 通信地址
    "WEBSOCKET_ACCESS_TOKEN": "",  # WebSocket 访问令牌 (通常为空)
    "DEVICE_ID": "YOUR_DEVICE_ID_HERE",  # <<<--- 必须修改：您的设备唯一ID (MAC地址)
    "VERIFICATION_CODE": "699244",  # 设备验证码 (通常无需修改)
}


# ==============================================================================
# sección 2: 自定义功能实现 (Custom Function Implementations)
# ==============================================================================
# 在这里定义您的自定义异步函数，它们可以被指令映射表调用。

async def wake_up_computer(speaker: SpeakerProtocol):
    """
    示例函数：发送网络唤醒 (Wake-on-LAN) 魔法包来启动电脑。
    - 依赖: `wakeonlan` 库 (脚本会自动安装)
    - 参数: `speaker` (由系统自动传入，您无需关心)
    """
    # 1. 声明此函数需要的第三方库，脚本会自动检查和安装
    ensure_dependencies(["wakeonlan"])

    # 2. 定义您自己的参数
    computer_mac = "YOUR_COMPUTER_MAC_ADDRESS"  # <<<--- 修改为您的电脑MAC地址
    subnet_broadcast_ip = "192.168.100.255"  # <<<--- 修改为您的局域网广播地址

    # 3. 导入并执行核心逻辑
    from wakeonlan import send_magic_packet
    # 使用 asyncio.to_thread 在异步环境中运行同步的库函数
    await asyncio.to_thread(send_magic_packet,
                            computer_mac,
                            ip_address=subnet_broadcast_ip)
    print(f"已向 {computer_mac} 发送网络唤醒包。")
    # (可选) 让小爱同学给出语音反馈
    await speaker.play("好的，正在尝试启动电脑")


# ==============================================================================
# sección 3: 指令映射表 (Command Maps)
# ==============================================================================
# 这是整个系统的核心，将您的语音指令映射到具体操作。

# --- 模式一：直接VAD唤醒指令 (免唤醒) ---
# 无需说“小爱同学”，直接说出关键词即可触发。

# 1. 定义一个“超级唤醒词”，用于激活小智，使其准备接收正式指令。
DIRECT_VAD_WAKEUP_KEYWORDS = ["小智小智"]

# 2. 定义免唤醒指令。
#    - 键 (Key): 您对小爱说的语音指令 (字符串)。
#    - 值 (Value): 一个动作列表 (Actions)。动作可以是：
#      a) 小爱同学的原生指令 (字符串)。
#      b) 您在上面定义的自定义异步函数名。
DIRECT_VAD_COMMAND_MAP: dict[str, Actions] = {
    # 示例 1: 单一指令映射
    # "打开电视" -> 执行小爱原生指令 "打开电视"
    "打开电视": ["打开电视"],

    # 示例 2: 多指令映射 (使用 map_all_to 简化)
    # "关闭电视" 或 "关掉电视" -> 执行小爱原生指令 "关闭电视"
    **map_all_to(("关闭电视", "关掉电视"), ["关闭电视"]),

    # 示例 3: 组合指令 (链式操作)
    # "我出门了" -> 先关主灯，再关电视
    "我出门了": ["关闭主灯", "关闭电视"],

    # 示例 4: 调用自定义函数
    # "打开电脑" -> 调用上面定义的 wake_up_computer 函数
    "打开电脑": [wake_up_computer],

    # 示例 5: 混合指令 (原生指令 + 自定义函数)
    # "我到家了" -> 先开电脑，再说“欢迎回家”
    "我到家了": [wake_up_computer, "欢迎回家"],

    # 示例 6: 使用 map_the_switches 快速生成开关指令
    # 这会自动创建 "打开空调"、"关闭空调"、"打开风扇"、"关闭风扇" 等指令
    **map_the_switches("空调", "风扇", "主灯", "台灯", "副灯"),
}


# --- 模式二：小爱对话中继指令 ---
# 在与“小爱同学”正常对话时，说出特定词语来触发特殊操作。

# 1. 定义在对话中召唤小智的关键词。
XIAOAI_WAKEUP_KEYWORDS = ["召唤小智", "呼叫小智"]

# 2. 定义扩展指令。
XIAOAI_EXTENSION_COMMAND_MAP: dict[str, Actions] = {
    # 示例：当您对小爱说“帮我打开电脑”时...
    "帮我打开电脑": [
        # a) 先中断小爱，避免它说“我没听懂”
        interrupt_xiaoai,
        # b) 然后执行您的自定义函数
        wake_up_computer
    ],
}