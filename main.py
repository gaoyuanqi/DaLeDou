import time

from schedule import every, repeat, run_pending

from src.daledou._run import daledou_one, daledou_two, daledou_account


@repeat(every(30).minutes)
def job():
    # 每隔30分钟检测cookie有效性
    daledou_account(str)


@repeat(every().day.at('13:01'))
def job_one():
    # 每天 13:01 运行第一轮
    daledou_one()


@repeat(every().day.at('20:01'))
def job_two():
    # 每天 20:01 运行第二轮
    daledou_two()


if __name__ == '__main__':
    # 检测cookie有效性
    daledou_account(str)
    # 开始定时运行
    while True:
        run_pending()
        time.sleep(1)
