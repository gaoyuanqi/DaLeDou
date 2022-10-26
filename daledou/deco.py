import time
import traceback

from loguru import logger
from decorator import decorator

from daledou.pushplus import pushplus


@decorator
def deco(func, *args, **kwargs):
    time.sleep(0.5)
    func_name = func.__name__
    try:
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        logger.info(f'【{func_name}】耗时: {round(end-start, 2)} s')
    except Exception:
        error = traceback.format_exc()
        logger.error(f'【{func_name}】error：\n{error}')
        pushplus(f'【{func_name}】异常', [error])
    time.sleep(0.5)
