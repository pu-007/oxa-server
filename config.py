import asyncio
import os
import subprocess
from typing import Dict, List, Callable, Awaitable

# --- 命令映射表 (数据驱动核心) ---
KWS_WAKEUP = ["小智小智"]


async def wake_up_computer(_):
    """
    发送网络唤醒 (Wake-on-LAN) 魔法包来启动电脑。
    """
    _ensure_dependencies(["wakeonlan"])

    computer_mac = "08BFB8A67CE2"
    subnet_broadcast_ip = "192.168.100.255"

    from wakeonlan import send_magic_packet

    await asyncio.to_thread(send_magic_packet,
                            computer_mac,
                            ip_address=subnet_broadcast_ip)


COMMAND_MAP: Dict[str, List[str | Callable | Awaitable]] = {
    # 小爱原生指令
    "切换电视": ["打开电视"],
    "请开空调": ["打开空调"],
    "请关空调": ["关闭空调"],
    "空调升速": ["空调风速升高"],
    "空调降速": ["空调风速降低"],
    "请开风扇": ["打开风扇"],
    "请关风扇": ["关闭风扇"],
    "切换主灯": ["打开主灯"],
    "请开台灯": ["打开台灯"],
    "请关台灯": ["关闭台灯"],
    "请关副灯": ["关闭副灯"],
    "请开副灯": ["打开副灯"],
    "切换色温": ["色温分段"],
    "打开夜灯": ["昏暗模式"],
    "空调降温": ["空调温度降低"],
    "空调升温": ["空调温度升高"],
    "风扇定时": ["定时风扇"],

    # 组合指令
    "点亮外面": ["打开台灯", "打开副灯"],
    "熄灭外面": ["关闭台灯", "关闭副灯"],
    "关灯空调": ["关闭主灯", "关闭台灯", "关闭副灯", "关闭空调"],
    "灯光全灭": ["关闭主灯", "关闭台灯", "关闭副灯"],
    "全部关闭": ["关闭空调", "关闭风扇", "关闭主灯", "关闭电视", "关闭我的电脑", "关闭台灯", "关闭副灯"],

    # PC 控制 & 特殊指令
    "请开电脑": [wake_up_computer],
    "切换屏幕": ["我的电脑设置为三"],
    "请关电脑": ["关闭我的电脑"],
    "重启电脑": ["我的电脑设置为一"],
    "测试电脑": ["我的电脑设置为七"],  # 按下空格

    # 混合指令
    "联合启动": [wake_up_computer, "打开电视"],
    "联合关闭": ["关闭我的电脑", "关闭电视"],
}


# --- 辅助函数 ---
async def _pause_xiaoai(speaker):
    """中断小爱并等待服务重启。"""
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)


def _ensure_dependencies(requirements: list[str]):
    """检查并安装缺失的 Python 依赖包。"""
    import importlib.util
    missing_packages = [
        pkg for pkg in requirements if not importlib.util.find_spec(pkg)
    ]

    if not missing_packages:
        return

    print(f"检测到缺失的依赖: {missing_packages}，正在尝试安装...")
    # 假设脚本在一个虚拟环境目录的父目录中运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_executable = os.path.join(script_dir, '.venv', "bin", 'python')
    if not os.path.exists(python_executable):
        # 如果找不到虚拟环境的 python，就使用系统默认的 python
        import sys
        python_executable = sys.executable
        print(f"未找到虚拟环境，使用系统 Python: {python_executable}")

    subprocess.run([python_executable, "-m", "ensurepip"], check=False)
    subprocess.run(
        [python_executable, "-m", "pip", "install", *missing_packages],
        check=True)
    print("依赖安装完成。")


# --- 事件处理器 ---
async def _kws_handler(speaker, text):
    """统一处理所有自定义关键词命令。"""
    actions = COMMAND_MAP[text]
    for action in actions:
        if isinstance(action, str):
            await speaker.ask_xiaoai(text=action, silent=True)
        elif callable(action):
            await action(speaker)
        await asyncio.sleep(0.2)  # 防止指令发送过快

    await speaker.play(text="已执行")


async def _xiaoai_handler(speaker, text):
    """处理来自小爱原生对话的特定指令。"""
    if text == "召唤小智":
        await _pause_xiaoai(speaker)
        await speaker.play(text="小智来了")
        return True


async def _before_wakeup(speaker, text, source):
    """在进入唤醒状态前的主回调函数。"""
    if source == "kws":
        if text in KWS_WAKEUP:
            await speaker.play(text="小智来了")
            return True
        return await _kws_handler(speaker, text)
    elif source == "xiaoai":
        return await _xiaoai_handler(speaker, text)


async def _after_wakeup(speaker):
    """退出唤醒状态时调用。"""
    await speaker.play(text="主人再见")


# --- APP 总配置 ---
ALL_COMMAND_KWS = list(COMMAND_MAP.keys())

APP_CONFIG = {
    "wakeup": {
        "keywords": [*KWS_WAKEUP, *ALL_COMMAND_KWS],
        "timeout": 5,
        "before_wakeup": _before_wakeup,
        "after_wakeup": _after_wakeup,
    },
    "vad": {
        "boost": 100,
        "threshold": 0.1,
        "min_speech_duration": 1000,
        "min_silence_duration": 1000,
    },
    "xiaozhi": {
        "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",
        "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",
        "WEBSOCKET_ACCESS_TOKEN": "",
        "DEVICE_ID": "70:70:fc:05:83:fa",
        "VERIFICATION_CODE": "477868",
    },
}
