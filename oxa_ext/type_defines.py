from typing import Dict, Literal, Optional, Protocol, TypedDict, Awaitable, Callable


class CommandResult(TypedDict):
    stdout: str
    stderr: str
    exit_code: int


class SpeakerProtocol(Protocol):
    """SpeakerManager 的接口协议，定义了所有可用的方法和属性"""

    status: Literal["playing", "paused", "idle"]
    """当前播放状态"""

    async def get_playing(self,
                          sync: bool = False
                          ) -> Literal["playing", "paused", "idle"]:
        """
        获取播放状态
        
        Args:
            sync: 是否同步远端最新状态
        Returns:
            当前播放状态
        """
        ...

    async def set_playing(self, playing: bool = True) -> bool:
        """
        播放/暂停
        
        Args:
            playing: True 为播放，False 为暂停
        Returns:
            操作是否成功
        """
        ...

    async def play(
        self,
        text: Optional[str] = None,
        url: Optional[str] = None,
        buffer: Optional[bytes] = None,
        blocking: bool = True,
        timeout: int = 10 * 60 * 1000,
    ) -> bool:
        """
        播放文字、音频链接、音频流
        
        Args:
            text: 文字内容
            url: 音频链接
            buffer: 音频流
            timeout: 超时时长（毫秒），默认10分钟
            blocking: 是否阻塞运行(仅对播放文字、音频链接有效)
        Returns:
            操作是否成功
        """
        ...

    async def wake_up(self, awake: bool = True, silent: bool = True) -> bool:
        """
        （取消）唤醒小爱
        
        Args:
            awake: 是否唤醒
            silent: 是否静默唤醒
        Returns:
            操作是否成功
        """
        ...

    async def ask_xiaoai(self, text: str, silent: bool = False) -> bool:
        """
        把文字指令交给原来的小爱执行
        
        Args:
            text: 文字指令
            silent: 是否静默执行
        Returns:
            操作是否成功
        """
        ...

    async def abort_xiaoai(self) -> bool:
        """
        中断原来小爱的运行
        
        注意：重启需要大约 1-2s 的时间，在此期间无法使用小爱音箱自带的 TTS 服务
        Returns:
            操作是否成功
        """
        ...

    async def get_boot(self) -> str:
        """
        获取启动分区
        Returns:
            启动分区信息
        """
        ...

    async def set_boot(self, boot_part: Literal["boot0", "boot1"]) -> bool:
        """
        设置启动分区
        
        Args:
            boot_part: 启动分区名称
        Returns:
            操作是否成功
        """
        ...

    async def get_device(self) -> Dict[str, str]:
        """
        获取设备型号、序列号信息
        
        Returns:
            包含设备型号和序列号的字典
        """
        ...

    async def get_mic(self) -> Literal["on", "off"]:
        """
        获取麦克风状态
        
        Returns:
            麦克风状态
        """
        ...

    async def set_mic(self, on: bool = True) -> bool:
        """
        打开/关闭麦克风
        
        Args:
            on: True 为打开，False 为关闭
        Returns:
            操作是否成功
        """
        ...

    async def run_shell(self,
                        script: str,
                        timeout: int = 10000) -> CommandResult:
        """
        执行脚本
        
        Args:
            script: 脚本内容
            timeout: 超时时间（毫秒）
        Returns:
            包含标准输出、标准错误和退出码的字典
        """
        ...


Actions = list[str | Callable[[SpeakerProtocol], Awaitable[None]]]
