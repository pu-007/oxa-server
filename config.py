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
# 将“打开xx”和“关闭xx”等指令统一修改为“请开/关xx”
kws_command = [
    "切换电视", "请开空调", "请关空调", "请开风扇", "请关风扇", "切换主灯", "请开台灯", "请关台灯", "请关副灯",
    "请开副灯", "点亮外面", "熄灭外面", "全部关闭", "切换色温", "打开夜灯", "灯光全灭", "空调降温", "空调升温"
]
kws_pc_control = ["打开电脑", "切换屏幕", "关闭电脑", "重启电脑", "按下空格", "联合启动", "联合关闭"]
computer_mac = "08BFB8A67CE2"  # 电脑的MAC地址


async def _pause_xiaoai(speaker):
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)


async def _wake_up_computer():
    # TODO: fix invalid
    from wakeonlan import send_magic_packet
    await asyncio.to_thread(send_magic_packet,
                            computer_mac,
                            ip_address="192.168.100.199")


async def kws_handler(speaker, text):
    match text:
    # kws_command
        case "切换电视":
            # 关闭/打开电视
            await speaker.ask_xiaoai(text="关闭电视", silent=True)
        case "请开空调":
            await speaker.ask_xiaoai(text="打开空调", silent=True)
        case "请关空调":
            await speaker.ask_xiaoai(text="关闭空调", silent=True)
        case "请开风扇":
            await speaker.ask_xiaoai(text="打开风扇", silent=True)
        case "请关风扇":
            await speaker.ask_xiaoai(text="关闭风扇", silent=True)
        case "切换主灯":
            # 关闭/打开主灯
            await speaker.ask_xiaoai(text="关闭主灯", silent=True)
        case "请开台灯":
            await speaker.ask_xiaoai(text="打开台灯", silent=True)
        case "请关台灯":
            await speaker.ask_xiaoai(text="关闭台灯", silent=True)
        case "请关副灯":
            await speaker.ask_xiaoai(text="关闭副灯", silent=True)
        case "请开副灯":
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
            await speaker.ask_xiaoai(text="关闭电视", silent=True)
            await speaker.ask_xiaoai(text="关闭我的电脑", silent=True)
            await speaker.ask_xiaoai(text="关闭台灯", silent=True)
            await speaker.ask_xiaoai(text="关闭副灯", silent=True)
        case "灯光全灭":
            await speaker.ask_xiaoai(text="关闭主灯", silent=True)
            await speaker.ask_xiaoai(text="关闭台灯", silent=True)
            await speaker.ask_xiaoai(text="关闭副灯", silent=True)
        case "切换色温":
            await speaker.ask_xiaoai(text="色温分段", silent=True)
        case "打开夜灯":
            await speaker.ask_xiaoai(text="昏暗模式", silent=True)
        case "空调降温":
            await speaker.ask_xiaoai(text="空调温度降低", silent=True)
        case "空调升温":
            await speaker.ask_xiaoai(text="空调温度升高", silent=True)
        # kws_pc_control
        # TODO: 与 cut_in_xiaoai pc 控制端联动，直接读取 commands_table 并解析
        case "打开电脑":
            await speaker.play(text="正在唤醒电脑")
            await _wake_up_computer()
        case "切换屏幕":
            await speaker.ask_xiaoai(text="我的电脑设置为三", silent=True)
        case "关闭电脑":
            await speaker.ask_xiaoai(text="关闭我的电脑", silent=True)
        case "重启电脑":
            await speaker.ask_xiaoai(text="我的电脑设置为一", silent=True)
        case "按下空格":
            await speaker.ask_xiaoai(text="我的电脑设置为七", silent=True)
        case "联合启动":
            await _wake_up_computer()
            await speaker.ask_xiaoai(text="打开电视", silent=True)
        case "联合关闭":
            await speaker.ask_xiaoai(text="关闭我的电脑", silent=True)
            await speaker.ask_xiaoai(text="关闭电视", silent=True)


async def xiaoai_handler(speaker, text):
    # 暂时用 xiaomuisc 替代该功能
    # # 新增case：处理“智能音乐”开头的指令
    # if text.startswith("智能音乐"):
    #     # 提取“智能音乐”后面的文本作为音乐名称，并去除前后空格
    #     music_name = text[len("智能音乐"):].strip()
    #     if music_name:  # 确保提取的音乐名称不为空
    #         await _pause_xiaoai(speaker)
    #         await xiaomusic_handler(speaker, music_name)
    #         return True  # 表示指令已成功处理

    match text:
        case "召唤小智":
            await _pause_xiaoai(speaker)
            await speaker.play(text="小智来了")
            return True


async def before_wakeup(speaker, text, source):
    match source:
        case "kws":
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
    "xiaozhi": {
        "OTA_URL": "https://2662r3426b.vicp.fun/xiaozhi/ota/",
        "WEBSOCKET_URL": "wss://2662r3426b.vicp.fun/xiaozhi/v1/",
        "WEBSOCKET_ACCESS_TOKEN": "",  #（可选）一般用不到这个值
        "DEVICE_ID": "70:70:fc:05:83:fa",  #（可选）默认自动生成
        "VERIFICATION_CODE": "477868",  # 首次登陆时，验证码会在这里更新
    },
    # "xiaozhi": {
    #     "OTA_URL": "",
    #     "WEBSOCKET_URL": "",
    #     "WEBSOCKET_ACCESS_TOKEN": "",  #（可选）一般用不到这个值
    #     "DEVICE_ID": "70:70:fc:05:83:fa",  #（可选）默认自动生成
    #     "VERIFICATION_CODE": "",  # 首次登陆时，验证码会在这里更新
    # },
}
