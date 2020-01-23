aimport datetime
import json
import logging
import time

from flask import Flask, render_template, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO, emit
from threading import Thread

from logs_to_queue import LogsQueue, NEW_LINE_QUEUE
from config import Config

# REDIS_MODEL = RedisModel(uri=Config.BACKEND_REDIS_URI)
app = Flask(__name__, template_folder='./vue')
# auth = HTTPBasicAuth()

socketio = SocketIO(app)

# TAIL_ALL_THREAD = None



def tail_logs_file():
    while True:
        # line = f.stdout.readline()
        # socketio.emit('response', {'text': line.decode()})
        if NEW_LINE_QUEUE.empty():
            print('************ QUEUE EMPTY!')
        else:
            print('************ QUEUE NOT EMPTY!')
            new_line = NEW_LINE_QUEUE.get()
            # socketio.emit('response', {'text': i + 1})
            socketio.emit('response', {'text': new_line['new_line'], 'path': new_line['path']})
        time.sleep(1)


TAIL_ALL_THREAD = Thread(target=tail_logs_file)
TAIL_ALL_THREAD.start()
ALL_FP_MAP = {}


# 发送测试消息
@app.route('/log.html', methods=['GET'])
# @auth.login_required
def log_test():
    # global TAIL_ALL_THREAD
    # if TAIL_ALL_THREAD is None:
    #     TAIL_ALL_THREAD = Thread(target=tail_logs_file)
    #     TAIL_ALL_THREAD.start()
    return render_template('log.html')


@socketio.on('client')
def client(msg):
    print("client connect..", msg)
    fp_path = msg['fp_path']

    if fp_path not in ALL_FP_MAP:
        logsObj = LogsQueue(Config.LASTS_VIEW_LINES, log_path=fp_path)
        time.sleep(1)
        ALL_FP_MAP[fp_path] = logsObj

    else:

        logsObj = ALL_FP_MAP[fp_path]

    for line in logsObj.pre_logs:
        print('返回中。。。')
        emit('response', {'text': line, 'path': fp_path})


@socketio.on('leavepage')
def leavepage(msg):
    print("leavepage..", msg)


def run():
    app.config['JSON_AS_ASCII'] = False
    handler = logging.FileHandler('logs/flask.log', encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run()
