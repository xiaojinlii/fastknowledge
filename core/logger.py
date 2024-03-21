"""
# 日志简单配置
# 具体其他配置 可自行参考 https://github.com/Delgan/loguru
"""

import os
import time
from loguru import logger
from application.settings import BASE_DIR


# 移除控制台输出
# logger.remove(handler_id=None)

log_path = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)


info = logger.add("info.log", rotation="00:00", retention="30 days", enqueue=True, encoding="UTF-8", level="INFO")
error = logger.add("error.log", rotation="00:00", retention="30 days", enqueue=True, encoding="UTF-8", level="ERROR")
