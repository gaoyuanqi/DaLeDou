import re
from datetime import datetime
from pathlib import Path
from shutil import copy

import requests
import yaml
from loguru import logger
from requests import Session

from daledou import HEADERS, MISSIONS_ONE, MISSIONS_TWO, NOW


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


def clean_cookie(cookie: str) -> str:
    """
    清洁大乐斗Cookie，改成 'RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=xx'
    """
    required_keys = ["RK", "ptcz", "openId", "accessToken", "newuin"]
    for key in required_keys:
        if key not in cookie:
            raise ValueError(f"大乐斗Cookie缺失 {key} 字段：\n{cookie}")

    ck = ""
    for key in ["RK", "ptcz", "openId", "accessToken", "newuin"]:
        result = re.search(f"{key}=(.*?); ", f"{cookie}; ", re.S).group(0)
        ck += f"{result}"
    return ck[:-2]


def get_qq(cookie: str) -> str:
    """
    从清洁的大乐斗Cookie中获取QQ
    """
    return re.search(r"newuin=(\d+)", cookie, re.S).group(1)


def session_add_cookie(cookie: str) -> Session | None:
    """
    向Session添加大乐斗Cookie，若Cookie有效则返回Session，否则返回None
    """
    url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
    with requests.Session() as session:
        session.cookies.set("Cookie", cookie)
        for _ in range(3):
            res = session.get(url, headers=HEADERS, allow_redirects=False)
            res.encoding = "utf-8"
            if "商店" in res.text:
                return session


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


def create_qq_yaml(qq: str) -> None:
    """
    基于daledou.yaml创建一份以qq命名的yaml配置文件
    """
    default_path = Path("./config/daledou.yaml")
    create_path = Path(f"./config/{qq}.yaml")
    if not create_path.exists():
        copy(default_path, create_path)
        logger.success(f"创建文件 {create_path}")


def get_dld_index_html(session: Session) -> str | None:
    """
    获取大乐斗首页HTML源码
    """
    url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
    for _ in range(3):
        response = session.get(url, headers=HEADERS)
        response.encoding = "utf-8"
        html = response.text
        if "商店" in html:
            return html.split("【退出】")[0]


def map_mission_names_to_function_names(missions: list[str]) -> list[str]:
    """
    将大乐斗首页任务名称映射为 run.py 中相应的函数名称
    """
    _data = {
        # 键为大乐斗首页任务名称，值为函数名称
        "5.1礼包": "五一礼包",
    }
    return [_data.get(k, k) for k in missions]


def init_config():
    """
    初始化账号配置，若Cookie有效则返回包含账号数据的生成器
    """
    dld_cookie: list[str] = read_yaml("settings.yaml", "DALEDOU_ACCOUNT")
    for cookie in dld_cookie:
        ck: str = clean_cookie(cookie)
        qq: str = get_qq(ck)

        # 获取大乐斗session
        dld_session = session_add_cookie(ck)

        if dld_session is None:
            logger.warning(f"{qq}：Cookie无效")
            push(f"{qq}：Cookie无效", ck)
            continue
        logger.success(f"{qq}：Cookie有效")

        # 为当前账号创建yaml任务配置文件
        create_qq_yaml(qq)
        # 读取当前账号任务配置
        _read_yaml = read_yaml(f"{qq}.yaml")

        # 获取大乐斗首页HTML
        dld_html = get_dld_index_html(dld_session)
        if dld_html is None:
            logger.warning(f"{qq}：大乐斗首页未找到，可能官方繁忙或者维护")
            push(f"{qq} 大乐斗首页未找到", "大乐斗首页未找到，可能官方繁忙或者维护")
            continue

        # 过滤大乐斗首页不存在的任务
        _one = [k for k in MISSIONS_ONE if k in dld_html]
        _two = [k for k in MISSIONS_TWO if k in dld_html]

        yield {
            "QQ": qq,
            "YAML": _read_yaml,
            "SESSION": dld_session,
            "MISSIONS": {
                "one": map_mission_names_to_function_names(_one),
                "two": map_mission_names_to_function_names(_two),
            },
        }


def create_qq_log(qq: str) -> int:
    """
    为当前QQ创建当天日志文件，返回日志记录器的标识符
    """
    log_dir = Path(f"./log/{qq}")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'{NOW.strftime("%Y-%m-%d")}.log'
    return logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <4} | {message}",
        enqueue=True,
        encoding="utf-8",
        retention="30 days",
    )


def get_datetime_weekday() -> str:
    """
    获取当前的日期和时间，并附加星期信息：2024-09-01 14:35:18 周日
    """
    name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    now = datetime.now()
    week = now.weekday()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    return f"{formatted_now} {name[week]}"


def remove_none_and_join(content: list[str | None]) -> str:
    """
    移除列表中的所有 None 值，并将剩余元素用换行符连接成一个字符串
    """
    return "\n".join(list(filter(None, content)))
