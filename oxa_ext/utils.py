from oxa_ext.type_defines import SpeakerProtocol, Actions
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


async def interrupt_xiaoai(speaker: SpeakerProtocol):
    """
    中断小爱同学当前的对话或播放，并等待其服务重启。
    这是一个公共函数，用于在自定义指令执行前“清场”。
    """
    await speaker.abort_xiaoai()
    await asyncio.sleep(2)
