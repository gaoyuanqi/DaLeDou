import argparse
import time

from schedule import every, repeat, run_pending

from .config_manager import ConfigMarager
from .daledou import DaLeDou
from .session import generate_daledou
from ..tasks.other import run_other_args
from ..tasks.one import run_one_all, run_one_args
from ..tasks.two import run_two_all, run_two_args


@repeat(every().day.at(ConfigMarager.one_run_time))
def _run_one():
    # 每天定时运行第一轮任务
    for d in generate_daledou():
        run_one_all(d, ConfigMarager.one_round_name)
    print(ConfigMarager.timing_info)


@repeat(every().day.at(ConfigMarager.two_run_time))
def _run_two():
    # 每天定时运行第二轮任务
    for d in generate_daledou():
        run_two_all(d, ConfigMarager.two_round_name)
    print(ConfigMarager.timing_info)


def _run_timing():
    """启动定时进程"""
    for _ in generate_daledou():
        print("--" * 20)
    print(ConfigMarager.timing_info)
    while True:
        run_pending()
        time.sleep(1)


def _handle_task(
    d: DaLeDou,
    args: list[str],
    all_runner: callable,
    args_runner: callable,
    task_name: str,
) -> None:
    if args:
        args_runner(d, args)
    else:
        all_runner(d, task_name)


def run_serve() -> None:
    """命令行入口点"""
    parser = argparse.ArgumentParser(
        description="大乐斗任务调度程序", formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--settings", action="store_true", help="查看任务配置")
    group.add_argument("--timing", action="store_true", help="启动定时任务守护进程")
    group.add_argument(
        "--one",
        nargs="*",
        metavar="FUNCS",
        help="立即运行第一轮任务（可选具体函数）\n示例: --one 邪神秘宝 矿洞",
    )
    group.add_argument(
        "--two",
        nargs="*",
        metavar="FUNCS",
        help="立即运行第二轮任务（可选具体函数）\n示例: --two 邪神秘宝 侠士客栈",
    )
    group.add_argument(
        "--other",
        nargs="*",
        metavar="FUNCS",
        help="立即运行其它任务（可选具体函数）\n示例: --other 神装 背包",
    )

    args = parser.parse_args()
    print("--" * 20)
    if args.timing:
        _run_timing()
    elif args.one is not None:
        for d in generate_daledou():
            _handle_task(
                d, args.one, run_one_all, run_one_args, ConfigMarager.one_round_name
            )
    elif args.two is not None:
        for d in generate_daledou():
            _handle_task(
                d, args.two, run_two_all, run_two_args, ConfigMarager.two_round_name
            )
    elif args.other is not None:
        for d in generate_daledou():
            run_other_args(d, args.other)
