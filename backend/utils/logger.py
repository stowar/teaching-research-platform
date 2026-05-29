import logging
import os
from datetime import datetime

# 日志文件夹自动创建
if not os.path.exists("logs"):
    os.mkdir("logs")

# 配置日志
logging.basicConfig(
    filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("research_platform")