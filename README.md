# oxa-server

使用最小侵入的方法，仅修改 config.py，方便同步更新官方的 open-xiaoai-esp32-example 的 docker 镜像

优势：快速简洁，可使用 python 生态，代码可读性好。

要求：小爱音箱刷机，安装 open-xiaoai 的 rust client

## Extra Modules

### WOL

#### requirements

`pip install wakeonlan`


## 相关项目对比

* 慕容柯小爱伴侣: 接入音频线，安装麻烦，而且会造成“当前设备连接有线，请在电脑/手机上停止”
* xiaomusic
* xiaogpt
* 巴法 mqtt 模拟设备：只能用数字模拟设备，曲折麻烦
* mijiaAPI
* open-xiaoai
* MiServices
