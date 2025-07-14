import sys
import textwrap
from datetime import datetime
from pathlib import Path
from shutil import copy

import requests
import yaml
from loguru import logger


CONFIG_DIR = Path("./config")
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default_config.yaml"


class ConfigMarager:
    """配置管理类"""

    # 第一轮定时运行时间
    one_run_time = "13:01"
    # 第二轮定时运行时间
    two_run_time = "20:01"
    # 第一轮名称
    one_round_name = "第一轮"
    # 第二轮名称
    two_round_name = "第二轮"
    # 定时运行时显示的信息
    timing_info = textwrap.dedent(f"""
        定时任务守护进程已启动：
        第一轮默认 {one_run_time} 定时运行
        第二轮默认 {two_run_time} 定时运行

        立即运行第一轮命令：
        python main.py --one 或 uv run main.py --one

        立即运行第二轮命令：
        python main.py --two 或 uv run main.py --two

        强制结束脚本按键：CTRL + C

        {"--" * 20}\
    """)

    @staticmethod
    def create_user_config(file: str):
        """创建用户配置文件"""
        create_path = CONFIG_DIR / Path(file).name
        if not create_path.exists():
            copy(DEFAULT_CONFIG_PATH, create_path)
        logger.success(f"任务配置|{create_path}")

    @staticmethod
    def load_settings_config(key: str) -> list | str:
        """加载settings.yaml配置文件"""
        config_path = CONFIG_DIR / Path("settings.yaml").name
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")

        try:
            with config_path.open("r", encoding="utf-8") as fp:
                config_data = yaml.safe_load(fp)
                return config_data.get(key)
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件解析错误：{e}")

    @staticmethod
    def load_user_config(file: str) -> dict:
        """加载用户配置文件"""
        config_path = CONFIG_DIR / Path(file).name
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")

        try:
            with config_path.open("r", encoding="utf-8") as fp:
                return yaml.safe_load(fp)
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件解析错误：{e}")


def push(title: str, content: str):
    """pushplus微信通知"""
    token: str = ConfigMarager.load_settings_config("PUSHPLUS_TOKEN")
    if not token or not len(token) == 32:
        logger.warning(f"无效的PUSHPLUS_TOKEN：{token}")
        print("--" * 20)
        return

    url = "http://www.pushplus.plus/send/"
    data = {
        "token": token,
        "title": title,
        "content": content,
    }
    res = requests.post(url, data=data, timeout=10)
    logger.success(f"pushplus推送结果：{res.json()}")
    print("--" * 20)


class LogManager:
    """日志管理类"""

    @staticmethod
    def init_logger():
        """初始化控制台输出格式"""
        logger.remove()
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{message}</level>",
            colorize=True,
        )

    @staticmethod
    def setup_user_logger(qq: str) -> int:
        """为指定QQ用户创建日志处理器"""
        log_dir = Path(f"./log/{qq}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

        logger.success(f"任务日志|{log_file}")

        return logger.add(
            sink=log_file,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{message}</level>",
            enqueue=True,
            encoding="utf-8",
            retention="30 days",
            level="INFO",
        )

    @staticmethod
    def remove_logger(handler_id: str):
        """移除日志处理器"""
        logger.remove(handler_id)
