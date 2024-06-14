import time

from schedule import every, repeat, run_pending

from daledou.run import run_mission


@repeat(every(2).hours)
def job_timing():
    # 每隔 2 小时检测Cookie有效期
    run_mission('check')


@repeat(every().day.at('13:10'))
def job_one():
    # 每天 13:10 运行第一轮
    run_mission('one')


@repeat(every().day.at('20:01'))
def job_two():
    # 每天 20:01 运行第二轮
    run_mission('two')


if __name__ == '__main__':
    run_mission('check')
    while True:
        run_pending()
        time.sleep(1)
