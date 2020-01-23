import base64
import subprocess
import time

from multiprocessing import Queue
from threading import Thread
import sh

from config import Config


class SameOriginSingleton(type):
    """
    同样的参数只有一个实例
    """
    _instances = {}

    @staticmethod
    def calc_params_identify(params):
        return base64.b64encode(str(params).encode())

    def __call__(cls, *args, **kwargs):
        params_ident = cls.calc_params_identify(str(args) + str(kwargs))
        if params_ident not in cls._instances:
            cls._instances[params_ident] = super(
                SameOriginSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[params_ident]


NEW_LINE_QUEUE = Queue()


class LogsQueue(metaclass=SameOriginSingleton):
    def __init__(self, size, log_path, monitor_time=10 * 60):
        # self.queue = Queue()
        self.log_path = log_path
        self.size = size
        self.pre_logs = []
        self.monitor_time = monitor_time
        self.start_monitor_task()

    def push_to_pre_logs(self, newline):
        if len(self.pre_logs) < self.size:
            self.pre_logs.append(newline)
        else:
            self.pre_logs.pop(0)
            self.pre_logs.append(newline)

    def get_pre_logs(self):
        # lines = subprocess.getoutput('tail -n %s "%s"' % (self.size, self.log_path))
        # [self.push_to_pre_logs(newline=line) for line in lines.split('\n')]

        # 不用上面实现, 不适用于windows
        with open(self.log_path, 'r') as f:
            f.seek(0, 2)
            total = f.tell()

            f.seek(max(total - (self.size // 10) * 1024, 0), 0)
            lines = f.readlines()[-self.size:]

        [self.push_to_pre_logs(newline=line) for line in lines]

    def run(self):
        # for line in sh.tail('-f', '-n', self.size, self.log_path, _iter=True):
        #     # print('+++++sh', line)
        #     self.push_to_pre_logs(newline=line)
        #
        #     NEW_LINE_QUEUE.put({'path': self.log_path, 'new_line': line})

        self.get_pre_logs()

        with open(self.log_path, 'r') as f:
            f.seek(0, 2)
            end_point = f.tell()
            while True:
                f.seek(end_point, 0)
                new_line = f.readline().strip()
                if not new_line:
                    # print('NO')
                    time.sleep(1)
                    # self.monitor_time -= 1 # （后台一直挂起这个死循环不太好， 设置没有操作记录就会推出循环）
                else:
                    print(new_line)
                    end_point = f.tell()  # 每次记录最后的行数在哪里
                    self.push_to_pre_logs(newline=new_line)
                    NEW_LINE_QUEUE.put({'path': self.log_path, 'new_line': new_line})

    def start_monitor_task(self):
        t = Thread(target=self.run)
        t.start()


if __name__ == '__main__':
    lq = LogsQueue(Config.LASTS_VIEW_LINES, log_path='/home/sayheya/Desktop/tmp/read_logs/logs/celery.log')
    # lq.run()
    print(666)
