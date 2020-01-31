import json
import logging
import time, os
from collections import defaultdict

from flask import Flask, render_template, jsonify, request
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO, emit
from threading import Thread, Lock

from logs_to_queue import LOG_FILE_CHECKER, NEW_LINE_QUEUE
from config import Config

app = Flask(__name__)
# auth = HTTPBasicAuth()

socketio = SocketIO(app)


def has_run_on_linux():
    if os.name != 'posix':
        raise SystemExit('only support linux!!!!!')


def files_from_dir(dirPath, logfiles={}):
    """
    Return : list of files located in log folders
    fuction recall itself if subfolders contain file
    """
    root = dirPath.split('/')[-1]
    try:
        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)
            if os.path.isdir(childPath):
                files_from_dir(childPath, logfiles)
            else:
                logfiles[root].append([childPath, child])
    except Exception as e:
        print(e)
    return logfiles


def get_logs():
    """
    function returns list of files located in specific directory
    """
    cwd = os.getcwd()
    logdir = os.path.join(cwd, 'logs')
    files = files_from_dir(logdir, defaultdict(list))
    return files


def tail_logs_file():
    while True:
        # if NEW_LINE_QUEUE.empty():
        if not LOG_FILE_CHECKER.logs_queue:
            # print('************ QUEUE EMPTY!')
            pass
        else:
            print('************ QUEUE LEN', len(LOG_FILE_CHECKER.logs_queue))
            # new_line = NEW_LINE_QUEUE.get()
            with Lock():
                new_lines = [
                    LOG_FILE_CHECKER.logs_queue.pop(0)
                    for _ in range(Config.LOG_QUEUE_PER_FETCH)
                    if LOG_FILE_CHECKER.logs_queue
                ]

            for new_line in new_lines:
                socketio.emit('response', {
                    'text': new_line['new_line'],
                    'path': new_line['path']
                })
        time.sleep(1)


# 启动多个线程消费，目前一个跟不上
[Thread(target=tail_logs_file).start() for _ in range(Config.LOG_QUEUE_CONSUMERS)]
ALL_FP_MAP = {}


@socketio.on('client')
def client(msg):
    print("client connect..", msg)
    fp_path = msg['fp_path']

    LOG_FILE_CHECKER.push_to_files_queue(fp_path)
    for line in LOG_FILE_CHECKER.pre_logs_map[fp_path]['logs']:
        emit('response', {'text': line, 'path': fp_path})


# client断开会自动触发
@socketio.on('disconnect')
def disconnect():
    print("disconnect from", request.sid)


@app.route('/', methods=['GET'])
def main():
    """ Homepage to render data"""
    res = get_logs()
    return render_template(
        'log.html', data=res,
        html_title=Config.HTML_TITLE,
        view_num=Config.LASTS_VIEW_LINES + 10
        # view_num=3
    )


def run():
    has_run_on_linux()
    app.config['JSON_AS_ASCII'] = False
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    run()
