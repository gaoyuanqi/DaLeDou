import argparse
import time

from schedule import every, repeat, run_pending

from daledou.other import run_other
from daledou.one import run_one
from daledou.two import run_two
from daledou.utils import yield_dld_objects


@repeat(every(2).hours)
def job_timing():
    # 每隔 2 小时检测Cookie有效期
    _run_func("check")


@repeat(every().day.at("13:10"))
def job_one():
    # 每天 13:10 运行第一轮
    _run_func("one")


@repeat(every().day.at("20:01"))
def job_two():
    # 每天 20:01 运行第二轮
    _run_func("two")


def _get_parse_args() -> tuple[str, list[str]]:
    """
    解析命令行参数，返回运行模式和额外参数列表
    """
    parser = argparse.ArgumentParser(description="处理命令行参数")
    parser.add_argument("mode", nargs="?", default="", help="运行模式")
    parser.add_argument("--extra", help="额外的参数")

    args, unknown_args = parser.parse_known_args()
    return args.mode, unknown_args


def run_serve():
    print("--" * 20)
    mode, unknown_args = _get_parse_args()
    if mode not in ["", "check", "one", "two", "other"]:
        print(f"不存在 {mode} 运行模式")
        return

    if not mode:
        _run_func("check")
        print("脚本将在 13:10 和 20:01 定时运行...")
        while True:
            run_pending()
            time.sleep(1)
    else:
        _run_func(mode, unknown_args)


def _run_func(mode: str, unknown_args=None):
    if mode == "check":
        for _ in yield_dld_objects():
            print("--" * 20)
    elif mode == "one":
        run_one(unknown_args)
    elif mode == "two":
        run_two(unknown_args)
    elif mode == "other":
        run_other(unknown_args)
