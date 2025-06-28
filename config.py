import asyncio

kws_wakeup = ["小智小智"]
# The handlers that actually performs the functionality is defined in kws_handler.
kws_command = ["唤醒电脑", "打开空调", "播放音乐"]


async def _pause_xiaoai(speaker):
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)


async def kws_handler(speaker, text):
    """
    用于处理关键字唤醒后的一级指令
    """
    # cases must in kws_command
    match text:
        case "唤醒电脑":
            from custom_modules import wol

            await speaker.play(text="正在唤醒电脑")
            await wol.wake_on_lan("08:BF:B8:A6:7C:E2")
        case "打开空调":
            await speaker.ask_xiaoai(text="打开空调")
        case "播放音乐":
            from custom_modules import xiaomusic

            await _pause_xiaoai(speaker)
            await xiaomusic.xiaomusic_handler(speaker, text)
        # TODO: 计算机控制
        # 方案一：依赖巴法云 mqtt (曾经的 cut in xiaoai 项目)
        # 方案二：用 fastapi 沟通客户端直接通信


async def xiaoai_handler(speaker, text):
    """
    用于处理小爱同学唤醒后收到的二级指令，可以介入小爱的对话流
    """
    match text:
        case "召唤小智":
            await _pause_xiaoai(speaker)
            await speaker.play(text="小智来了")
            # 返回 True 唤醒小智 AI
            # 更多功能可以在 xiaozhi_esp32_server 控制台的智能体中定义
            # 还可以通过 MCP 实现更多种功能，未来可期
            return True
        case "强制中断":
            await _pause_xiaoai(speaker)
            await speaker.set_playing(False)
            await speaker.play(text="已强制中断")


async def before_wakeup(speaker, text, source):
    """
    处理收到的用户消息，并决定是否唤醒小智 AI

    - source: 唤醒来源
        - 'kws': 关键字唤醒
        - 'xiaoai': 小爱同学收到用户指令
    """

    match source:
        case "kws":
            # 如果是唤醒词就直接唤醒小智，跳过其他流程
            if text in kws_wakeup:
                await speaker.play(text="小智来了")
                return True
            return await kws_handler(speaker, text)
        case "xiaoai":
            return await xiaoai_handler(speaker, text)


async def after_wakeup(speaker):
    """
    退出唤醒状态
    """
    await speaker.play(text="主人再见")


APP_CONFIG = {
    "wakeup": {
        # 自定义唤醒词列表（英文字母要全小写）
        "keywords": [*kws_wakeup, *kws_command],
        # 静音多久后自动退出唤醒（秒）
        "timeout": 10,
        # 语音识别结果回调
        "before_wakeup": before_wakeup,
        # 退出唤醒时的提示语（设置为空可关闭）
        "after_wakeup": after_wakeup,
    },
    "vad": {
        # 录音音量增强倍数（小爱音箱录音音量较小，需要后期放大一下）
        "boost": 10,
        # 语音检测阈值（0-1，越小越灵敏）
        "threshold": 0.10,
        # 最小语音时长（ms）
        "min_speech_duration": 250,
        # 最小静默时长（ms）
        "min_silence_duration": 500,
    },
    "xiaozhi": {
        "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",
        "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",
        "WEBSOCKET_ACCESS_TOKEN": "",  #（可选）一般用不到这个值
        "DEVICE_ID": "70:70:fc:05:83:fa",  #（可选）默认自动生成
        "VERIFICATION_CODE": "623519",  # 首次登陆时，验证码会在这里更新
    },
}
