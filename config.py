from flask import Flask
app = Flask(__name__)
# debug mode is enable or disable
app.debug = True
app.secret_key = 'aQRaFWWWaAa!#$43$aa!!!AsSSQ'


class Config:
    
    HTML_TITLE = 'Logs Viewer'    

    LASTS_VIEW_LINES = 20
        
