import datetime


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class Logger:
    def __init__(self, print_info=True, log_file=None):
        self.print_info = print_info
        self.log_file = open(log_file, 'r') if log_file is not None else None

    def __del__(self):
        if self.log_file:
            self.log_file.close()

    def log(self, obj=None, message=None):
        if message is None:
            return

        cur_time = str(datetime.datetime.now())
        obj_str = '[{}]'.format(obj) if obj is not None else ''
        msg_str = '[{}]{}{}'.format(cur_time, obj_str, message)
        if self.print_info:
            print(msg_str)
        if self.log_file:
            self.log_file.write(msg_str + '\n')
