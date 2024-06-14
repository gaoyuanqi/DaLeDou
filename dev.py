'''
读取命令行参数，支持以下命令启动脚本：

    run 模式：
        python dev.py run one    执行第一轮大乐斗任务
        python dev.py run two    执行第二轮大乐斗任务

    dev 模式：
        python dev.py dev [func_name]    func_name 指run.py中的某个大乐斗任务函数
'''
from daledou.run import get_argparse

get_argparse()
