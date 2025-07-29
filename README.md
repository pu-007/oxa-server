# Oxa-Server: 小爱同学 Docker 定制增强脚本

[中文](#中文) | [English](#english)

---

## 中文 <a name="中文"></a>

### 简介

本项目是一个基于 [open-xiaoai](https://github.com/idootop/open-xiaoai) 项目 `xiaozhi` 示例的深度定制 `config.py` 脚本。它旨在通过 Docker Volume 挂载的方式，以最小的侵入性，极大地增强和自定义小爱同学的功能。

你可以在单个文件中，通过简单修改 Python 字典和列表，实现免唤醒指令、组合指令、自定义 Python 函数调用等高级功能，让你的小爱同学变得更智能、更听话。

### ✨ 特性

- **免唤醒指令**：将常用指令（如 `打开主灯`, `关闭电脑`）配置为免唤醒关键词，直接说出即可执行，无需先说 "小爱同学"。
- **强大的指令映射**：使用 `COMMAND_MAP` 字典，轻松将一句口语指令映射到一个或多个动作。
- **组合指令与链式调用**：一个指令可以触发一连串的动作，例如用 "灯光全灭" 一次性关闭所有指定灯光。
- **Python 函数无缝集成**：可以直接在指令中调用自定义的 Python 函数（同步或异步），实现网络唤醒（WOL）、API 调用、执行 Shell 命令等复杂操作。
- **依赖自动安装**：脚本内置依赖检查功能，如果自定义函数需要新的 Python 包（如 `wakeonlan`），它会自动尝试安装，简化部署。
- **单文件部署**：所有核心逻辑和自定义功能都集中在 `config.py` 和 `oxa_ext` 目录中，只需将它们挂载到 Docker 容器即可生效。

### 🚀 工作原理

本项目利用了 `open-xiaoai` (`xiaozhi` 版本) 的架构，它会加载一个名为 `config.py` 的文件来获取所有配置和回调函数。

我们通过 Docker 的 `-v` (volume) 参数，将外部宿主机上的 `config.py` 文件和 `oxa_ext` 目录挂载并覆盖到容器内部。这样，我们就可以在不修改原始 Docker 镜像的情况下，动态地注入我们自己的逻辑。

### 🛠️ 如何使用

#### 1. 部署 `open-xiaoai`

本项目并非一个独立的应用程序，而是 `open-xiaoai` (`xiaozhi` 版本) 的一个 **增强配置**。

因此，在开始之前，你 **必须** 首先根据官方文档成功部署 `open-xiaoai` 的 `xiaozhi` 示例。这通常涉及到获取设备 ID 和 Token，并成功运行 Docker 容器。

> **重要**：请严格参考官方 `xiaozhi` 示例的部署指南完成基础配置：
> [https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi](https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi)

在确认你的 `open-xiaoai` 容器可以正常工作后，再进行下一步。

#### 2. 使用本项目的配置

本项目的核心是提供一个功能更强大的配置。

1.  **停止并移除** 你之前根据官方文档启动的 `oxa-server` 容器（如果已运行）。
    ```bash
    docker stop oxa-server && docker rm oxa-server
    ```

2.  **下载或克隆** 本项目，确保 `config.py` 和 `oxa_ext` 目录在同一路径下。根据你的需求修改 `config.py`。

3.  **重新运行容器**，但这次使用 `-v` 参数将 `config.py` 和 `oxa_ext` 挂载到容器内部。

    在 `config.py` 所在的目录下，执行以下命令：
    ```bash
    # 确保将 <YOUR_DEVICE_ID> 和 <YOUR_TOKEN> 替换为你的真实值
    # -v "$(pwd)/config.py:/app/config.py" 和 -v "$(pwd)/oxa_ext:/app/oxa_ext" 是此方案的核心
    docker run -itd \
      --name oxa-server \
      -p 4399:4399 \
      -v "$(pwd)/config.py:/app/config.py" \
      -v "$(pwd)/oxa_ext:/app/oxa_ext" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

通过这种方式，你既可以享受到 `open-xiaoai` 的强大基础功能，又能利用本项目的配置轻松实现各种高级定制。


### ⚙️ 配置说明

`config.py` 文件是本项目的核心配置文件。通过修改其中的 Python 变量和字典，你可以高度定制小爱同学的行为。我们提供了一系列工具函数，让配置过程更简单、更高效。

#### 主要配置变量

-   `VAD_CONFIG`: 语音活动检测 (VAD) 的高级参数，通常无需修改。
-   `XIAOZHI_CONFIG`: 连接 `open-xiaoai` 云服务的配置。

#### `DIRECT_VAD_WAKEUP_KEYWORDS`

-   **作用**: 定义一个或多个“超级唤醒词”（例如 `["小智小智"]`）。当小爱同学听到这些词，会激活小智模式，准备接收下一条免唤醒指令。

#### `DIRECT_VAD_COMMAND_MAP`

-   **作用**: 这是核心的 **免唤醒** 指令映射表。它将你口述的指令（键）映射到一个或多个具体动作（值）。
-   **动作 (Actions)**: 可以是小爱同学的原生指令（字符串），也可以是你自己编写的 Python 异步函数。
-   **配置示例**:
    ```python
    from oxa_ext.utils import map_all_to, map_the_switches

    DIRECT_VAD_COMMAND_MAP = {
        # 基础映射: "打开电视" -> 执行原生指令 "打开电视"
        "打开电视": ["打开电视"],

        # 组合指令: "我出门了" -> 先关灯，再关空调
        "我出门了": ["关闭所有灯", "关闭空调"],

        # 函数调用: "打开电脑" -> 执行自定义的 wake_up_computer 函数
        "打开电脑": [wake_up_computer],

        # 混合指令: "我到家了" -> 先开电脑，再说“欢迎回家”
        "我到家了": [wake_up_computer, "欢迎回家"],
    }
    ```

#### `XIAOAI_WAKEUP_KEYWORDS`

-   **作用**: 定义在与小爱原生对话时，用于“召唤”小智的关键词，例如 `["召唤小智"]`。

#### `XIAOAI_EXTENSION_COMMAND_MAP`

-   **作用**: 扩展小爱原生对话的能力。当你在和小爱对话时说出此处的关键词，可以中断它并执行你的自定义操作。
-   **配置示例**:
    ```python
    from oxa_ext.utils import interrupt_xiaoai

    XIAOAI_EXTENSION_COMMAND_MAP = {
        # 当对小爱说“帮我打开电脑”时...
        "帮我打开电脑": [
            interrupt_xiaoai,  # 首先中断小爱，防止它回复
            wake_up_computer   # 然后执行开机函数
        ],
    }
    ```

### 🛠️ 辅助工具函数 (`oxa_ext/utils.py`)

为了简化 `config.py` 的配置，我们在 `oxa_ext/utils.py` 中提供了一些实用的辅助函数，你可以直接在配置文件中导入和使用它们。

-   **`map_all_to(keys, value)`**: 将多个语音指令（`keys`，一个元组）映射到同一组动作（`value`）。
    -   **示例**: `**map_all_to(("关灯", "熄灯"), ["关闭主灯"])` 会让“关灯”和“熄灯”都执行“关闭主灯”的动作。

-   **`map_the_switches(*devices)`**: 为一系列设备快速生成标准的“开”和“关”指令。
    -   **示例**: `**map_the_switches("空调", "风扇")` 会自动创建 `"打开空调"`, `"关闭空调"`, `"打开风扇"`, `"关闭风扇"` 四个指令。

-   **`ensure_dependencies(packages)`**: 在你的自定义函数中调用，以确保需要的 Python 包（如 `wakeonlan`）已被自动安装。

-   **`interrupt_xiaoai(speaker)`**: 一个可被调用的动作，用于在执行后续指令前，中断小爱同学当前的对话或播放。

### 🔗 关联项目

- **[open-xiaoai](https://github.com/idootop/open-xiaoai)**: 本项目的基础，一个功能强大的小米智能音箱开放平台项目。

---

## English <a name="english"></a>

### Introduction

This project provides a highly customized `config.py` script based on the `xiaozhi` example from the [open-xiaoai](https://github.com/idootop/open-xiaoai) project. It's designed to significantly enhance and customize the functionality of your Xiaoai Speaker with minimal intrusion, using Docker volume mounting.

Within a single file, you can implement advanced features like wake-word-free commands, command chaining, and custom Python function calls just by modifying Python dictionaries and lists, making your Xiaoai speaker smarter and more obedient.

### ✨ Features

- **Wake-Word-Free Commands**: Configure frequently used commands (e.g., `turn on main light`, `shut down pc`) as keywords that can be executed directly without saying the "Xiaoai Tongxue" wake-word first.
- **Powerful Command Mapping**: Use the `COMMAND_MAP` dictionary to easily map a spoken phrase to one or more actions.
- **Command Chaining**: A single command can trigger a sequence of actions. For example, use "lights out" to turn off all specified lights at once.
- **Seamless Python Function Integration**: Directly call custom Python functions (sync or async) within commands to perform complex operations like Wake-on-LAN, API calls, or executing shell commands.
- **Automatic Dependency Installation**: The script includes a built-in dependency checker. If a custom function requires a new Python package (e.g., `wakeonlan`), it will attempt to install it automatically, simplifying deployment.
- **Single-File Deployment**: All core logic and custom functionalities are centralized in `config.py` and the `oxa_ext` directory. Simply mount them into the Docker container to apply your changes.

### 🚀 How It Works

This project leverages the architecture of `open-xiaoai` (`xiaozhi` version), which loads a file named `config.py` to get all configurations and callback functions.

By using Docker's `-v` (volume) flag, we mount the `config.py` file and the `oxa_ext` directory from the host machine to overwrite the corresponding paths inside the container. This allows us to dynamically inject our own logic without altering the original Docker image.

### 🛠️ How to Use

#### 1. Deploy `open-xiaoai`

This project is not a standalone application but an **enhanced configuration** for `open-xiaoai` (`xiaozhi` version).

Therefore, before you begin, you **must** first successfully deploy the `xiaozhi` example from `open-xiaoai` according to the official documentation. This typically involves obtaining your device ID and token, and running the Docker container successfully.

> **Important**: Please strictly follow the official `xiaozhi` example's deployment guide to complete the basic setup:
> [https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi](https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi)

Proceed to the next step only after confirming that your `open-xiaoai` container is working correctly.

#### 2. Use This Project's Configuration

The core of this project is to provide a more powerful configuration.

1.  **Stop and remove** the `oxa-server` container you previously started according to the official documentation (if it's running).
    ```bash
    docker stop oxa-server && docker rm oxa-server
    ```

2.  **Download or clone** this project. Copy `config.template.py` to `config.py` and modify it to suit your needs.

3.  **Re-run the container**, but this time, use the `-v` flag to mount `config.py` and `oxa_ext` into the container.

    In the same directory as your `config.py`, run the following command:
    ```bash
    # Make sure to replace <YOUR_DEVICE_ID> and <YOUR_TOKEN> with your actual values.
    # -v "$(pwd)/config.py:/app/config.py" and -v "$(pwd)/oxa_ext:/app/oxa_ext" are the core of this solution.
    docker run -itd \
      --name oxa-server \
      -p 4399:4399 \
      -v "$(pwd)/config.py:/app/config.py" \
      -v "$(pwd)/oxa_ext:/app/oxa_ext" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

This way, you can enjoy the powerful base functionality of `open-xiaoai` while easily implementing various advanced customizations using this project's configuration.


### ⚙️ Configuration Explanation

The `config.py` file is the core configuration file for this project. By modifying its Python variables and dictionaries, you can highly customize the behavior of your Xiaoai Speaker. We provide a set of utility functions to make the configuration process simpler and more efficient.

#### Main Configuration Variables

-   `VAD_CONFIG`: Advanced parameters for Voice Activity Detection (VAD), usually no need to modify.
-   `XIAOZHI_CONFIG`: Configuration for connecting to the `open-xiaoai` cloud service.

#### `DIRECT_VAD_WAKEUP_KEYWORDS`

-   **Purpose**: Defines one or more "super wake-words" (e.g., `["Xiaozhi Xiaozhi"]`). When the speaker hears these words, it activates Xiaozhi mode, ready to receive the next wake-word-free command.

#### `DIRECT_VAD_COMMAND_MAP`

-   **Purpose**: This is the core **wake-word-free** command map. It maps your spoken commands (keys) to one or more specific actions (values).
-   **Actions**: Can be native Xiaoai Speaker commands (strings) or your own custom Python asynchronous functions.
-   **Configuration Example**:
    ```python
    from oxa_ext.utils import map_all_to, map_the_switches

    DIRECT_VAD_COMMAND_MAP = {
        # Basic mapping: "turn on TV" -> executes native command "turn on TV"
        "turn on TV": ["turn on TV"],

        # Combined commands: "I'm leaving" -> turn off lights, then turn off AC
        "I'm leaving": ["turn off all lights", "turn off AC"],

        # Function call: "turn on PC" -> executes the custom wake_up_computer function
        "turn on PC": [wake_up_computer],

        # Mixed commands: "I'm home" -> turn on PC, then say "welcome home"
        "I'm home": [wake_up_computer, "welcome home"],
    }
    ```

#### `XIAOAI_WAKEUP_KEYWORDS`

-   **Purpose**: Defines keywords used to "summon" Xiaozhi during a native conversation with Xiaoai, e.g., `["summon Xiaozhi"]`.

#### `XIAOAI_EXTENSION_COMMAND_MAP`

-   **Purpose**: Extends the native Xiaoai dialogue capabilities. When you say a keyword from this map during a conversation, it can interrupt Xiaoai and execute your custom action.
-   **Configuration Example**:
    ```python
    from oxa_ext.utils import interrupt_xiaoai

    XIAOAI_EXTENSION_COMMAND_MAP = {
        # When you say to Xiaoai "help me turn on the computer"...
        "help me turn on the computer": [
            interrupt_xiaoai,  # First, interrupt Xiaoai to prevent it from replying
            wake_up_computer   # Then, execute the power-on function
        ],
    }
    ```

### 🛠️ Utility Functions (`oxa_ext/utils.py`)

To simplify the configuration in `config.py`, we provide several useful helper functions in `oxa_ext/utils.py` that you can import and use directly in your configuration file.

-   **`map_all_to(keys, value)`**: Maps multiple voice commands (`keys`, a tuple) to the same set of actions (`value`).
    -   **Example**: `**map_all_to(("lights off", "darkness"), ["turn off main light"])` makes both "lights off" and "darkness" execute the "turn off main light" action.

-   **`map_the_switches(*devices)`**: Quickly generates standard "on" and "off" commands for a series of devices.
    -   **Example**: `**map_the_switches("AC", "fan")` will automatically create four commands: `"turn on AC"`, `"turn off AC"`, `"turn on fan"`, and `"turn off fan"`.

-   **`ensure_dependencies(packages)`**: Call this in your custom functions to ensure that required Python packages (e.g., `wakeonlan`) are automatically installed.

-   **`interrupt_xiaoai(speaker)`**: A callable action used to interrupt Xiaoai's current dialogue or playback before executing subsequent commands.

### 🔗 Related Projects

- **[open-xiaoai](https://github.com/idootop/open-xiaoai)**: The foundation of this project, a powerful open platform for Xiaomi smart speakers.

