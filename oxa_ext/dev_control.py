from oxa_ext.utils import ensure_dependencies
from json import load
from mijiaAPI import mijiaAPI, mijiaDevice
from pathlib import Path

# 可以直接使用米家 API，更加准确地控制设备
# 暂时不是很需要，后面如果有需求再完善
# https://github.com/Do1e/mijia-api

ensure_dependencies(['mijiaAPI'])

with open(Path(__file__).parent / "mijia-api-auth.json", "r") as auth_info:
    api = mijiaAPI(load(auth_info))

main_light = mijiaDevice(api, dev_name="主灯", did="ir.1765388093977935872")
