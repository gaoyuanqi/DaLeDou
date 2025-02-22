import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy

import requests
import yaml
from loguru import logger
from requests import Session

from daledou import MISSIONS_ONE, MISSIONS_TWO


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
        print("--" * 20)


class InItDaLeDou:
    """
    初始化大乐斗
    """

    def __init__(self, dld_cookie: str):
        self._setup_console_logger()
        self._start_time = f"【开始时间】\n{self._get_datetime_weekday()}"
        self._cookie: str = self._clean_cookie(dld_cookie)
        self._qq: str = self._get_qq()
        self._session = self._session_add_cookie()

        if isinstance(self._session, requests.Session):
            # 创建QQ任务配置文件
            self._create_qq_yaml()
            # 创建QQ日志文件
            self._handler_id: int = self._create_qq_log()
            # 大乐斗任务配置
            self._yaml: dict = read_yaml(f"{self.qq}.yaml")
            # 获取函数映射
            self._func_map = self._get_func_map()

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
    def func_map(self) -> dict | None:
        return self._func_map

    def _setup_console_logger(self) -> int:
        """
        设置控制台输出格式，返回处理器id
        """
        logger.remove()
        return logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>",
        )

    def _clean_cookie(self, dld_cookie: str) -> str:
        """
        清洁大乐斗Cookie，改成 'RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=xx'
        """
        required_keys = ["RK", "ptcz", "openId", "accessToken", "newuin"]
        for key in required_keys:
            if key not in dld_cookie:
                raise ValueError(f"大乐斗Cookie缺失 {key} 字段：\n{dld_cookie}")

        ck = ""
        for key in ["RK", "ptcz", "openId", "accessToken", "newuin"]:
            result = re.search(f"{key}=(.*?); ", f"{dld_cookie}; ", re.S)
            ck += f"{result.group(0)}"
        return ck[:-2]

    def _get_qq(self) -> str:
        """
        返回 self._cookie 中的QQ
        """
        return re.search(r"newuin=(\d+)", self._cookie, re.S).group(1)

    def _session_add_cookie(self) -> Session | None:
        """
        向Session添加大乐斗Cookie，若Cookie有效则返回Session，否则返回None
        """
        url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
        with requests.Session() as session:
            session.cookies.set("Cookie", self._cookie)
            for _ in range(3):
                res = session.get(url, headers=_HEADERS, allow_redirects=False)
                res.encoding = "utf-8"
                if "商店" in res.text:
                    logger.success(f"{self.qq} | Cookie有效")
                    return session

        logger.warning(f"{self.qq} | Cookie无效")
        push(f"{self.qq} | Cookie无效", self._cookie)

    def _create_qq_yaml(self) -> None:
        """
        基于daledou.yaml创建一份以qq命名的yaml配置文件
        """
        default_path = Path("./config/daledou.yaml")
        create_path = Path(f"./config/{self.qq}.yaml")
        if not create_path.exists():
            copy(default_path, create_path)
        logger.success(f"任务配置：{create_path}")

    def _create_qq_log(self) -> int:
        """
        创建QQ日志文件，返回日志处理器id
        """
        log_dir = Path(f"./log/{self.qq}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        logger.success(f"任务日志：{log_file}")

        return logger.add(
            log_file,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>",
            enqueue=True,
            encoding="utf-8",
            retention="30 days",
        )

    def _get_datetime_weekday(self) -> str:
        """
        获取当前的日期和时间，并附加星期信息：2024-09-01 14:35:18 周日
        """
        name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        now = datetime.now()
        week = now.weekday()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        return f"{formatted_now} {name[week]}"

    def _get_func_map(self) -> dict | None:
        """
        过滤掉未出现在大乐斗首页的任务，并将剩余任务名称映射的函数名称以字典返回
        """
        if _html := self._get_dld_main_page_html():
            _one = [k for k in MISSIONS_ONE if k in _html]
            _two = [k for k in MISSIONS_TWO if k in _html]
            return {
                "one": self._map_mission_names_to_function_names(_one),
                "two": self._map_mission_names_to_function_names(_two),
            }

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

        logger.warning(f"{self.qq} | 大乐斗首页未找到，可能官方繁忙或者维护")
        push(
            f"{self.qq} 大乐斗首页未找到",
            "大乐斗首页未找到，可能官方繁忙或者维护",
        )

    def _map_mission_names_to_function_names(self, missions: list) -> list:
        """
        将大乐斗首页任务名称映射为函数名称
        """
        _data = {
            # 键为大乐斗首页任务名称，值为函数名称
            "5.1礼包": "五一礼包",
        }
        return [_data.get(k, k) for k in missions]

    def remove_logger_handler(self):
        """
        移除当前QQ日志处理器
        """
        logger.remove(self._handler_id)


class DaLeDou:
    """
    大乐斗实例方法
    """

    def __init__(self, qq: str, session: Session, yaml: dict, func_map: dict):
        self._start_time = time.time()
        self._now = datetime.now()
        self._year: int = self._now.year
        self._month: int = self._now.month
        self._day: int = self._now.day
        self._week: int = self._now.weekday() + 1

        self._qq = qq
        self._session = session
        self._yaml = yaml
        self._func_map = func_map

        # 储存推送消息
        self._msg: list[str] = []
        # 大乐斗当前页面HTML
        self.html = None
        # 大乐斗日志任务名称
        self.func_name = None

    @property
    def now(self) -> datetime:
        return self._now

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
    def qq(self) -> str:
        return self._qq

    @property
    def yaml(self) -> dict:
        return self._yaml

    @property
    def func_map(self) -> dict:
        return self._func_map

    @property
    def msg(self) -> list:
        return self._msg

    @property
    def msg_join(self) -> str:
        """
        将列表中的元素用换行符连接成一个字符串
        """
        return "\n".join(self.msg)

    def msg_append(self, message: str):
        """
        向列表添加字符串消息
        """
        if isinstance(message, str):
            self.msg.append(message)

    def get(self, params: str) -> str:
        """
        发送get请求获取响应内容
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
                break
        return self.html

    def print_info(self, message: str, name=None) -> None:
        """
        打印信息
        """
        if name is None:
            name = self.func_name
        logger.info(f"{self.qq} | {name}：{message}")

    def find(self, mode="<br />(.*?)<", name=None) -> str | None:
        """
        匹配成功返回首个结果，匹配失败返回None

        无论结果如何都会被打印并写入日志
        """
        _match = re.search(mode, self.html, re.S)
        result = _match.group(1) if _match else None
        self.print_info(result, name)
        return result

    def findall(self, mode: str) -> list:
        """
        查找大乐斗HTML字符串源码中所有匹配正则表达式的子串
        """
        return re.findall(mode, self.html, re.S)

    def is_arrive_date(self, days: int, year_month_day: tuple) -> bool:
        """
        判断当前日期是否大于等于预定的结束日期

        Arg:
            days：结束日期的前 days 天
            year_month_day：结束日期

        举例：
            任务结束日期为 2024-11-8
            判断当前日期是否为2024-11-7：D.is_target_date_reached(1, (2024, 11, 8))
            判断当前日期是否为2024-11-2：D.is_target_date_reached(6, (2024, 11, 8))
        """
        year, month, day = year_month_day
        # 获取当前日期
        current_date = self.now.date()
        # 获取结束日期
        end_date = datetime(year, month, day).date()
        # 计算结束日期的前 days 天日期
        target_date = end_date - timedelta(days=days)

        # 比较当前日期和目标日期
        return current_date >= target_date

    def run_time(self):
        """
        运行耗时
        """
        self.msg_append(
            f"\n【运行耗时】\n耗时：{int(time.time() - self._start_time)} s"
        )


def yield_dld_objects():
    """
    返回大乐斗实例对象
    """
    dld_cookies: list[str] = read_yaml("settings.yaml", "DALEDOU_ACCOUNT")
    for cookie in dld_cookies:
        dld = InItDaLeDou(cookie)
        if dld.session is None:
            continue
        if dld.func_map is None:
            continue

        D = DaLeDou(dld.qq, dld.session, dld.yaml, dld.func_map)
        D.msg_append(dld.start_time)
        yield D

        dld.remove_logger_handler()
