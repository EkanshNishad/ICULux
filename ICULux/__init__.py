from flask import Flask
import dash

server=Flask(__name__)
server.config['MYSQL_HOST'] = 'localhost'
server.config['MYSQL_USER'] = 'root'
server.config['MYSQL_PASSWORD'] = ''
server.config['MYSQL_DB'] = 'icu'

server.config['DEBUG']=True
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app=dash.Dash(__name__,external_stylesheets=external_stylesheets,server=server,url_base_pathname='/stream/')
app.config['suppress_callback_exceptions']=True

from ICULux import routes
