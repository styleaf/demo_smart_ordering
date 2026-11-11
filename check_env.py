"""第一步自检：确认 .env 里的配置项有没有填写。

只打印“有没有值”，不打印密钥本身。
"""

import os

from dotenv import load_dotenv

# 读取项目根目录的 .env，把里面的键值放进当前进程的环境变量。
load_dotenv()

REQUIRED = [
    "DEEPSEEK_API_KEY",
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_USER_NAME",
    "MYSQL_USER_PASSWORD",
    "MYSQL_DB_NAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "MILVUS_URI",
]


def main() -> None:
    """逐项检查必填配置是否已填写。

    参数:
        无。

    返回:
        无。只在终端打印已填写或未填写，不打印配置内容。
    """
    print("环境自检（只看是否填写，不显示内容）")
    missing = []
    for key in REQUIRED:
        value = (os.getenv(key) or "").strip()
        if value:
            print(f"  [已填写] {key}")
        else:
            print(f"  [未填写] {key}")
            missing.append(key)
    if missing:
        print(f"\n还有 {len(missing)} 项没填。模型和数据库密码可以等用到时再填。")
    else:
        print("\n必填项都已填写。")


if __name__ == "__main__":
    main()
