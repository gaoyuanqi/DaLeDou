import re
import sys
import time
from datetime import datetime
from pathlib import Path
from shutil import copy

import requests
import yaml
from loguru import logger
from requests import Session

from daledou import HEADERS, MISSIONS_ONE, MISSIONS_TWO


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


def map_mission_names_to_function_names(missions: list[str]) -> list[str]:
    """
    将大乐斗首页任务名称映射为 run.py 中的函数名称
    """
    _data = {
        # 键为大乐斗首页任务名称，值为函数名称
        "5.1礼包": "五一礼包",
    }
    return [_data.get(k, k) for k in missions]


class InItDaLeDou:
    """
    初始化大乐斗
    """

    def __init__(self, dld_cookie: str) -> None:
        # 设置控制台输出
        self.setup_console_logger()
        # 初始化pushplus内容正文
        self.msg: list[str] = [
            f"【开始时间】\n{self.get_datetime_weekday()}",
        ]

        self.cookie: str = self.clean_cookie(dld_cookie)
        self.qq: str = self.get_qq()
        self.session = self.session_add_cookie()

        if isinstance(self.session, requests.Session):
            # 创建QQ任务配置文件
            self.create_qq_yaml()
            # 创建QQ日志文件
            self.handler_id: int = self.create_qq_log()
            # 获取大乐斗首页HTML
            self.main_page_html = self.get_dld_main_page_html()

    def setup_console_logger(self) -> int:
        """
        设置控制台输出，返回处理器id
        """
        logger.remove()
        return logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>",
        )

    def clean_cookie(self, dld_cookie: str) -> str:
        """
        清洁大乐斗Cookie，改成 'RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=xx'
        """
        required_keys = ["RK", "ptcz", "openId", "accessToken", "newuin"]
        for key in required_keys:
            if key not in dld_cookie:
                raise ValueError(f"大乐斗Cookie缺失 {key} 字段：\n{dld_cookie}")

        ck = ""
        for key in ["RK", "ptcz", "openId", "accessToken", "newuin"]:
            result = re.search(f"{key}=(.*?); ", f"{dld_cookie}; ", re.S).group(0)
            ck += f"{result}"
        return ck[:-2]

    def get_qq(self) -> str:
        """
        返回 self.cookie 中的QQ
        """
        return re.search(r"newuin=(\d+)", self.cookie, re.S).group(1)

    def session_add_cookie(self) -> Session | None:
        """
        向Session添加大乐斗Cookie，若Cookie有效则返回Session，否则返回None
        """
        url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
        with requests.Session() as session:
            session.cookies.set("Cookie", self.cookie)
            for _ in range(3):
                res = session.get(url, headers=HEADERS, allow_redirects=False)
                res.encoding = "utf-8"
                if "商店" in res.text:
                    logger.success(f"{self.qq} | Cookie有效")
                    return session

        logger.warning(f"{self.qq} | Cookie无效")
        push(f"{self.qq} | Cookie无效", self.cookie)

    def create_qq_yaml(self) -> None:
        """
        基于daledou.yaml创建一份以qq命名的yaml配置文件
        """
        default_path = Path("./config/daledou.yaml")
        create_path = Path(f"./config/{self.qq}.yaml")
        if not create_path.exists():
            copy(default_path, create_path)
        logger.success(f"任务配置：{create_path}")

    def create_qq_log(self) -> int:
        """
        创建QQ日志文件，返回日志处理器id
        """
        log_dir = Path(f"./log/{self.qq}")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        logger.success(f"任务日志：{log_file}")

        return logger.add(
            log_file,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>",
            enqueue=True,
            encoding="utf-8",
            retention="30 days",
        )

    def get_dld_main_page_html(self) -> str | None:
        """
        获取大乐斗首页HTML源码
        """
        url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
        for _ in range(3):
            response = self.session.get(url, headers=HEADERS)
            response.encoding = "utf-8"
            if "商店" in response.text:
                return response.text.split("【退出】")[0]

        logger.warning(f"{self.qq} | 大乐斗首页未找到，可能官方繁忙或者维护")
        push(f"{self.qq} 大乐斗首页未找到", "大乐斗首页未找到，可能官方繁忙或者维护")

    def get_datetime_weekday(self) -> str:
        """
        获取当前的日期和时间，并附加星期信息：2024-09-01 14:35:18 周日
        """
        name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        now = datetime.now()
        week = now.weekday()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        return f"{formatted_now} {name[week]}"

    def get_dld_yaml(self):
        """
        获取大乐斗任务配置
        """
        return read_yaml(f"{self.qq}.yaml")


class DaLeDou:
    """
    大乐斗实例方法
    """

    def __init__(self, qq: str, session: Session, mission: dict, yaml: dict):
        self.start_timing = time.time()
        self.qq = qq
        self.session = session
        self.mission = mission
        self.yaml = yaml
        self.html = None
        self.msg = None
        self.mission_name = None

    def get(self, params: str) -> str:
        """
        发送get请求获取响应内容
        """
        url = f"https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{params}"
        for _ in range(3):
            res = self.session.get(url, headers=HEADERS)
            res.encoding = "utf-8"
            self.html = res.text
            if "系统繁忙" in self.html:
                time.sleep(0.4)
            elif "操作频繁" in self.html:
                time.sleep(0.4)
            else:
                break
        return self.html

    def print_info(self, message: str, mission_name=None) -> None:
        """
        打印信息
        """
        if mission_name is None:
            mission_name = self.mission_name
        logger.info(f"{self.qq} | {mission_name}：{message}")

    def find(self, mode: str = "<br />(.*?)<", mission_name=None) -> str | None:
        """
        匹配成功返回首个结果，匹配失败返回None

        无论结果如何都会被打印并写入日志
        """
        _match = re.search(mode, self.html, re.S)
        result = _match.group(1) if _match else None
        self.print_info(result, mission_name)
        return result

    def findall(self, mode: str) -> list:
        """
        查找大乐斗HTML字符串源码中所有匹配正则表达式的子串
        """
        return re.findall(mode, self.html, re.S)

    def remove_msg_none_and_join(self) -> str:
        """
        移除列表中的所有 None 值，并将剩余元素用换行符连接成一个字符串
        """
        return "\n".join(list(filter(None, self.msg)))

    def run_time(self):
        """
        运行耗时
        """
        self.msg.append(
            f"\n【运行耗时】\n耗时：{int(time.time() - self.start_timing)} s"
        )


def yield_dld_objects():
    """
    返回大乐斗实例对象
    """
    dld_cookies: list[str] = read_yaml("settings.yaml", "DALEDOU_ACCOUNT")
    for cookie in dld_cookies:
        dld = InItDaLeDou(cookie)
        dld_qq: str = dld.qq
        dld_session = dld.session

        if dld_session is None:
            continue

        dld_main_page_html = dld.main_page_html
        if dld_main_page_html is None:
            continue

        # 过滤大乐斗首页不存在的任务
        _one = [k for k in MISSIONS_ONE if k in dld_main_page_html]
        _two = [k for k in MISSIONS_TWO if k in dld_main_page_html]

        mission = {
            "one": map_mission_names_to_function_names(_one),
            "two": map_mission_names_to_function_names(_two),
        }

        yaml = dld.get_dld_yaml()

        D = DaLeDou(dld_qq, dld_session, mission, yaml)
        D.msg = dld.msg

        yield D

        # 移除当前QQ日志处理器
        logger.remove(dld.handler_id)
