from typing import Generator

from loguru import logger
from requests import Session

from .config_manager import ConfigMarager, LogManager, push
from .daledou import DaLeDou
from .mission import get_func_names


class SessionManager:
    """会话管理类"""

    @staticmethod
    def parse_cookie(cookie_str: str) -> dict:
        """解析Cookie字符串为字典"""
        cookies = {}
        for item in cookie_str.split("; "):
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
        return cookies

    @staticmethod
    def create_verified_session(qq: str, cookie_dict: dict) -> Session | None:
        """创建并验证会话"""
        url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
        with Session() as session:
            session.cookies.update(cookie_dict)
            session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"
                }
            )
            for _ in range(3):
                res = session.get(url, allow_redirects=False)
                res.encoding = "utf-8"
                if "商店" in res.text:
                    logger.success(f"{qq}|会话验证成功")
                    return session

        logger.warning(f"{qq}|会话验证失败")
        print("--" * 20)


class LogContext:
    def __init__(self, qq: str):
        self.qq = qq

    def __enter__(self):
        self.handler_id = LogManager.setup_user_logger(self.qq)
        return self.handler_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        LogManager.remove_logger(self.handler_id)


def generate_daledou() -> Generator[DaLeDou, None, None]:
    """生成大乐斗实例对象"""
    cookies: list = ConfigMarager.load_settings_config("DALEDOU_COOKIES")
    for cookie in cookies:
        cookie_dict = SessionManager.parse_cookie(cookie)
        qq = cookie_dict["newuin"]

        with LogContext(qq):
            session = SessionManager.create_verified_session(qq, cookie_dict)
            if not session:
                push(
                    f"{qq} Cookie无效",
                    "请更换Cookie",
                )
                continue

            # 创建用户配置，如果没有的话
            ConfigMarager.create_user_config(f"{qq}.yaml")

            func_names = get_func_names(qq, session)
            if not func_names:
                push(
                    f"{qq} 无法完成任务",
                    "可能官方系统繁忙或者维护",
                )
                continue

            # 加载用户QQ配置文件
            config = ConfigMarager.load_user_config(f"{qq}.yaml")
            yield DaLeDou(qq, session, config, func_names)
