import os

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("EQUIPMENT_API_KEY")

if not API_KEY:
    raise RuntimeError("缺少环境变量：EQUIPMENT_API_KEY")