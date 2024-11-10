"""
支持以下命令启动脚本：
    python main.py        定时运行第一轮和第二轮
    python main.py check  检查大乐斗账号配置
    python main.py one    立即执行第一轮大乐斗任务
    python main.py two    立即执行第二轮大乐斗任务

携带额外参数：
    python main.py one -- 邪神秘宝  立即运行 one.py 中的 邪神秘宝
    python main.py two -- 邪神秘宝  立即运行 two.py 中的 邪神秘宝
    python main.py other -- 神装  立即运行 other.py 中的 神装
"""

from daledou.run import run_serve


if __name__ == "__main__":
    run_serve()
