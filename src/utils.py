import re
import sys
import time
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from shutil import copy
from typing import Iterator, Self

import requests
import yaml
from loguru import logger
from requests import Session

from src import MISSIONS_ONE, MISSIONS_TWO


# 请求头
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
}


def read_yaml(file: str, key: str | None = None):
    """
    读取config目录下的yaml配置文件
    """
    path = Path(f"./config/{file}")
    try:
        with path.open("r", encoding="utf-8") as fp:
            users = yaml.safe_load(fp)
            return users[key] if key else users
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} 文件不存在")
    except yaml.YAMLError:
        raise yaml.YAMLError(f"{path} 文件格式不正确")


def push(title: str, content: str) -> None:
    """
    pushplus微信通知
    """
    if token := read_yaml("settings.yaml", "PUSHPLUS_TOKEN"):
        url = "http://www.pushplus.plus/send/"
        data = {
            "token": token,
            "title": title,
            "content": content,
        }
        res = requests.post(url, data=data)
        logger.success(f"pushplus推送信息：{res.json()}")
    else:
        logger.warning("你没有配置pushplus微信推送")


class InItDaLeDou:
    """
    初始化大乐斗
    """

    def __init__(self, cookie: str):
        self._setup_console_logger()
        self._cookie: dict = self.parse_cookie(cookie)
        self._qq: str = self._cookie["newuin"]
        self._session = self._session_add_cookie()

        if isinstance(self._session, requests.Session):
            self._create_qq_yaml()
            self._handler_id: int = self._create_qq_log()
            self._yaml: dict = read_yaml(f"{self.qq}.yaml")
            self._func_name = self._get_func_name()

    @property
    def start_time(self) -> str:
        return self._start_time

    @property
    def qq(self) -> str:
        return self._qq

    @property
    def session(self) -> Session | None:
        return self._session

    @property
    def yaml(self) -> dict:
        return self._yaml

    @property
    def func_name(self) -> dict | None:
        """
        返回第一、二轮要执行的函数名称
        """
        return self._func_name

    def _setup_console_logger(self) -> int:
        """
        设置控制台输出格式，返回处理器id
        """
        logger.remove()
        return logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{message}</level>",
        )

    def parse_cookie(self, cookie: str) -> dict:
        cookies = {}
        for cookie in cookie.split("; "):
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value
        return cookies

    def _session_add_cookie(self) -> Session | None:
        """
        向Session添加大乐斗Cookie，若Cookie有效则返回Session，否则返回None
        """
        url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
        with requests.Session() as session:
            session.cookies.update(self._cookie)
            for _ in range(3):
                res = session.get(url, headers=_HEADERS, allow_redirects=False)
                res.encoding = "utf-8"
                if "商店" in res.text:
                    logger.success(f"{self.qq}|Cookie有效")
                    return session

        logger.warning(f"{self.qq}|Cookie无效")
        push(f"{self.qq} Cookie无效", "请更换Cookie")

    def _create_qq_yaml(self) -> None:
        """
        基于daledou.yaml创建一份以qq命名的yaml配置文件
        """
        default_path = Path("./config/daledou.yaml")
        create_path = Path(f"./config/{self.qq}.yaml")
        if not create_path.exists():
            copy(default_path, create_path)
        logger.success(f"任务配置|{create_path}")

    def _create_qq_log(self) -> int:
        """
        创建QQ日志文件，返回日志处理器id
        """
        log_dir = Path(f"./log/{self.qq}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        logger.success(f"任务日志|{log_file}")

        return logger.add(
            log_file,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{message}</level>",
            enqueue=True,
            encoding="utf-8",
            retention="30 days",
        )

    def _get_dld_main_page_html(self) -> str | None:
        """
        获取大乐斗首页HTML源码
        """
        url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
        for _ in range(3):
            response = self._session.get(url, headers=_HEADERS)
            response.encoding = "utf-8"
            if "商店" in response.text:
                return response.text.split("【退出】")[0]

        logger.warning(f"{self.qq}|大乐斗首页未找到，可能官方繁忙或者维护")
        push(
            f"{self.qq} 大乐斗首页未找到",
            "大乐斗首页未找到，可能官方繁忙或者维护",
        )

    def _map_mission_names_to_func_names(self, missions: list) -> list:
        """
        将大乐斗首页任务名称映射为函数名称
        """
        _data = {
            # 键为大乐斗首页任务名称，值为函数名称
            "5.1礼包": "五一礼包",
        }
        return [_data.get(k, k) for k in missions]

    def _get_func_name(self) -> dict | None:
        """
        过滤掉未出现在大乐斗首页的任务，并将剩余任务名称映射的函数名称以字典返回
        """
        if _html := self._get_dld_main_page_html():
            _one = [k for k in MISSIONS_ONE if k in _html]
            _two = [k for k in MISSIONS_TWO if k in _html]
            return {
                "one": self._map_mission_names_to_func_names(_one),
                "two": self._map_mission_names_to_func_names(_two),
            }

    def remove_logger_handler(self):
        """
        移除当前QQ日志处理器
        """
        logger.remove(self._handler_id)


class DaLeDou:
    """
    大乐斗实例方法
    """

    _compile_cache = lru_cache(maxsize=256)(re.compile)
    _WEEKDAY_NAMES = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")

    def __init__(self, qq: str, session: Session, yaml: dict, func_name: dict):
        self._qq = qq
        self._session = session
        self._yaml = yaml
        self._func_name = func_name

        self._start_time = time.time()
        self._now = datetime.now()
        self._year: int = self._now.year
        self._month: int = self._now.month
        self._day: int = self._now.day
        self._week: int = self._now.weekday() + 1

        # pushplus内容正文
        self._pushplus_body: list[str] = [
            f"【开始时间】\n{self._now.strftime('%Y-%m-%d %H:%M:%S')} {self._WEEKDAY_NAMES[self._now.weekday()]}",
        ]
        # 大乐斗当前页面HTML
        self.html: str = None
        # 大乐斗日志任务名称
        self.func_name: str = None
        # log方法读写、append方法只读
        self._info: str = None

        self._default_pattern = self._compile_with_cache(r"<br />(.*?)<")

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    @property
    def week(self) -> int:
        return self._week

    @property
    def yaml(self) -> dict:
        return self._yaml

    @property
    def func_name_one(self) -> list:
        """
        返回第一轮要执行的函数名称
        """
        return self._func_name["one"]

    @property
    def func_name_two(self) -> list:
        """
        返回第二轮要执行的函数名称
        """
        return self._func_name["two"]

    @classmethod
    def _compile_with_cache(cls, pattern: str) -> re.Pattern:
        """
        带缓存的编译方法
        """
        return cls._compile_cache(pattern, re.DOTALL)

    def get(self, params: str) -> str | None:
        """
        发送get请求获取HTML源码
        """
        url = f"https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{params}"
        for _ in range(3):
            res = self._session.get(url, headers=_HEADERS)
            res.encoding = "utf-8"
            self.html = res.text
            if "系统繁忙" in self.html:
                time.sleep(0.2)
            elif "操作频繁" in self.html:
                time.sleep(0.8)
            else:
                return self.html

    def find(self, regex: str = None) -> str | None:
        """
        返回成功匹配的首个结果，匹配失败返回None

        regex为None时默认使用 '<br />(.*?)<' 缓存编译
        """
        if regex is None:
            pattern = self._default_pattern
        else:
            pattern = self._compile_with_cache(regex)
        if result := pattern.search(self.html):
            return result.group(1)

    def findall(self, regex: str, html: str = None) -> list:
        """
        匹配所有结果
        """
        if html is None:
            html = self.html
        return re.findall(regex, html, re.DOTALL)

    def log(self, info: str = None, name: str = None) -> Self:
        """
        将传入的内容打印并写入日志
        """
        self._info = info
        if name is None:
            name = self.func_name
        logger.info(f"{self._qq}|{name}|{self._info}")
        return self

    def append(self, info: str = None) -> None:
        """
        向pushplus正文追加消息内容

        Examples：
            >>> # 直接追加字符串
            >>> D.append("大乐斗") # 将"大乐斗"添加到正文

            >>> # 链式调用追加日志内容
            >>> D.log("大乐斗").append() # 将日志内容写入正文

            >>> # 分步操作
            >>> D.log("旧日志内容")
            >>> D.log("大乐斗")
            >>> D.append() # 将最近的日志内容"大乐斗"追加到正文
        """
        if info is None:
            info = self._info
        if isinstance(info, str):
            self._pushplus_body.append(info)

    def is_target_date_reached(
        self, days_before: int, end_date_tuple: tuple[int, int, int]
    ) -> bool:
        """
        判断当前日期是否已达到或超过目标日期（结束日期的前N天）

        Args:
            days_before: 结束日期之前的天数（目标日期 = 结束日期 - days_before）
            end_date_tuple: 结束日期的年月日三元组，格式为 (年, 月, 日)

        Returns:
            bool: 如果当前日期大于等于目标日期返回True，否则返回False

        Examples:
            >>> # 判断当前日期是否为2024-11-7（2024-11-8的前1天）
            >>> D.is_target_date_reached(1, (2024, 11, 8))

            >>> # 判断当前日期是否为2024-11-2（2024-11-8的前6天）
            >>> D.is_target_date_reached(6, (2024, 11, 8))
        """
        end_year, end_month, end_day = end_date_tuple
        current_date = self._now.date()
        target_date = datetime(end_year, end_month, end_day).date() - timedelta(
            days=days_before
        )
        return current_date >= target_date

    def body(self) -> str:
        """
        生成pushplus推送正文内容
        """
        self.append(f"\n【运行耗时】\n耗时：{int(time.time() - self._start_time)} s")
        return "\n".join(self._pushplus_body)

    def push(self, title: str):
        """
        向pushplus推送消息
        """
        push(f"{self._qq} {title}", self.body())


def generate_daledou() -> Iterator[DaLeDou]:
    """
    返回大乐斗实例对象
    """
    dld_cookies: list[str] = read_yaml("settings.yaml", "DALEDOU_ACCOUNT")
    for cookie in dld_cookies:
        dld = InItDaLeDou(cookie)
        if dld.session is None or dld.func_name is None:
            continue

        D = DaLeDou(dld.qq, dld.session, dld.yaml, dld.func_name)
        yield D

        dld.remove_logger_handler()
