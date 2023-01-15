import time

from schedule import every, repeat, run_pending

from src.daledou._run import _daledouone, _daledoutwo, _daledoucookie


@repeat(every(30).minutes)
def job():
    # 每隔30分钟检测cookie有效性
    _daledoucookie()


@repeat(every().day.at('13:01'))
def job_1():
    # 每天 13:01 运行第一轮
    _daledouone()


@repeat(every().day.at('20:01'))
def job_2():
    # 每天 20:01 运行第二轮
    _daledoutwo()


if __name__ == '__main__':
    # 立即检测cookie有效性
    _daledoucookie()
    # 开始定时运行
    while True:
        run_pending()
        time.sleep(1)
