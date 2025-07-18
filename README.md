# oxa-server

This project provides a highly customizable server for Xiaoai speakers running the `open-xiaoai` client. It allows you to define your own voice commands and link them to various actions, all by editing a single configuration file: `config.py`.

The core principle is a data-driven approach, making it easy to add or change commands without altering the main logic.

## Key Features

*   **Simple Configuration**: All customizations are done in `config.py`.
*   **Flexible Command Mapping**: Map a single voice command to another command, a sequence of commands, or a custom Python function.
*   **Extensible with Python**: Easily add new functionality, like the built-in Wake-on-LAN (WOL) feature to turn on your computer.
*   **Custom Wake Words**: Define your own wake words (e.g., "小智小智") to activate a special command mode.
*   **Automatic Dependency Management**: The script automatically detects and installs required Python packages.

## How It Works

All logic is controlled by the `COMMAND_MAP` dictionary in `config.py`. You can map a trigger phrase to one or more actions.

**1. Basic Aliases (String)**
Map one phrase to another.
```python
"切换电视": ["打开电视"],
```

**2. Command Sequences (List of Strings)**
Execute multiple commands in order.
```python
"灯光全灭": ["关闭主灯", "关闭台灯", "关闭副灯"],
```

**3. Custom Functions (Callable)**
Execute custom Python code.
```python
async def wake_up_computer(_):
    # ... implementation ...
    from wakeonlan import send_magic_packet
    send_magic_packet("YOUR_MAC_ADDRESS_HERE")

"请开电脑": [wake_up_computer],
```
**Note**: To use the Wake-on-LAN feature, you must edit `config.py` and set your computer's MAC address in the `wake_up_computer` function.

**4. Mixed Actions**
Combine functions and string commands.
```python
"联合启动": [wake_up_computer, "打开电视"],
```

## Usage

1.  **Prerequisite**: Your Xiaoai speaker must be flashed with the `open-xiaoai` rust client.
2.  **Customize**: Open `config.py` and modify the `COMMAND_MAP` and any other settings to your liking.
3.  **Run**: Start the server.

### Command Activation

You can trigger commands in two ways:

1.  **Direct Command**: Simply say any command key defined in `COMMAND_MAP` (e.g., "请开电脑").
2.  **Wake Word Mode**:
    *   Say the custom wake word (default: "小智小智").
    *   The speaker will respond ("小智来了").
    *   You can then say your command within the configured timeout (default: 5 seconds).

### Dependencies

The script requires certain Python packages for special functions. For example, the Wake-on-LAN feature uses the `wakeonlan` library.

The server will automatically check for and install any missing dependencies upon startup.

## 相关项目对比

* 慕容柯小爱伴侣: 接入音频线，安装麻烦，而且会造成“当前设备连接有线，请在电脑/手机上停止”
* xiaomusic
* xiaogpt
* 巴法 mqtt 模拟设备：只能用数字模拟设备，曲折麻烦
* mijiaAPI
* open-xiaoai
* MiServices