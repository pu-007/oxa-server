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
      -e MI_DEVICE_ID="<YOUR_DEVICE_ID>" \
      -e MI_TOKEN="<YOUR_TOKEN>" \
      --restart=always \
      idootop/open-xiaoai:xiaozhi
    ```

通过这种方式，你既可以享受到 `open-xiaoai` 的强大基础功能，又能利用本项目的 `config.py` 轻松实现各种高级定制。


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


### 🔗 Related Projects

- **[open-xiaoai](https://github.com/idootop/open-xiaoai)**: The foundation of this project, a powerful open platform for Xiaomi smart speakers.

