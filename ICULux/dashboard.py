import io
import os
import string
from logging import Logger
from collections import deque
from pandas._typing import Level
from pyspark.sql.functions import col
from pyspark.shell import spark
from pyspark.sql import SQLContext, SparkSession

from pyspark.sql.types import *
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql import HiveContext
import pyspark.sql.functions as sqf
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import plotly
import random
import plotly.io as plt_io
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from ICULux import app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

#app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
#server=app.server
plt_io.templates["custom_dark"] = plt_io.templates["plotly_dark"]

spark = SparkSession.builder.master('local[*]').appName('ICULux').config("spark.files.overwrite", "true")\
    .config("spark.worker.cleanup.enabled","true").getOrCreate()
sc = spark.sparkContext
url = "https://physionet.org/files/mimicdb/1.0.0/055/05500001.txt"
sc.addFile(url)


# first get all lines from file
with open(SparkFiles.get("05500001.txt"), 'r') as f:
   lines = f.readlines()

# remove spaces
lines = [line.replace(' ', '') for line in lines]

 #finally, write lines in the file
with open("temp.txt", 'w') as f:
    f.writelines(lines)


schema = StructType([
    StructField("Name",StringType(),True),
    StructField("val1",StringType(),True),
    StructField("val2",StringType(),True),
    StructField("val3", StringType(), True)])


readfrmfile = spark.read.csv("temp.txt", header="false", schema=schema, sep='\\t')
df = readfrmfile.select("*").toPandas()
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#def create_dash_application(flask_app):
#    dash_app=dash.Dash(
#        server=flask_app,name="Dashboard",url_base_pathname="/stream/"
#    )
    
app.layout = html.Div([
    html.Div([
    html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        interval=1000,
        n_intervals=0),

    dcc.Graph(id='grph', figure={},animate=True)

],className="one-third column",style={'backgroundColor': colors['background']}),
html.Div([
    

    dcc.Graph(id='grph1', figure={},animate=True)

],className="one-third column",style={'backgroundColor': colors['background']}),
html.Div([
    

    dcc.Graph(id='grph2', figure={},animate=True)

],className="one-third column",style={'backgroundColor': colors['background']})
],className="row",style={'backgroundColor': colors['background']}),
    html.Div([
    html.Div([
    

    dcc.Graph(id='grph3', figure={},animate=True)

],className="one-third column",style={'backgroundColor': colors['background']}),
html.Div([
    

    dcc.Graph(id='grph4', figure={},animate=True)

],className="one-third column",style={'backgroundColor': colors['background']}),
html.Div([
    

    dcc.Graph(id='grph5', figure={},animate=True)

],className="one-third column",style={'backgroundColor': colors['background']})
],className="row",style={'backgroundColor': colors['background']})

],style={'backgroundColor': colors['background']})
#return dash_app

dff = df[df["Name"]=="SpO2"]
condition = df["Name"]=="C.O."
index = df.index
ind = index[condition]
k=list(ind) 
condition1 = df["Name"]=="Tblood"
ind1 = index[condition1]
k1=list(ind1)
condition2 = df["Name"]=="HR"
ind2 = index[condition2]
k2=list(ind2)
condition3 = df["Name"]=="SpO2"
ind3 = index[condition3]
k3=list(ind3)
condition4 = df["Name"]=="PULSE"
ind4 = index[condition4]
k4=list(ind4)
condition5 = df["Name"]=="RESP"
ind5 = index[condition5]
k5=list(ind5)

X1 = deque(maxlen=100)
X1.append(1)
Y1 = deque(maxlen=100)
Y1.append(0)
X2 = deque(maxlen=100)
X2.append(1)
Y2 = deque(maxlen=100)
Y2.append(0)
X3 = deque(maxlen=100)
X3.append(1)
Y3 = deque(maxlen=100)
Y3.append(0)
X4 = deque(maxlen=100)
X4.append(1)
Y4 = deque(maxlen=100)
Y4.append(100)
X5 = deque(maxlen=5000)
X5.append(1)
Y5 = deque(maxlen=5000)
Y5.append(100)
X6 = deque(maxlen=5000)
X6.append(1)
Y6 = deque(maxlen=5000)
Y6.append(100)
#
#
@app.callback(
     [Output(component_id='grph', component_property='figure'),
     Output('grph1','figure'),
     Output('grph2','figure'),
     Output('grph3','figure'),
     Output('grph4','figure'),
     Output('grph5','figure'),],
    [Input('my_interval','n_intervals')]
)

def update_graph(n):
    
    mk=float(df._get_value(k[n],'val1'))   
    X1.append(X1[-1]+1)
    Y1.append(mk)
    mk1=float(df._get_value(k1[n],'val1'))   
    X2.append(X2[-1]+1)
    Y2.append(mk1)
    mk2=float(df._get_value(k2[n],'val1'))
    X3.append(X3[-1]+1)
    Y3.append(mk2)
    mk3=float(df._get_value(k3[n],'val1'))
    X4.append(X4[-1]+1)
    Y4.append(mk3)
    mk4=float(df._get_value(k4[n],'val1'))
    X5.append(X5[-1]+1)
    Y5.append(mk4)
    mk5=float(df._get_value(k5[n],'val1'))
    X6.append(X6[-1]+1)
    Y6.append(mk5)
    data = go.Scatter(
    x=list(X1),
    y=list(Y1),
    name='Scatter',
    mode= 'lines+markers'
    )
    data1 = go.Scatter(
    x=list(X2),
    y=list(Y2),
    name='Scatter',
    mode= 'lines+markers')
    data2 = go.Scatter(
    x=list(X3),
    y=list(Y3),
    name='Scatter',
    mode= 'lines+markers')
    data3 = go.Scatter(
    x=list(X4),
    y=list(Y4),
    name='Scatter',
    mode= 'lines+markers')
    data4 = go.Scatter(
    x=list(X5),
    y=list(Y5),
    name='Scatter',
    mode= 'lines+markers')
    data5 = go.Scatter(
    x=list(X6),
    y=list(Y6),
    name='Scatter',
    mode= 'lines+markers')
    #fig={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X1),max(X1)]),yaxis=dict(range=[min(Y1),max(Y1)]),title="C.O.",plot_bgcolor='rgba(10,10,10)')}  
    #fig.update_layout(template='plotly_dark')
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[max(X1)-10,max(X1)]),
                                                yaxis=dict(range=[min(Y1),max(Y1)]),title="C.O.",plot_bgcolor='black',paper_bgcolor='black')},{'data': [data1],'layout' : go.Layout(xaxis=dict(range=[max(X2)-10,max(X2)]),
                                                yaxis=dict(range=[min(Y2),max(Y2)]),title="Tblood",plot_bgcolor='black',paper_bgcolor='black')},{'data': [data2],'layout' : go.Layout(xaxis=dict(range=[max(X3)-10,max(X3)]),
                                                yaxis=dict(range=[min(Y3),max(Y3)]),title="HR",plot_bgcolor='black',paper_bgcolor='black')},{'data': [data3],'layout' : go.Layout(xaxis=dict(range=[max(X4)-10,max(X4)]),
                                                yaxis=dict(range=[min(Y4),max(Y4)]),title="SpO2",plot_bgcolor='black',paper_bgcolor='black')},{'data': [data4],'layout' : go.Layout(xaxis=dict(range=[max(X5)-10,max(X5)]),
                                                yaxis=dict(range=[min(Y5),max(Y5)]),title="PULSE",plot_bgcolor='black',paper_bgcolor='black')},{'data': [data5],'layout' : go.Layout(xaxis=dict(range=[max(X6)-10,max(X6)]),
                                                yaxis=dict(range=[min(Y6),max(Y6)]),title="RESP",plot_bgcolor='black',paper_bgcolor='black')}

#readfrmfile = readfrmfile.filter(col('Name').startswith('[') == False)
#readfrmfile.show()

if __name__ == '__main__':
    app.run_server(debug=True)

#os.remove("temp.txt")




