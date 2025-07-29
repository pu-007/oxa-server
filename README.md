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
- **单文件部署**：所有核心逻辑和自定义功能都集中在 `config.py` 中，只需挂载这一个文件到 Docker 容器即可生效。

### 🚀 工作原理

本项目利用了 `open-xiaoai` (`xiaozhi` 版本) 的架构，它会加载一个名为 `config.py` 的文件来获取所有配置和回调函数。

我们通过 Docker 的 `-v` (volume) 参数，将外部宿主机上的 `config.py` 文件挂载并覆盖到容器内部的 `/app/config.py`。这样，我们就可以在不修改原始 Docker 镜像的情况下，动态地注入我们自己的逻辑。

### 🛠️ 如何使用

#### 1. 部署 `open-xiaoai`

本项目并非一个独立的应用程序，而是 `open-xiaoai` (`xiaozhi` 版本) 的一个 **增强配置**。

因此，在开始之前，你 **必须** 首先根据官方文档成功部署 `open-xiaoai` 的 `xiaozhi` 示例。这通常涉及到获取设备 ID 和 Token，并成功运行 Docker 容器。

> **重要**：请严格参考官方 `xiaozhi` 示例的部署指南完成基础配置：
> [https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi](https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi)

在确认你的 `open-xiaoai` 容器可以正常工作后，再进行下一步。

#### 2. 使用本项目的 `config.py`

本项目的核心是提供一个功能更强大的 `config.py`。

1.  **停止并移除** 你之前根据官方文档启动的 `oxa-server` 容器（如果已运行）。
    ```bash
    docker stop oxa-server && docker rm oxa-server
    ```

2.  **下载或编辑** 本项目的 `config.py` 文件，根据你的需求修改 `COMMAND_MAP` 和其他配置。

3.  **重新运行容器**，但这次使用 `-v` 参数将本项目的 `config.py` 挂载到容器内部。

    在 `config.py` 所在的目录下，执行以下命令：
    ```bash
    # 确保将 <YOUR_DEVICE_ID> 和 <YOUR_TOKEN> 替换为你的真实值
    # -v "$(pwd)/config.py:/app/config.py" 是此方案的核心
    docker run -itd \
      --name oxa-server \
      -v "$(pwd)/config.py:/app/config.py" \
      -v "$(pwd)/oxa_utils:/app/oxa_utils" \
      -e MI_DEVICE_ID="<YOUR_DEVICE_ID>" \
      -e MI_TOKEN="<YOUR_TOKEN>" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

通过这种方式，你既可以享受到 `open-xiaoai` 的强大基础功能，又能利用本项目的 `config.py` 轻松实现各种高级定制。


### ⚙️ 配置说明

`config.py` 文件是本项目的核心配置文件，通过修改其中的变量和字典，你可以高度定制小爱同学的行为。

#### `KWS_WAKEUP`

*   **作用**: 定义用于唤醒小智的关键词列表。当小爱同学识别到这些词语时，会触发小智的唤醒逻辑。
*   **配置方式**: 修改列表中的字符串，例如 `KWS_WAKEUP = ["小智小智", "你好小智"]`。

#### `COMMAND_MAP`

*   **作用**: 这是最核心的指令映射表。它将你对小爱同学说出的自定义指令（键）映射到一个或多个实际执行的动作（值）。动作可以是小爱同学的原生指令字符串，也可以是自定义的 Python 异步函数。
*   **配置方式**:
    *   **原生指令映射**: `"你的自定义指令": ["小爱原生指令"]`。例如：`"切换电视": ["打开电视"]`。
    *   **组合指令**: `"你的组合指令": ["小爱原生指令1", "小爱原生指令2", ...]`。例如：`"点亮外面": ["打开台灯", "打开副灯"]`。
    *   **Python 函数调用**: `"你的自定义指令": [你的异步函数名]`。例如：`"请开电脑": [wake_up_computer]`。
    *   **混合指令**: `"你的混合指令": [你的异步函数名, "小爱原生指令"]`。例如：`"联合启动": [wake_up_computer, "打开电视"]`。
    *   `wake_up_computer` 是一个示例函数，用于发送网络唤醒包。你可以根据需要编写自己的 Python 函数。

#### `APP_CONFIG`

这是一个总的应用程序配置字典，包含了 `wakeup`、`vad` 和 `xiaozhi` 三个主要部分。

##### `APP_CONFIG["wakeup"]`

*   **作用**: 控制小智的唤醒行为。
*   **配置项**:
    *   `keywords`: 包含所有触发小智的关键词，通常会自动包含 `KWS_WAKEUP` 和 `COMMAND_MAP` 中的所有键。一般无需手动修改。
    *   `timeout`: 唤醒状态的超时时间（秒）。小智在被唤醒后，如果在此时间内没有新的指令，将自动退出唤醒状态。
    *   `before_wakeup`: 进入唤醒状态前执行的回调函数。
    *   `after_wakeup`: 退出唤醒状态时执行的回调函数。

##### `APP_CONFIG["vad"]`

*   **作用**: 配置语音活动检测（VAD）参数，影响小智对语音的识别和断句。
*   **配置项**:
    *   `boost`: VAD 增益，影响语音识别的灵敏度。
    *   `threshold`: VAD 阈值，用于判断是否有语音活动。
    *   `min_speech_duration`: 最小语音持续时间（毫秒），低于此时间可能被认为是噪音。
    *   `min_silence_duration`: 最小静音持续时间（毫秒），用于判断一句话是否结束。

##### `APP_CONFIG["xiaozhi"]`

*   **作用**: 配置与 `open-xiaoai` `xiaozhi` 服务相关的连接参数。
*   **配置项**:
    *   `OTA_URL`: OTA (Over-The-Air) 更新服务的 URL。
    *   `WEBSOCKET_URL`: WebSocket 服务器的 URL，用于与小爱同学服务通信。
    *   `WEBSOCKET_ACCESS_TOKEN`: 连接 WebSocket 服务器所需的访问令牌。**重要：请务必替换为你的真实 Token。**
    *   `DEVICE_ID`: 你的小爱同学设备的唯一 ID。**重要：请务必替换为你的真实设备 ID。**
    *   `VERIFICATION_CODE`: 用于设备验证的验证码。

### 🔌 事件处理器 (Handler Functions)

`config.py` 中定义了多个异步函数，它们作为事件处理器，在小爱同学的不同状态或接收到特定指令时被调用。

#### `_kws_handler(speaker, text)`

*   **作用**: 统一处理所有自定义关键词命令。当小爱同学识别到 `COMMAND_MAP` 中定义的关键词时，此函数会被调用，并根据映射执行相应的动作（发送原生指令或调用自定义 Python 函数）。
*   **参数**:
    *   `speaker`: `Speaker` 对象，用于与小爱同学交互（如发送指令、播放语音）。
    *   `text`: 小爱同学识别到的关键词文本。

#### `_xiaoai_handler(speaker, text)`

*   **作用**: 处理来自小爱原生对话的特定指令。例如，当你说出 "召唤小智" 时，此函数会中断小爱同学的当前对话，并让小智接管。
*   **参数**:
    *   `speaker`: `Speaker` 对象。
    *   `text`: 小爱同学识别到的对话文本。

#### `_before_wakeup(speaker, text, source)`

*   **作用**: 在小智进入唤醒状态前的主回调函数。它会根据指令来源 (`kws` 或 `xiaoai`) 分发到 `_kws_handler` 或 `_xiaoai_handler` 进行处理。
*   **参数**:
    *   `speaker`: `Speaker` 对象。
    *   `text`: 识别到的文本。
    *   `source`: 指令来源，可以是 `"kws"` (关键词唤醒) 或 `"xiaoai"` (小爱原生对话)。

#### `_after_wakeup(speaker)`

*   **作用**: 当小智退出唤醒状态时调用。通常用于播放一个结束语。
*   **参数**:
    *   `speaker`: `Speaker` 对象。

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
- **Single-File Deployment**: All core logic and custom functionalities are centralized in `config.py`. Simply mount this single file into the Docker container to apply your changes.

### 🚀 How It Works

This project leverages the architecture of `open-xiaoai` (`xiaozhi` version), which loads a file named `config.py` to get all configurations and callback functions.

By using Docker's `-v` (volume) flag, we mount the `config.py` file from the host machine to overwrite the `/app/config.py` inside the container. This allows us to dynamically inject our own logic without altering the original Docker image.

### 🛠️ How to Use

#### 1. Deploy `open-xiaoai`

This project is not a standalone application but an **enhanced configuration** for `open-xiaoai` (`xiaozhi` version).

Therefore, before you begin, you **must** first successfully deploy the `xiaozhi` example from `open-xiaoai` according to the official documentation. This typically involves obtaining your device ID and token, and running the Docker container successfully.

> **Important**: Please strictly follow the official `xiaozhi` example's deployment guide to complete the basic setup:
> [https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi](https://github.com/idootop/open-xiaoai/tree/main/examples/xiaozhi)

Proceed to the next step only after confirming that your `open-xiaoai` container is working correctly.

#### 2. Use This Project's `config.py`

The core of this project is to provide a more powerful `config.py`.

1.  **Stop and remove** the `oxa-server` container you previously started according to the official documentation (if it's running).
    ```bash
    docker stop oxa-server && docker rm oxa-server
    ```

2.  **Download or edit** this project's `config.py` file, modifying the `COMMAND_MAP` and other configurations to suit your needs.

3.  **Re-run the container**, but this time, use the `-v` flag to mount this project's `config.py` into the container.

    In the same directory as your `config.py`, run the following command:
    ```bash
    # Make sure to replace <YOUR_DEVICE_ID> and <YOUR_TOKEN> with your actual values.
    # The -v "$(pwd)/config.py:/app/config.py" is the core of this solution.
    docker run -itd \
      --name oxa-server \
      -v "$(pwd)/config.py:/app/config.py" \
      -e MI_DEVICE_ID="<YOUR_DEVICE_ID>" \
      -e MI_TOKEN="<YOUR_TOKEN>" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

This way, you can enjoy the powerful base functionality of `open-xiaoai` while easily implementing various advanced customizations using this project's `config.py`.


### ⚙️ Configuration Explanation

The `config.py` file is the core configuration file for this project. By modifying its variables and dictionaries, you can highly customize the behavior of Xiaoai Speaker.

#### `KWS_WAKEUP`

*   **Purpose**: Defines a list of keywords used to wake up Xiaozhi. When Xiaoai Speaker recognizes these words, it triggers Xiaozhi's wake-up logic.
*   **Configuration**: Modify the strings in the list, for example `KWS_WAKEUP = ["xiaozhi xiaozhi", "hello xiaozhi"]`.

#### `COMMAND_MAP`

*   **Purpose**: This is the most crucial command mapping table. It maps your custom spoken commands (keys) to one or more actions (values) to be executed. Actions can be native Xiaoai Speaker commands (strings) or custom Python asynchronous functions.
*   **Configuration**:
    *   **Native Command Mapping**: `"Your Custom Command": ["Native Xiaoai Command"]`. For example: `"switch TV": ["turn on TV"]`.
    *   **Combined Commands**: `"Your Combined Command": ["Native Xiaoai Command 1", "Native Xiaoai Command 2", ...]`. For example: `"light up outside": ["turn on desk lamp", "turn on auxiliary light"]`.
    *   **Python Function Calls**: `"Your Custom Command": [your_async_function_name]`. For example: `"turn on PC": [wake_up_computer]`.
    *   **Mixed Commands**: `"Your Mixed Command": [your_async_function_name, "Native Xiaoai Command"]`. For example: `"joint start": [wake_up_computer, "turn on TV"]`.
    *   `wake_up_computer` is an example function for sending Wake-on-LAN packets. You can write your own Python functions as needed.

#### `APP_CONFIG`

This is a general application configuration dictionary, containing three main sections: `wakeup`, `vad`, and `xiaozhi`.

##### `APP_CONFIG["wakeup"]`

*   **Purpose**: Controls Xiaozhi's wake-up behavior.
*   **Configuration Items**:
    *   `keywords`: Contains all keywords that trigger Xiaozhi, usually automatically including `KWS_WAKEUP` and all keys from `COMMAND_MAP`. Generally no manual modification is needed.
    *   `timeout`: The timeout duration (in seconds) for the awakened state. If Xiaozhi receives no new commands within this time after being awakened, it will automatically exit the awakened state.
    *   `before_wakeup`: A callback function executed before entering the awakened state.
    *   `after_wakeup`: A callback function executed when exiting the awakened state.

##### `APP_CONFIG["vad"]`

*   **Purpose**: Configures Voice Activity Detection (VAD) parameters, affecting Xiaozhi's speech recognition and segmentation.
*   **Configuration Items**:
    *   `boost`: VAD gain, affecting the sensitivity of speech recognition.
    *   `threshold`: VAD threshold, used to determine if there is voice activity.
    *   `min_speech_duration`: Minimum speech duration (milliseconds); durations below this may be considered noise.
    *   `min_silence_duration`: Minimum silence duration (milliseconds), used to determine if a sentence has ended.

##### `APP_CONFIG["xiaozhi"]`

*   **Purpose**: Configures connection parameters related to the `open-xiaoai` `xiaozhi` service.
*   **Configuration Items**:
    *   `OTA_URL`: The URL for the OTA (Over-The-Air) update service.
    *   `WEBSOCKET_URL`: The URL of the WebSocket server for communication with the Xiaoai Speaker service.
    *   `WEBSOCKET_ACCESS_TOKEN`: The access token required to connect to the WebSocket server. **Important: Please replace this with your actual Token.**
    *   `DEVICE_ID`: The unique ID of your Xiaoai Speaker device. **Important: Please replace this with your actual Device ID.**
    *   `VERIFICATION_CODE`: The verification code used for device authentication.

### ⚙️ Configuration Explanation

The `config.py` file is the core configuration file for this project. By modifying its variables and dictionaries, you can highly customize the behavior of Xiaoai Speaker.

#### `KWS_WAKEUP`

*   **Purpose**: Defines a list of keywords used to wake up Xiaozhi. When Xiaoai Speaker recognizes these words, it triggers Xiaozhi's wake-up logic.
*   **Configuration**: Modify the strings in the list, for example `KWS_WAKEUP = ["xiaozhi xiaozhi", "hello xiaozhi"]`.

#### `COMMAND_MAP`

*   **Purpose**: This is the most crucial command mapping table. It maps your custom spoken commands (keys) to one or more actions (values) to be executed. Actions can be native Xiaoai Speaker commands (strings) or custom Python asynchronous functions.
*   **Configuration**:
    *   **Native Command Mapping**: `"Your Custom Command": ["Native Xiaoai Command"]`. For example: `"switch TV": ["turn on TV"]`.
    *   **Combined Commands**: `"Your Combined Command": ["Native Xiaoai Command 1", "Native Xiaoai Command 2", ...]`. For example: `"light up outside": ["turn on desk lamp", "turn on auxiliary light"]`.
    *   **Python Function Calls**: `"Your Custom Command": [your_async_function_name]`. For example: `"turn on PC": [wake_up_computer]`.
    *   **Mixed Commands**: `"Your Mixed Command": [your_async_function_name, "Native Xiaoai Command"]`. For example: `"joint start": [wake_up_computer, "turn on TV"]`.
    *   `wake_up_computer` is an example function for sending Wake-on-LAN packets. You can write your own Python functions as needed.

#### `APP_CONFIG`

This is a general application configuration dictionary, containing three main sections: `wakeup`, `vad`, and `xiaozhi`.

##### `APP_CONFIG["wakeup"]`

*   **Purpose**: Controls Xiaozhi's wake-up behavior.
*   **Configuration Items**:
    *   `keywords`: Contains all keywords that trigger Xiaozhi, usually automatically including `KWS_WAKEUP` and all keys from `COMMAND_MAP`. Generally no manual modification is needed.
    *   `timeout`: The timeout duration (in seconds) for the awakened state. If Xiaozhi receives no new commands within this time after being awakened, it will automatically exit the awakened state.
    *   `before_wakeup`: A callback function executed before entering the awakened state.
    *   `after_wakeup`: A callback function executed when exiting the awakened state.

##### `APP_CONFIG["vad"]`

*   **Purpose**: Configures Voice Activity Detection (VAD) parameters, affecting Xiaozhi's speech recognition and segmentation.
*   **Configuration Items**:
    *   `boost`: VAD gain, affecting the sensitivity of speech recognition.
    *   `threshold`: VAD threshold, used to determine if there is voice activity.
    *   `min_speech_duration`: Minimum speech duration (milliseconds); durations below this may be considered noise.
    *   `min_silence_duration`: Minimum silence duration (milliseconds), used to determine if a sentence has ended.

##### `APP_CONFIG["xiaozhi"]`

*   **Purpose**: Configures connection parameters related to the `open-xiaoai` `xiaozhi` service.
*   **Configuration Items**:
    *   `OTA_URL`: The URL for the OTA (Over-The-Air) update service.
    *   `WEBSOCKET_URL`: The URL of the WebSocket server for communication with the Xiaoai Speaker service.
    *   `WEBSOCKET_ACCESS_TOKEN`: The access token required to connect to the WebSocket server. **Important: Please replace this with your actual Token.**
    *   `DEVICE_ID`: The unique ID of your Xiaoai Speaker device. **Important: Please replace this with your actual Device ID.**
    *   `VERIFICATION_CODE`: The verification code used for device authentication.

### 🔌 Event Handlers (Handler Functions)

`config.py` defines several asynchronous functions that act as event handlers, called when Xiaoai Speaker is in different states or receives specific commands.

#### `_kws_handler(speaker, text)`

*   **Purpose**: Uniformly handles all custom keyword commands. When Xiaoai Speaker recognizes a keyword defined in `COMMAND_MAP`, this function is called and executes the corresponding action (sending a native command or calling a custom Python function) based on the mapping.
*   **Parameters**:
    *   `speaker`: The `Speaker` object, used to interact with Xiaoai Speaker (e.g., sending commands, playing audio).
    *   `text`: The keyword text recognized by Xiaoai Speaker.

#### `_xiaoai_handler(speaker, text)`

*   **Purpose**: Handles specific commands from Xiaoai's native dialogue. For example, when you say "summon Xiaozhi", this function will interrupt Xiaoai Speaker's current dialogue and let Xiaozhi take over.
*   **Parameters**:
    *   `speaker`: The `Speaker` object.
    *   `text`: The dialogue text recognized by Xiaoai Speaker.

#### `_before_wakeup(speaker, text, source)`

*   **Purpose**: The main callback function executed before Xiaozhi enters the awakened state. It dispatches to `_kws_handler` or `_xiaoai_handler` for processing based on the command source (`kws` or `xiaoai`).
*   **Parameters**:
    *   `speaker`: The `Speaker` object.
    *   `text`: The recognized text.
    *   `source`: The command source, which can be `"kws"` (keyword wake-up) or `"xiaoai"` (Xiaoai native dialogue).

#### `_after_wakeup(speaker)`

*   **Purpose**: Called when Xiaozhi exits the awakened state. Typically used to play a closing remark.
*   **Parameters**:
    *   `speaker`: The `Speaker` object.

### 🔗 Related Projects

- **[open-xiaoai](https://github.com/idootop/open-xiaoai)**: The foundation of this project, a powerful open platform for Xiaomi smart speakers.

