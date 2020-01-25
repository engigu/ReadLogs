import base64
import subprocess
import time, os

from multiprocessing import Queue
from threading import Thread, Lock
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
            cls._instances[params_ident] = super(SameOriginSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[params_ident]


NEW_LINE_QUEUE = Queue()   # 暂时不知道queue使用不了，会阻塞在put上，使用list代替
# TO_CHECK_LOGS_FILES_QUEUE = Queue()  # 直接把检查的文件丢进队列

#####################################
#### 使用python的with open
#### 会出现一旦文件更新， flask就会卡死
#####################################
#
# class LogsQueue(metaclass=SameOriginSingleton):
#     def __init__(self, size, log_path, monitor_time=10 * 60):
#         # self.queue = Queue()
#         self.log_path = log_path
#         self.size = size
#         self.pre_logs = []
#         self.monitor_time = monitor_time
#         self.start_monitor_task()
#
#     def push_to_pre_logs(self, newline):
#         if len(self.pre_logs) < self.size:
#             self.pre_logs.append(newline)
#         else:
#             self.pre_logs.pop(0)
#             self.pre_logs.append(newline)
#
#     def get_pre_logs(self):
#         lines = subprocess.getoutput('tail -n %s "%s"' % (self.size, self.log_path))
#         [self.push_to_pre_logs(newline=line) for line in lines.split('\n')]
#
#         # # 不用上面实现, 不适用于windows
#         # with open(self.log_path, 'r') as f:
#         #     f.seek(0, 2)
#         #     total = f.tell()
#         #     print(t)
#
#         #     f.seek(max(total - (self.size // 10) * 1024, 0), 0)
#         #     lines = f.readlines()[-self.size:]
#
#         # [self.push_to_pre_logs(newline=line) for line in lines]
#
#     def run(self):
#         # for line in sh.tail('-f', '-n', self.size, self.log_path, _iter=True):
#         #     # print('+++++sh', line)
#         #     self.push_to_pre_logs(newline=line)
#         #
#         #     NEW_LINE_QUEUE.put({'path': self.log_path, 'new_line': line})
#
#         self.get_pre_logs()
#
#         with open(self.log_path, 'r') as f:
#             f.seek(0, 2)
#             end_point = f.tell()
#             while True:
#                 f.seek(end_point, 0)
#                 new_line = f.readline().strip()
#                 if not new_line:
#                     # print('NO')
#                     time.sleep(1)
#                     # self.monitor_time -= 1 # （后台一直挂起这个死循环不太好， 设置没有操作记录就会推出循环）
#                 else:
#                     print(new_line)
#                     end_point = f.tell()  # 每次记录最后的行数在哪里
#                     self.push_to_pre_logs(newline=new_line)
#                     NEW_LINE_QUEUE.put({
#                         'path': self.log_path,
#                         'new_line': new_line
#                     })
#
#     def start_monitor_task(self):
#         t = Thread(target=self.run)
#         t.start()


class LogFilesChecker(metaclass=SameOriginSingleton):
    def __init__(
            self,
            # files_queue: Queue,
            # logs_queue: Queue,
            pre_logs_size: int,
            monitor_time: int = 10 * 60
    ):
        """
        
        """
        # self.files_queue = files_queue
        self.files_queue = []
        # self.logs_queue = logs_queue
        self.logs_queue = []
        self.pre_logs_map = {}
        self.pre_logs_size = pre_logs_size
        self.monitor_time = monitor_time

        # self.files_queue.put('|')  # 插入一轮的间隔标志
        self.files_queue.append('|')  # 插入一轮的间隔标志
        self.start_monitor_task()

    def push_newline_to_list(self, line_list: list, newline: str, size: int):
        if len(line_list) < size:
            line_list.append(newline)
        else:
            line_list.pop(0)
            line_list.append(newline)
        return line_list

    def push_to_files_queue(self, log_path):
        # 把要查看的日志路径加入队列，一般是网页提交路径，返回一个最近要看的pre_logs_size条数列表

        if log_path not in self.pre_logs_map:
            # 不存在才会推进队列
            # self.files_queue.put(log_path)
            self.files_queue.append(log_path)
            pre_logs = self.get_pre_logs(
                size=self.pre_logs_size,
                log_path=log_path
            )
            self.pre_logs_map[log_path] = {
                'logs': pre_logs,
                'mtime': os.path.getmtime(log_path),
                'lines': self.get_lines(log_path)
            }
            return pre_logs
        return self.pre_logs_map[log_path]

    def get_pre_logs(self, log_path, size):
        if not Config.SHOW_LINE_NO:
            shell = 'tail -n %s "%s"' % (size, log_path)
        else:
            # shell = 'tail -n %s "%s" | nl' % (size, log_path)
            shell = 'cat -n "%s" | tail -n %s' % (log_path, size)

        lines = subprocess.getoutput(shell)
        return lines.split('\n')

    def get_lines(self, log_path):
        # 128 app.py
        wc_line = subprocess.getoutput('wc -l "%s"' % log_path)
        return int(wc_line.split()[0])

    def run(self):
        while True:
            # log_path = self.files_queue.get()
            log_path = self.files_queue.pop(0)

            # self.files_queue.put(log_path)
            self.files_queue.append(log_path)
            if log_path == '|':
                time.sleep(1)  # 一轮，暂停一些时间
                # print('loop checker sleep 1s...', time.time())

            lp_info = self.pre_logs_map.get(log_path, None)
            if not lp_info:
                continue  # 可能存在推到队列，但是还没取到最近的几行信息

            mtime = os.path.getmtime(log_path)
            if mtime != lp_info['mtime']:
                # 文件更新了，有新日志, 获取新的更新行
                new_line_num = self.get_lines(log_path=log_path)

                d_value = new_line_num - lp_info['lines']
                new_lines = self.get_pre_logs(log_path=log_path, size=d_value)
                lp_info['mtime'] = mtime  # 更新map里的文件信息
                lp_info['lines'] = new_line_num
                try:
                    for new_line in new_lines:
                        print('更新的行：', new_line)
                        old_list = self.pre_logs_map[log_path]['logs']
                        self.pre_logs_map[log_path]['logs'] = self.push_newline_to_list(
                            line_list=old_list, newline=new_line, size=self.pre_logs_size
                        )
                        # self.logs_queue.put({
                        self.logs_queue.append({
                            'path': log_path,
                            'new_line': new_line
                        })
                        # print('+++++push', new_line, NEW_LINE_QUEUE.qsize())
                except Exception as e:
                    print('error!!!!!', e)

    def start_monitor_task(self):
        # self.test()
        t = Thread(target=self.run)
        t.start()


    def test(self):
        def get():
            while True:
                # line = f.stdout.readline()
                # socketio.emit('response', {'text': line.decode()})
                if NEW_LINE_QUEUE.empty():
                    print('************ QUEUE EMPTY!')
                else:
                    print('************ QUEUE NOT EMPTY!')
                    new_line = NEW_LINE_QUEUE.get()
                time.sleep(1)

        t = Thread(target=get)
        t.start()


LOG_FILE_CHECKER = LogFilesChecker(
    # files_queue=TO_CHECK_LOGS_FILES_QUEUE,
    # logs_queue=NEW_LINE_QUEUE,
    pre_logs_size=Config.LASTS_VIEW_LINES
)

if __name__ == '__main__':
    # lq = LogsQueue(Config.LASTS_VIEW_LINES, log_path='/home/sayheya/Desktop/tmp/read_logs/logs/celery.log')
    # lq.run()
    # print(666)
    lq = LogFilesChecker(
        # files_queue=TO_CHECK_LOGS_FILES_QUEUE,
        #                  logs_queue=NEW_LINE_QUEUE,
                         pre_logs_size=20)
    res = lq.push_to_files_queue(log_path='/home/sayheya/Desktop/tmp/read_logs/logs/celery.log')
    # lq.start_monitor_task()
