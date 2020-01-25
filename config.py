from flask import Flask
app = Flask(__name__)
# debug mode is enable or disable
app.debug = True
app.secret_key = 'aQRaFWWWaAa!#$43$aa!!!AsSSQ'


class Config:

    HTML_TITLE = 'Logs Viewer'
    
    LOG_QUEUE_CONSUMERS = 4 # log 队列消费者线程数目
    LOG_QUEUE_PER_FETCH = 10 # log 队列消费者单个线程每次取出的数目

    LASTS_VIEW_LINES = 20
    SHOW_LINE_NO = True
