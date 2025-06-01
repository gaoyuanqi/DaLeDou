"""
支持以下命令启动脚本:
    >>> # 定时运行第一轮和第二轮
    >>> python main.py --timing

    >>> # 立即运行第一轮大乐斗任务
    >>> python main.py --one

    >>> # 立即运行 one.py 中的 邪神秘宝
    >>> python main.py --one 邪神秘宝

    >>> # 立即运行第二轮大乐斗任务
    >>> python main.py --two

    >>> # 立即运行 two.py 中的 邪神秘宝
    >>> python main.py --two 邪神秘宝

    >>> # 立即运行 other.py 中的 神装
    >>> python main.py --other 神装

如果使用 uv 包管理器，则将上面 python 替换为 uv run
"""

from src.dld.core.cli import run_serve


if __name__ == "__main__":
    try:
        run_serve()
    except KeyboardInterrupt:
        print("\n用户强制终止任务")
