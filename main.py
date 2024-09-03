"""
支持以下命令启动脚本：
    python main.py          等同 timing
    python main.py one      立即执行第一轮大乐斗任务
    python main.py two      立即执行第二轮大乐斗任务
    python main.py check    检查大乐斗账号配置
    python main.py timing   定时运行
    python main.py dev -- [func_name]   立即运行run.py中的一个或多个函数
"""

from daledou.run import run_serve


if __name__ == "__main__":
    run_serve()
