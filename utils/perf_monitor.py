import logging
from functools import wraps
from timeit import default_timer


def measure_runtime(f):
    """
    Measures the runtime of a function. Used as a decorator
    Args:
        f: function

    Returns:
        wrapper
    """

    @wraps(f)
    def wrap(*args, **kw):
        ts = default_timer()
        result = f(*args, **kw)
        te = default_timer()
        logging.getLogger("measure_runtime").info(
            "Function %r: %2.4f s", f.__name__, te - ts
        )
        return result

    return wrap


# =================================================
