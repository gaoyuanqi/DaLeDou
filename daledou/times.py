import time


def times_list() -> list:
    # 2022-05-08 09:51:13
    return [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
