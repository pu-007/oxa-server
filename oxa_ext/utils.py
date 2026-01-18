from oxa_ext.type_defines import SpeakerProtocol, Actions, ActionFunction
from typing import Any, Literal, Optional
import os
import subprocess
import asyncio


def map_all_to(keys: tuple[str, ...], value: Actions) -> dict[str, Actions]:
    return {key: value for key in keys}


def ensure_dependencies(requirements: list[str]):
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


def map_the_switches(*devices: str,
                     type: Literal["on", "off", "all"] = "all") -> dict:
    """
    根据一个包含设备名称的列表，生成对应的开关指令字典。

    Args:
        device_list (list): 一个包含设备名称字符串的列表，例如 ["空调", "风扇"]。

    Returns:
        dict: 一个包含“开”和“关”指令的字典。
    """
    command_dict = {}
    for device in devices:
        # 使用 f-string 格式化字符串，代码更简洁易读

        # 生成“开”指令
        if type == "on" or type == "all":
            on_key = f"请开{device}"
            on_value = [f"打开{device}"]
            command_dict[on_key] = on_value

        # 生成“关”指令
        if type == "off" or type == "all":
            off_key = f"请关{device}"
            off_value = [f"关闭{device}"]
            command_dict[off_key] = off_value

    return command_dict


def switch_cmds(*devices: str,
                type: Literal["on", "off", "all"] = "all") -> list:
    """
    快速生成开关设备的小爱原生指令列表。
    """
    commands = []
    for device in devices:
        if type == "on" or type == "all":
            commands.append(f"打开{device}")
        if type == "off" or type == "all":
            commands.append(f"关闭{device}")
    return commands


def off(*devices: str) -> list:
    """
    快速生成关闭设备的小爱原生指令列表。
    """
    return switch_cmds(*devices, type="off")


def on(*devices: str) -> list:
    """
    快速生成打开设备的小爱原生指令列表。
    """
    return switch_cmds(*devices, type="on")


async def interrupt_xiaoai(speaker: SpeakerProtocol):
    """
    中断小爱同学当前的对话或播放，并等待其服务重启。
    这是一个公共函数，用于在自定义指令执行前“清场”。
    """
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)


def wol(computer_mac: str, broadcast_ip: str) -> ActionFunction:
    """
    发送网络唤醒 (Wake-on-LAN) 魔法包来启动电脑。
    请确保已安装 'wakeonlan' 库，并替换为您的 MAC 地址和广播 IP。
    """
    ensure_dependencies(["wakeonlan"])

    async def wake_up_computer(_: SpeakerProtocol):
        from wakeonlan import send_magic_packet
        await asyncio.to_thread(send_magic_packet,
                                computer_mac,
                                ip_address=broadcast_ip)
        print(f"已向 {computer_mac} 发送网络唤醒包。")

    return wake_up_computer


def xiaoai_play(
    text: Optional[str] = None,
    url: Optional[str] = None,
    buffer: Optional[bytes] = None,
    blocking: bool = True,
    timeout: int = 10 * 60 * 1000,
):

    async def _play(speaker: SpeakerProtocol):
        await speaker.play(text, url, buffer, blocking, timeout)

    return _play


def hass_action(url: str, token: str, domain: str, service: str,
                entity_id: str) -> ActionFunction:
    """
    调用 Home Assistant 的 REST API 服务。
    """
    ensure_dependencies(["aiohttp"])

    async def _call_hass(_: SpeakerProtocol):
        import aiohttp
        api_url = f"{url.rstrip('/')}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {"entity_id": entity_id}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers,
                                        json=payload) as response:
                    if response.status == 200:
                        print(f"HASS 指令成功: {domain}.{service} -> {entity_id}")
                    else:
                        text = await response.text()
                        print(f"HASS 指令失败 ({response.status}): {text}")
        except Exception as e:
            print(f"HASS 请求异常: {e}")

    return _call_hass


class AppConfigBuilder:
    """
    一个用于构建 APP_CONFIG 的构建器类。

    它通过创建闭包来生成回调函数，以确保回调函数在被外部系统调用时
    （即使不传递 self），也能正确访问类的实例数据。
    """

    # ... __init__ 方法和之前一样，保持不变 ...
    def __init__(
        self,
        # --- 核心指令和关键词常量 ---
        direct_vad_wakeup_keywords: list[str],
        direct_vad_command_map: dict[str, Actions],
        xiaoai_wakeup_keywords: list[str],
        xiaoai_extension_command_map: dict[str, Actions],

        # --- 基础配置字典 ---
        vad_config: dict[str, Any],
        xiaozhi_config: dict[str, Any],

        # --- 可选的微调参数 ---
        wakeup_timeout: int = 5,
        on_wakeup_play_text: str = "小智来了",
        on_execute_play_text: str = "已执行",
        on_exit_play_text: str = "主人再见",
    ):
        """初始化构建器，仅保存用户定义的常量和配置。"""
        self.direct_vad_wakeup_keywords = direct_vad_wakeup_keywords
        self.direct_vad_command_map = direct_vad_command_map
        self.xiaoai_wakeup_keywords = xiaoai_wakeup_keywords
        self.xiaoai_extension_command_map = xiaoai_extension_command_map
        self.vad_config = vad_config
        self.xiaozhi_config = xiaozhi_config
        self.wakeup_timeout = wakeup_timeout
        self.on_wakeup_play_text = on_wakeup_play_text
        self.on_execute_play_text = on_execute_play_text
        self.on_exit_play_text = on_exit_play_text

    async def _execute_actions(self, speaker: SpeakerProtocol,
                               actions: Actions):
        """辅助方法，用于执行一系列指令动作。"""
        # ... 此方法逻辑不变 ...
        for action in actions:
            if isinstance(action, str):
                print(f"  -> 执行小爱原生指令: '{action}'")
                await speaker.ask_xiaoai(text=action, silent=True)
            elif callable(action):
                print(
                    f"  -> 执行自定义函数: {getattr(action, '__name__', 'unknown_function')}"
                )
                await action(speaker)
            await asyncio.sleep(0.2)

    async def _internal_before_wakeup(self, speaker: SpeakerProtocol,
                                      text: str, source: str) -> bool:
        """回调的内部实现，它需要 self。"""
        if source == "kws":
            if text in self.direct_vad_wakeup_keywords:
                if self.on_wakeup_play_text:
                    await speaker.play(text=self.on_wakeup_play_text)
                return True
            actions = self.direct_vad_command_map.get(text)
            if actions:
                print(f"接收到直接VAD指令: '{text}'")
                await self._execute_actions(speaker, actions)
                if self.on_execute_play_text:
                    await speaker.play(text=self.on_execute_play_text)
            return False
        elif source == "xiaoai":
            if text in self.xiaoai_wakeup_keywords:
                await interrupt_xiaoai(speaker)
                if self.on_wakeup_play_text:
                    await speaker.play(text=self.on_wakeup_play_text)
                return True
            actions = self.xiaoai_extension_command_map.get(text)
            if actions:
                print(f"接收到小爱扩展指令: '{text}'")
                await interrupt_xiaoai(speaker)
                await self._execute_actions(speaker, actions)
            return False
        return False

    async def _internal_after_wakeup(self, speaker: SpeakerProtocol):
        """设备从“唤醒”状态退出时调用的内部实现。"""
        if self.on_exit_play_text:
            await speaker.play(text=self.on_exit_play_text)

    def build(self) -> dict[str, Any]:
        """组装并返回最终的 APP_CONFIG 字典。"""

        # 创建包装器函数 (闭包)
        # 这个 wrapper 函数可以访问 `self`，但它自身的签名没有 `self`
        async def before_wakeup_wrapper(speaker: SpeakerProtocol, text: str,
                                        source: str) -> bool:
            # 当外部调用 wrapper 时，它会调用我们真正的内部方法，并把 self 传进去
            return await self._internal_before_wakeup(speaker, text, source)

        async def after_wakeup_wrapper(speaker: SpeakerProtocol):
            return await self._internal_after_wakeup(speaker)

        # -------------------------------------------------------------------

        all_vad_keywords = [
            *self.direct_vad_wakeup_keywords,
            *list(self.direct_vad_command_map.keys())
        ]

        wakeup_config = {
            "keywords": all_vad_keywords,
            "timeout": self.wakeup_timeout,
            "before_wakeup": before_wakeup_wrapper,  # 使用新的包装器
            "after_wakeup": after_wakeup_wrapper,  # 使用新的包装器
        }

        return {
            "vad": self.vad_config,
            "xiaozhi": self.xiaozhi_config,
            "wakeup": wakeup_config,
        }
