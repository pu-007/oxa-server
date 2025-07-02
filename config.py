import asyncio
import os
import subprocess


def ensure_dependencies(requirements: list[str]):
    import importlib.util
    missing_packages = [
        pkg for pkg in requirements if not importlib.util.find_spec(pkg)
    ]

    if not missing_packages:
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    python = os.path.join(script_dir, '.venv', "bin", 'python')
    subprocess.run([python, "-m", "ensurepip"])
    subprocess.run([python, "-m", "pip", "install", *missing_packages])


ensure_dependencies([
    "wakeonlan",
    # "mijiaAPI",
    # "yt-dlp",
])

kws_wakeup = ["小智小智"]
kws_command = [
    "切换电视", "打开空调", "关闭空调", "打开风扇", "关闭风扇", "切换主灯", "打开台灯", "关闭台灯", "关闭副灯",
    "打开副灯", "点亮外面", "熄灭外面", "全部关闭"
]
kws_pc_control = ["打开电脑", "切换屏幕", "关闭电脑", "重启电脑", "按下空格"]


async def xiaomusic_handler(speaker, text):
    pass


async def _pause_xiaoai(speaker):
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)


async def kws_handler(speaker, text):
    match text:
        case "小智小智":
            await speaker.play(text="小智来了")
            return True
        # kws_command
        case "切换电视":
            await speaker.ask_xiaoai(text="关闭电视", silent=True)
        case "打开空调":
            await speaker.ask_xiaoai(text="打开空调", silent=True)
        case "关闭空调":
            await speaker.ask_xiaoai(text="关闭空调", silent=True)
        case "打开风扇":
            await speaker.ask_xiaoai(text="打开风扇", silent=True)
        case "关闭风扇":
            await speaker.ask_xiaoai(text="关闭风扇", silent=True)
        case "切换主灯":
            await speaker.ask_xiaoai(text="关闭主灯", silent=True)
        case "打开台灯":
            await speaker.ask_xiaoai(text="打开台灯", silent=True)
        case "关闭台灯":
            await speaker.ask_xiaoai(text="关闭台灯", silent=True)
        case "关闭副灯":
            await speaker.ask_xiaoai(text="关闭副灯", silent=True)
        case "打开副灯":
            await speaker.ask_xiaoai(text="打开副灯", silent=True)
        case "点亮外面":
            await speaker.ask_xiaoai(text="打开台灯", silent=True)
            await speaker.ask_xiaoai(text="打开副灯", silent=True)
        case "熄灭外面":
            await speaker.ask_xiaoai(text="关闭台灯", silent=True)
            await speaker.ask_xiaoai(text="关闭副灯", silent=True)
        case "全部关闭":
            await speaker.ask_xiaoai(text="关闭空调", silent=True)
            await speaker.ask_xiaoai(text="关闭风扇", silent=True)
            await speaker.ask_xiaoai(text="关闭主灯", silent=True)
            await speaker.ask_xiaoai(text="关闭台灯", silent=True)
            await speaker.ask_xiaoai(text="关闭副灯", silent=True)
        # kws_pc_control
        case "打开电脑":
            await speaker.play(text="正在唤醒电脑")
            from wakeonlan import send_magic_packet
            # TODO: fix
            send_magic_packet("08BFB8A67CE2", ip_address="192.168.100.199")
        case "切换屏幕":
            await speaker.ask_xiaoai(text="我的电脑设置为三", silent=True)
        case "按下空格":
            await speaker.ask_xiaoai(text="我的电脑设置为七", silent=True)


async def xiaoai_handler(speaker, text):
    match text:
        case "召唤小智":
            await _pause_xiaoai(speaker)
            await speaker.play(text="小智来了")
            return True


async def before_wakeup(speaker, text, source):
    match source:
        case "kws":
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
        "keywords": [*kws_wakeup, *kws_command, *kws_pc_control],
        # 静音多久后自动退出唤醒（秒）
        "timeout": 5,
        # 语音识别结果回调
        "before_wakeup": before_wakeup,
        # 退出唤醒时的提示语（设置为空可关闭）
        "after_wakeup": after_wakeup,
    },
    "vad": {
        # 录音音量增强倍数（小爱音箱录音音量较小，需要后期放大一下）
        "boost": 130,
        # 语音检测阈值（0-1，越小越灵敏）
        "threshold": 0.35,
        # 最小语音时长（ms）
        "min_speech_duration": 1000,
        # 最小静默时长（ms）
        "min_silence_duration": 1000,
    },
    # "xiaozhi": {
    #     "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",
    #     "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",
    #     "WEBSOCKET_ACCESS_TOKEN": "",  #（可选）一般用不到这个值
    #     "DEVICE_ID": "70:70:fc:05:83:fa",  #（可选）默认自动生成
    #     "VERIFICATION_CODE": "477868",  # 首次登陆时，验证码会在这里更新
    # },
    "xiaozhi": {
        "OTA_URL": "",
        "WEBSOCKET_URL": "",
        "WEBSOCKET_ACCESS_TOKEN": "",  #（可选）一般用不到这个值
        "DEVICE_ID": "70:70:fc:05:83:fa",  #（可选）默认自动生成
        "VERIFICATION_CODE": "",  # 首次登陆时，验证码会在这里更新
    },
}
