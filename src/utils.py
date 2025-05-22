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


# 请求头
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
}


def _current_day_and_week():
    now = datetime.now()
    return now.day, now.isoweekday()


def _one() -> list:
    """
    返回当天可做的第一轮任务
    """
    day, week = _current_day_and_week()
    mission = {
        "邪神秘宝": True,
        "华山论剑": day <= 26,
        "斗豆月卡": True,
        "分享": True,
        "乐斗": True,
        "武林": True,
        "群侠": True,
        "侠侣": week in [2, 5, 7],
        "结拜": week in [1, 2],
        "巅峰之战进行中": True,
        "矿洞": True,
        "掠夺": week in [2, 3],
        "踢馆": week in [5, 6],
        "竞技场": day <= 25,
        "十二宫": True,
        "许愿": True,
        "抢地盘": True,
        "历练": True,
        "镖行天下": True,
        "幻境": True,
        "群雄逐鹿": week == 6,
        "画卷迷踪": True,
        "门派": True,
        "门派邀请赛": True,
        "会武": True,
        "梦想之旅": True,
        "问鼎天下": True,
        "帮派商会": True,
        "帮派远征军": True,
        "帮派黄金联赛": True,
        "任务派遣中心": True,
        "武林盟主": True,
        "全民乱斗": True,
        "侠士客栈": True,
        "大侠回归三重好礼": week == 4,
        "飞升大作战": True,
        "深渊之潮": True,
        "侠客岛": True,
        "时空遗迹": True,
        "世界树": True,
        "任务": True,
        "我的帮派": True,
        "帮派祭坛": True,
        "每日奖励": True,
        "领取徒弟经验": True,
        "今日活跃度": True,
        "江湖长梦": True,
        "仙武修真": True,
        "乐斗黄历": True,
        "器魂附魔": True,
        "兵法": week in [4, 6],
        "猜单双": True,
        "煮元宵": True,
        "万圣节": True,
        "元宵节": week == 4,
        "神魔转盘": True,
        "乐斗驿站": True,
        "浩劫宝箱": True,
        "幸运转盘": True,
        "冰雪企缘": True,
        "甜蜜夫妻": True,
        "乐斗菜单": True,
        "客栈同福": True,
        "周周礼包": True,
        "登录有礼": True,
        "活跃礼包": True,
        "上香活动": True,
        "徽章战令": True,
        "生肖福卡": True,
        "长安盛会": True,
        "深渊秘宝": True,
        "中秋礼盒": True,
        "双节签到": True,
        "乐斗游记": True,
        "斗境探秘": True,
        "幸运金蛋": True,
        "春联大赛": True,
        "新春拜年": True,
        "喜从天降": True,
        "节日福利": True,
        "5.1礼包": week == 4,
        "端午有礼": week == 4,
        "圣诞有礼": week == 4,
        "新春礼包": week == 4,
        "登录商店": week == 4,
        "盛世巡礼": week == 4,
        "新春登录礼": True,
        "年兽大作战": True,
        "惊喜刮刮卡": True,
        "开心娃娃机": True,
        "好礼步步升": True,
        "企鹅吉利兑": True,
        "乐斗大笨钟": True,
        "乐斗激运牌": True,
        "乐斗能量棒": True,
        "乐斗回忆录": week == 4,
        "爱的同心结": week == 4,
        "周年生日祝福": week == 4,
        "重阳太白诗会": True,
        "5.1预订礼包": True,
    }
    return [k for k, v in mission.items() if v]


def _two() -> list:
    """
    返回当天可做的第二轮任务
    """
    day, week = _current_day_and_week()
    mission = {
        "邪神秘宝": True,
        "问鼎天下": week not in [6, 7],
        "帮派商会": True,
        "任务派遣中心": True,
        "侠士客栈": True,
        "深渊之潮": True,
        "侠客岛": True,
        "背包": True,
        "镶嵌": week == 4,
        "神匠坊": day == 20,
        "每日宝箱": day == 20,
        "商店": True,
        "幸运金蛋": True,
        "新春拜年": True,
        "乐斗大笨钟": True,
    }
    return [k for k, v in mission.items() if v]


def _load_yaml(file: str, key: str | None = None):
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
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"{path} 第{e.problem_mark.line}行解析失败")


def push(title: str, content: str) -> None:
    """
    pushplus微信通知
    """
    if token := _load_yaml("settings.yaml", "PUSHPLUS_TOKEN"):
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


class InitDaLeDou:
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
            self._yaml: dict = _load_yaml(f"{self.qq}.yaml")
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
            "5.1预订礼包": "五一预订礼包",
        }
        return [_data.get(k, k) for k in missions]

    def _get_func_name(self) -> dict | None:
        """
        过滤掉未出现在大乐斗首页的任务，并将剩余任务名称映射的函数名称以字典返回
        """
        if _html := self._get_dld_main_page_html():
            one = [k for k in _one() if k in _html]
            two = [k for k in _two() if k in _html]
            return {
                "one": self._map_mission_names_to_func_names(one),
                "two": self._map_mission_names_to_func_names(two),
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

    def __init__(self, qq: str, session: Session, yaml: dict, func_name: dict):
        self._qq = qq
        self._session = session
        self._yaml = yaml
        self._func_name = func_name

        self._start_time = time.time()
        self._now = datetime.now()

        # pushplus内容正文
        self._pushplus_body: list[str] = [
            f"【开始时间】\n{self._now.strftime('%Y-%m-%d %H:%M:%S')} 星期{self.week}",
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
        return self._now.year

    @property
    def month(self) -> int:
        return self._now.month

    @property
    def day(self) -> int:
        return self._now.day

    @property
    def week(self) -> int:
        return self._now.isoweekday()

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
    dld_cookies: list[str] = _load_yaml("settings.yaml", "DALEDOU_ACCOUNT")
    for cookie in dld_cookies:
        dld = InitDaLeDou(cookie)
        if dld.session is None or dld.func_name is None:
            continue

        D = DaLeDou(dld.qq, dld.session, dld.yaml, dld.func_name)
        yield D

        dld.remove_logger_handler()
