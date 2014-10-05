__author__ = 'subashatreya'

import abc
from reporters import CheckerResult

def check(func):
    def wrapper(*args, **kwargs):
        args[0].reporter.notify_progress("Running " + func.__name__)
        result = func(*args, **kwargs)

        checker_result = CheckerResult(func.__name__, result[0], result[1])
        args[0].reporter.notify_progress("Completed " + func.__name__ + " ....... " + str(result[0]))
        args[0].result.add_check_result(checker_result)
    return wrapper


class CheckerBase:

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self.config = {}
        self.reporter = None
        self.result = CheckerResult(name)

    @abc.abstractmethod
    def configure(self, config, reporter):
        return

    @abc.abstractmethod
    def run_checks(self):
        return
