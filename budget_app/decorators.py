
import time
from functools import wraps

import logging

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        elapsed = time.perf_counter() - start
        print(f"[실행 시간] {func.__name__}: {elapsed:.4f}초")

        return result

    return wrapper

logger = logging.getLogger(__name__)


def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("%s 실행 시작", func.__name__)

        result = func(*args, **kwargs)

        logger.info("%s 실행 완료", func.__name__)
        return result

    return wrapper


def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("%s 실행 중 오류 발생", func.__name__)
            raise

    return wrapper
