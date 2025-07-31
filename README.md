# Oxa-Server: 小爱同学 Docker 定制增强脚本

[中文](#中文) | [English](#english)

---

## 中文 <a name="中文"></a>

### 简介

本项目是一个基于 [open-xiaoai](https://github.com/idootop/open-xiaoai) 项目 `xiaozhi` 示例的深度定制增强方案。

它旨在通过 Docker Volume 挂载的方式，以**最小的侵入性**，极大地增强和自定义小爱同学的功能。你无需修改原版 Docker 镜像，只需在官方运行命令的基础上，额外挂载你自己的 `config.py` 文件和 `oxa_ext` 扩展目录，即可实现免唤醒、组合指令、执行自定义 Python 代码等高级功能。

### ✨ 特性

- **最小侵入**：只需额外挂载 `config.py` 和 `oxa_ext` 目录，即可在原版功能基础上无缝增强。
- **结构化配置**：使用 `AppConfigBuilder` 构建器，配置逻辑更清晰、更易于维护。
- **免唤醒指令**：将常用指令配置为免唤醒关键词，直接说出即可执行，无需先说 "小爱同学"。
- **强大的指令映射**：轻松将一句口语指令映射到一个或多个动作（原生指令或自定义函数）。
- **Python 函数无缝集成**：可以直接在指令中调用自定义的 Python 函数（同步或异步），实现网络唤醒（WOL）、API 调用、执行 Shell 命令等复杂操作。
- **依赖自动安装**：如果自定义函数需要新的 Python 包，脚本会自动尝试安装，简化部署。

### 🚀 如何使用

#### 1. 准备工作：成功运行原版 `open-xiaoai`

本项目是 `open-xiaoai` 的一个**增强配置**，而非独立应用。因此，你 **必须** 首先根据官方文档成功部署并运行 `open-xiaoai` 的 `xiaozhi` 示例。这一步是为了确保你的基础环境、设备连接和 Token 等都是正常的。

> **重要**: 请严格参考官方 `xiaozhi` 示例的部署指南完成基础配置。所有关于设备 ID、Token 获取、设备绑定等问题，均以官方文档为准。
>
> **官方文档地址**: [https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi](https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi)

在确认你的 `open-xiaoai` 容器可以正常工作后，停止并移除该临时容器，再进行下一步。

```bash
# 停止并移除用于测试的官方容器
docker stop oxa-server && docker rm oxa-server
```

#### 2. 使用本项目进行增强部署

与官方步骤几乎完全一样，唯一的区别是**额外挂载了本项目的 `config.py` 和 `oxa_ext` 目录**。

1.  **下载文件**:
    将本项目的 `config.py` 文件和 `oxa_ext` 整个目录下载到你的服务器上。

2.  **修改配置**:
    打开 `config.py`，根据你的需求修改指令映射和相关配置。

3.  **启动增强版容器**:
    在 `config.py` 和 `oxa_ext` 所在的目录下，执行以下命令启动容器。

    > **核心提示**: 对比官方命令，我们只增加了两个 `-v` 参数来挂载我们自己的逻辑，其他保持不变。

    ```bash
    # 基础命令与官方一致，仅增加 volume 挂载
    docker run -itd \
      --name oxa-server \
      -p 4399:4399 \
      -v "$(pwd)/config.py:/app/config.py" \
      -v "$(pwd)/oxa_ext:/app/oxa_ext" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

### ⚙️ 配置说明

所有配置均在 `config.py` 中完成，核心是 `AppConfigBuilder` 构建器。

```python
# config.py
APP_CONFIG = AppConfigBuilder(
    # 1. 免唤醒直接执行的指令
    direct_vad_command_map={
        # a. 将多个指令映射到同一个动作
        **map_all_to(("调整颜色", "切换色温", "请开夜灯", "请关夜灯"), ["色温分段"]),

        # b. 批量生成开关指令
        **map_the_switches(*lights_all, *appliances_extra),
        # 上一行等同于:
        # "请开空调": ["打开空调"], "请关空调": ["关闭空调"],
        # "请开风扇": ["打开风扇"], "请关风扇": ["关闭风扇"],
        # ...

        # c. 将指令映射到自定义的 Python 函数
        "空调升速": ["空调风速升高"],
        "空调降速": ["空调风速降低"],
        "空调降温": ["空调温度降低"],
        "空调升温": ["空调温度升高"],
        "风扇定时": ["风扇计时器"],
        "风扇风类": ["调整风类"],
        "点亮阳台": on(*lights_balcony),
        "熄灭阳台": off(*lights_balcony),
        "灯光全灭": off(*lights_all),
        "关灯空调": off(*lights_all, "空调"),
        "全部关闭": off(*appliances_all),
        "请开电脑": [wake_up_computer],
        "请关电脑": ["关闭我的电脑"],
        "重启电脑": ["我的电脑设置为一"],
        "切换屏幕": ["我的电脑设置为三"],
        "测试电脑": ["我的电脑设置为七"],
        "联合关闭": ["关闭我的电脑", "关闭电视"],
        "联合启动": [wake_up_computer, "打开电视"],
    },

    # 2. 用于“唤醒”小智，进入连续对话模式的关键词
    direct_vad_wakeup_keywords=["小智小智"],

    # 3. 在小爱原生对话中，用于“抢麦”并唤醒小智的关键词
    xiaoai_wakeup_keywords=["召唤小智"],

    on_execute_play_text="", # 禁用执行指令后的提示音，保持安静

    # ... 其他配置，请参考 config.py 文件 ...
).build()
```

#### `wol(computer_mac, broadcast_ip)`

一个辅助函数，用于生成网络唤醒 (Wake-on-LAN) 的指令。它会发送一个魔法包来启动指定 MAC 地址的电脑。

```python
# config.py
wake_up_computer = wol(computer_mac="08BFB8A67CE2",
                       broadcast_ip="192.168.100.255")

# ... 然后在 direct_vad_command_map 中使用
"请开电脑": [wake_up_computer],
```

#### `on(*devices)` 和 `off(*devices)`

这两个辅助函数用于快速生成针对一组设备的“打开”或“关闭”小爱原生指令列表。在 `config.py` 中，你可以先定义好不同位置或类别的设备列表，然后直接使用 `on()` 或 `off()` 来生成组合指令。

例如，在 `config.py` 中：
```python
lights_balcony = ["台灯", "副灯"]
appliances_extra = ["空调", "风扇", "电视"]
lights_all = [*lights_balcony, "主灯"]
appliances_all = [*lights_all, *appliances_extra, "我的电脑"]

# ... 然后在 direct_vad_command_map 中使用
"点亮阳台": on(*lights_balcony),
"熄灭阳台": off(*lights_balcony),
"灯光全灭": off(*lights_all),
"全部关闭": off(*appliances_all),
```

这使得管理大量设备的开关指令变得非常简洁和灵活。

#### `direct_vad_command_map`

这是最核心的**免唤醒指令表**。当小爱同学识别到这里的键（key），会直接执行对应的值（value），无需先说“小爱同学”。

- **值（Actions）** 可以是：
  - `["小爱原生指令"]`: 一个包含字符串的列表，将执行小爱音箱的原生指令。
  - `[自定义函数]`: 一个包含 Python 函数的列表，将直接调用你定义的函数。
  - 混合列表: `[自定义函数, "小爱原生指令", ...]`，将按顺序执行。

#### `map_the_switches(*devices)`

一个辅助函数，用于快速生成设备的标准“开/关”指令。例如 `map_the_switches("空调", "灯")` 会自动创建 `请开空调`、`请关空调`、`请开灯`、`请关灯` 四个指令。

#### 进阶配置 (可选)

`AppConfigBuilder` 还提供了一些可选参数，用于微调小智的行为。

- **`xiaoai_extension_command_map`**: 定义一组特殊的指令。当你在和小爱同学正常对话时，如果说出这里的指令，小智会**中断**小爱的当前任务并执行该指令。这对于需要立即响应的控制非常有用。
- **`wakeup_timeout`**: 唤醒超时（秒）。当使用 `direct_vad_wakeup_keywords` 唤醒小智后，它会在此时间内等待你的下一条指令，超时后会自动退出唤醒状态。默认为 `5` 秒。
- **`on_wakeup_play_text`**: 唤醒提示音。唤醒小智后播放的文本。默认为 `"小智来了"`。
- **`on_execute_play_text`**: 执行提示音。当一个免唤醒指令执行完毕后播放的文本。默认为 `"已执行"`。
- **`on_exit_play_text`**: 退出提示音。小智退出唤醒状态时播放的文本。默认为 `"主人再见"`。

### 🐍 自定义 Python 函数

你可以在 `config.py` 的顶部自由编写自己的 Python 异步函数，并在 `direct_vad_command_map` 中引用它们。

```python
# config.py

import asyncio
from oxa_ext.utils import ensure_dependencies, ...

# 示例：一个网络唤醒电脑的函数
async def wake_up_computer(_):
    # 确保依赖已安装
    ensure_dependencies(["wakeonlan"])
    # 你的逻辑...
    print("已发送网络唤醒包。")

# ... 在 AppConfigBuilder 中使用
# "请开电脑": [wake_up_computer],
```

`ensure_dependencies` 函数会自动检查并使用 `pip` 安装缺失的库，让你的自定义功能开箱即用。

### 🔗 关联项目

- **[open-xiaoai](https://github.com/idootop/open-xiaoai)**: 本项目的基础，一个功能强大的小米智能音箱开放平台项目。

---

## English <a name="english"></a>

### Introduction

This project provides a deeply customized enhancement solution based on the `xiaozhi` example from the [open-xiaoai](https://github.com/idootop/open-xiaoai) project.

It is designed to significantly enhance and customize the functionality of your Xiaoai Speaker with **minimal intrusion** using Docker volume mounting. You don't need to modify the original Docker image. Simply add extra volume mounts for your `config.py` file and the `oxa_ext` directory to the official run command to enable features like wake-word-free commands, command chains, and custom Python code execution.

### ✨ Features

- **Minimal Intrusion**: Seamlessly enhances original functionality by just adding extra mounts for `config.py` and the `oxa_ext` directory.
- **Structured Configuration**: Uses the `AppConfigBuilder` for a cleaner and more maintainable configuration logic.
- **Wake-Word-Free Commands**: Configure frequently used commands to be executed directly without saying the "Xiaoai Tongxue" wake-word first.
- **Powerful Command Mapping**: Easily map a spoken phrase to one or more actions (native commands or custom functions).
- **Seamless Python Function Integration**: Directly call custom Python functions (sync or async) within commands to perform complex operations like Wake-on-LAN (WOL), API calls, or executing shell commands.
- **Automatic Dependency Installation**: If a custom function requires a new Python package, the script will automatically attempt to install it, simplifying deployment.

### 🚀 How to Use

#### 1. Prerequisite: Successfully Run the Original `open-xiaoai`

This project is an **enhanced configuration** for `open-xiaoai`, not a standalone application. Therefore, you **must** first successfully deploy and run the `xiaozhi` example according to the official documentation. This step ensures that your basic environment, device connection, and Token are all working correctly.

> **Important**: Please strictly follow the official `xiaozhi` example's deployment guide for the basic setup. All issues related to Device ID, Token acquisition, and device binding should refer to the official documentation.
>
> **Official Documentation**: [https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi](https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi)

After confirming that your `open-xiaoai` container works, stop and remove that temporary container before proceeding.

```bash
# Stop and remove the official container used for testing
docker stop oxa-server && docker rm oxa-server
```

#### 2. Enhanced Deployment with This Project

The process is almost identical to the official steps, with the only difference being the **additional mounting of this project's `config.py` and `oxa_ext` directory**.

1.  **Download Files**:
    Download this project's `config.py` file and the entire `oxa_ext` directory to your server.

2.  **Modify Configuration**:
    Open `config.py` and modify the command mappings and other settings to suit your needs.

3.  **Start the Enhanced Container**:
    In the directory where `config.py` and `oxa_ext` are located, run the following command.

    > **Key Tip**: Compared to the official command, we only add two `-v` flags to mount our custom logic; everything else remains the same.

    ```bash
    # The base command is the same as the official one, just with added volume mounts
    docker run -itd \
      --name oxa-server \
      -p 4399:4399 \
      -v "$(pwd)/config.py:/app/config.py" \
      -v "$(pwd)/oxa_ext:/app/oxa_ext" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

### ⚙️ Configuration Explanation

All configurations are done in `config.py`, with the `AppConfigBuilder` being the core component.

```python
# config.py
APP_CONFIG = AppConfigBuilder(
    # 1. Wake-word-free commands that execute directly
    direct_vad_command_map={
        # a. Map multiple phrases to the same action
        **map_all_to(("adjust color", "switch color temperature", "turn on night light", "turn off night light"), ["color temperature segment"]),

        # b. Batch generate on/off commands
        **map_the_switches(*lights_all, *appliances_extra),
        # The line above is equivalent to:
        # "turn on AC": ["turn on AC"], "turn off AC": ["turn off AC"],
        # "turn on Fan": ["turn on Fan"], "turn off Fan": ["turn off Fan"],
        # ...

        # c. Map a command to a custom Python function
        "AC speed up": ["AC fan speed up"],
        "AC speed down": ["AC fan speed down"],
        "AC cool down": ["AC temperature down"],
        "AC heat up": ["AC temperature up"],
        "fan timer": ["fan timer"],
        "fan mode": ["adjust fan mode"],
        "light up balcony": on(*lights_balcony),
        "turn off balcony lights": off(*lights_balcony),
        "all lights off": off(*lights_all),
        "turn off AC lights": off(*lights_all, "AC"),
        "turn all off": off(*appliances_all),
        "turn on PC": [wake_up_computer],
        "turn off PC": ["turn off my PC"],
        "restart PC": ["set my PC to one"],
        "switch screen": ["set my PC to three"],
        "test PC": ["set my PC to seven"],
        "joint shutdown": ["turn off my PC", "turn off TV"],
        "joint startup": [wake_up_computer, "turn on TV"],

    # 2. Keywords to "wake up" Xiaozhi for continuous dialogue
    direct_vad_wakeup_keywords=["hey zhi"],

    # 3. Keywords to "interrupt" native Xiaoai and wake up Xiaozhi
    xiaoai_wakeup_keywords=["summon xiaozhi"],

    on_execute_play_text="", # Disable the prompt sound after command execution for quiet operation

    # ... other configurations, please refer to the config.py file ...
).build()
```

#### `wol(computer_mac, broadcast_ip)`

A helper function to generate Wake-on-LAN (WOL) commands. It sends a magic packet to start a computer with the specified MAC address.

```python
# config.py
wake_up_computer = wol(computer_mac="08BFB8A67CE2",
                       broadcast_ip="192.168.100.255")

# ... then use in direct_vad_command_map
"turn on PC": [wake_up_computer],
```

#### `on(*devices)` and `off(*devices)`

These two helper functions are used to quickly generate lists of native Xiaoai "turn on" or "turn off" commands for a group of devices. In `config.py`, you can first define lists of devices by location or category, and then directly use `on()` or `off()` to generate combined commands.

For example, in `config.py`:
```python
lights_balcony = ["balcony lamp", "side lamp"]
appliances_extra = ["AC", "Fan", "TV"]
lights_all = [*lights_balcony, "main light"]
appliances_all = [*lights_all, *appliances_extra, "my PC"]

# ... then use in direct_vad_command_map
"light up balcony": on(*lights_balcony),
"turn off balcony lights": off(*lights_balcony),
"all lights off": off(*lights_all),
"turn all off": off(*appliances_all),
```

This makes managing on/off commands for a large number of devices very concise and flexible.

#### `direct_vad_command_map`

This is the core **wake-word-free command table**. When Xiaoai Speaker recognizes a key from this map, it will execute the corresponding value directly.

- **Value (Actions)** can be:
  - `["Native Xiaoai Command"]`: A list of strings for native commands.
  - `[custom_function]`: A list containing a Python function to be called.
  - A mixed list: `[custom_function, "Native Command", ...]`, executed in sequence.

#### `map_the_switches(*devices)`

A helper function to quickly generate standard "on/off" commands for devices. For example, `map_the_switches("AC", "Light")` will automatically create commands for `turn on AC`, `turn off AC`, `turn on Light`, and `turn off Light`.

#### Advanced Configuration (Optional)

`AppConfigBuilder` also provides several optional parameters to fine-tune Xiaozhi's behavior.

- **`xiaoai_extension_command_map`**: Defines a special set of commands. If you say one of these commands during a normal conversation with the native Xiaoai, Xiaozhi will **interrupt** the current task and execute the command. This is useful for controls that require immediate response.
- **`wakeup_timeout`**: Wake-up timeout (in seconds). After waking up Xiaozhi with a keyword from `direct_vad_wakeup_keywords`, it will wait for your next command for this duration before automatically exiting the awakened state. Defaults to `5` seconds.
- **`on_wakeup_play_text`**: Text played upon wake-up. Defaults to `"Xiaozhi is here"`.
- **`on_execute_play_text`**: Text played after a wake-word-free command is executed. Defaults to `"Done"`.
- **`on_exit_play_text`**: Text played when Xiaozhi exits the awakened state. Defaults to `"Goodbye, master"`.

### 🐍 Custom Python Functions

You can write your own async Python functions at the top of `config.py` and reference them in the `direct_vad_command_map`.

```python
# config.py

import asyncio
from oxa_ext.utils import ensure_dependencies, ...

# Example: A function to wake up a computer via Wake-on-LAN
async def wake_up_computer(_):
    ensure_dependencies(["wakeonlan"])
    # Your logic here...
    print("Magic packet sent.")

# ... Use it in AppConfigBuilder
# "turn on PC": [wake_up_computer],
```

The `ensure_dependencies` function automatically checks and installs missing libraries, making your custom features work out of the box.

### 🔗 Related Projects

- **[open-xiaoai](https://github.com/idootop/open-xiaoai)**: The foundation of this project, a powerful open platform for Xiaomi smart speakers.
