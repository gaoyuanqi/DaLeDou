import time

from schedule import every, repeat, run_pending

from daledou import run


@repeat(every(30).minutes)
def job_timing():
    # 每隔 30 分钟检测cookie有效期
    run('check')


@repeat(every().day.at('13:05'))
def job_one():
    # 每天 13:05 运行第一轮
    run('one')


@repeat(every().day.at('20:01'))
def job_two():
    # 每天 20:01 运行第二轮
    run('two')


if __name__ == '__main__':
    run()
    while True:
        run_pending()
        time.sleep(1)
