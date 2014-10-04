__author__ = 'subashatreya'


class CheckerResult:
    def __init__(self, name, status=None, message=None):
        self.name = name
        self.status = status
        self.message = message
        self.steps = []

    def add_step_result(self, step):
        self.steps.append(step)

    def set_status(self, status):
        self.status = status

    def set_message(self, message):
        self.message = message

    def to_dict(self):
        dict_obj = {"name": self.name, "status:": self.status, "message:": self.message}

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


