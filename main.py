"""
支持以下命令启动脚本:
    定时运行第一轮和第二轮:
        python main.py --timing

    手动运行第一轮大乐斗任务:
        python main.py --one

    手动运行 one.py 中的 邪神秘宝:
        python main.py --one 邪神秘宝

    手动运行第二轮大乐斗任务:
        python main.py --two

    手动运行 two.py 中的 邪神秘宝:
        python main.py --two 邪神秘宝

    手动运行 other.py 中的 神装:
        python main.py --other 神装

如果使用 uv 包管理器，则将上面 python 替换为 uv run
"""

import argparse
import time

from schedule import every, repeat, run_pending

from daledou.other import run_other
from daledou.one import run_one
from daledou.two import run_two
from daledou.utils import yield_dld_objects


@repeat(every().day.at("13:10"))
def job_one():
    # 每天 13:10 运行第一轮
    run_one()


@repeat(every().day.at("20:01"))
def job_two():
    # 每天 20:01 运行第二轮
    run_two()


def run_serve():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description="处理多个可选参数的示例程序")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--timing", nargs="*", metavar="不传参数", help="检查大乐斗配置")
    group.add_argument("--one", nargs="*", metavar="函数名称", help="大乐斗第一轮任务")
    group.add_argument("--two", nargs="*", metavar="函数名称", help="大乐斗第二轮任务")
    group.add_argument("--other", nargs="*", metavar="函数名称", help="大乐斗其它任务")

    print("--" * 20)
    args = parser.parse_args()
    if args.timing is not None:
        for _ in yield_dld_objects():
            print("--" * 20)
        print("定时任务守护进程已启动：")
        print("第一轮默认 13:10 定时运行")
        print("第二轮默认 20:01 定时运行")
        print("\n手动运行第一轮命令：")
        print("python main.py --one 或者 uv run main.py --one")
        print("\n手动运行第二轮命令：")
        print("python main.py --two 或者 uv run main.py --two")
        print("\n强制结束脚本按键：CTRL + C")
        print("--" * 20)
        while True:
            run_pending()
            time.sleep(1)
    elif args.one is not None:
        run_one(args.one)
    elif args.two is not None:
        run_two(args.two)
    elif args.other is not None:
        run_other(args.other)


if __name__ == "__main__":
    run_serve()
