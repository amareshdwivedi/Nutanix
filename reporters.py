__author__ = 'subashatreya'


class CheckerResult:
    def __init__(self, name, passed=None, message=None):
        self.name = name
        self.passed = passed
        self.message = message
        self.steps = []

    def add_check_result(self, step):
        self.steps.append(step)

    def set_status(self, status):
        self.status = status

    def set_message(self, message):
        self.message = message

    def to_dict(self):
        dict_obj = {"name": self.name, "pass:": self.passed, "message:": self.message}

        if len(self.steps) > 0:
            steps_dict = []
            for step in self.steps:
                steps_dict.append(step.to_dict())
            dict_obj["checks"] = steps_dict

        return dict_obj


class DefaultConsoleReporter:

    def __init__(self, name):
        self.name = name

    def notify_progress(self, message):
        print self.name + " : " + message


