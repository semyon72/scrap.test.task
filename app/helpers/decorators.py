# TODO: write scheduler decorator - for logging (wrap the executor.db.dump, ....)
#  and run_once raise CancelJob
import datetime
import functools

from schedule import CancelJob
from app import logger


def get_function_info(fn):
    if hasattr(fn, "__name__"):
        fn_name = fn.__name__
    else:
        fn_name = repr(fn)
    return fn_name


def run_once(fn):
    @functools.wraps(fn)
    def wrapper():
        fn()
        logger.info(f"Cancelling job for function [{get_function_info(fn)}]. Decorated by [run_once].")
        return CancelJob

    return wrapper


def log(fn):
    @functools.wraps(fn)
    def wrapper():
        fn_info = get_function_info(fn)
        sart_ts = datetime.datetime.now().timestamp()
        logger.info(f'run function [{fn_info}]')
        fn()
        logger.info(f'function [{fn_info}] done in {round(datetime.datetime.now().timestamp() - sart_ts, 3)}sec.')
    return wrapper
