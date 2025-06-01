import re
import time
from datetime import datetime
from functools import lru_cache
from typing import Any, Pattern, Self

from loguru import logger
from requests import Session

from .config_manager import push


class DaLeDou:
    """
    大乐斗实例方法
    """

    pattern_cache = lru_cache(maxsize=256)(re.compile)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    }

    def __init__(
        self,
        qq: str,
        session: Session,
        config: dict[str, Any],
        func_names: dict[str, list[str]],
    ):
        self._qq = qq
        self._session = session
        self._config = config
        self._func_names = func_names

        self._start_time = time.time()
        self._now = datetime.now()

        # 状态信息
        self._pushplus_content: list[str] = [
            f"{self._now.strftime('%Y-%m-%d %H:%M:%S')} 星期{self.week}"
        ]
        self.html: str | None = None
        self.current_task: str | None = None
        self.last_log: str | None = None

        self._default_pattern = self._compile_pattern(r"<br />(.*?)<")

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
    def config(self) -> dict[str, Any]:
        return self._config

    @property
    def func_names_one(self) -> list[str]:
        return self._func_names.get("one", [])

    @property
    def func_names_two(self) -> list[str]:
        return self._func_names.get("two", [])

    @classmethod
    def _compile_pattern(cls, pattern: str) -> Pattern:
        return cls.pattern_cache(pattern, re.DOTALL)

    def get(self, path: str) -> str | None:
        """发送GET请求获取HTML源码"""
        url = f"https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{path}"
        for _ in range(3):
            response = self._session.get(url, headers=self.headers, timeout=10)
            response.encoding = "utf-8"
            self.html = response.text
            if "系统繁忙" in self.html:
                time.sleep(0.2)
                continue
            elif "操作频繁" in self.html:
                time.sleep(0.8)
                continue
            return self.html

    def find(self, regex: str | None = None) -> str | None:
        """返回成功匹配的首个结果"""
        if not self.html:
            return None

        pattern = self._compile_pattern(regex) if regex else self._default_pattern
        _match = pattern.search(self.html)
        return _match.group(1) if _match else None

    def findall(self, regex: str, html: str | None = None) -> list[str]:
        """匹配所有结果"""
        content = html or self.html
        if not content:
            return []

        return re.findall(regex, content, re.DOTALL)

    def log(self, info: str, task_name: str | None = None) -> Self:
        """记录日志信息"""
        task = task_name or self.current_task
        logger.info(f"{self._qq}|{task}|{info}")
        self.last_log = info
        return self

    def append(self, info: str | None = None) -> None:
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
        content = info or self.last_log
        if content:
            self._pushplus_content.append(content)

    def pushplus_content(self) -> str:
        """pushplus正文内容"""
        elapsed = int(time.time() - self._start_time)
        self._pushplus_content.append(f"\n【运行耗时】{elapsed}秒")
        return "\n".join(self._pushplus_content)

    def pushplus_send(self, title: str) -> None:
        """发送pushplus通知"""
        push(
            title=f"{self._qq} {title}",
            content=self.pushplus_content(),
        )
