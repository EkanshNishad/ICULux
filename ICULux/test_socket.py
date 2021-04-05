import json
import time
import numpy as np
import flask
import mysql
#import numpy as np
from engineio.async_drivers import gevent
from flask import Flask, render_template, flash, redirect, request, session, abort, jsonify, url_for, Response, \
     stream_with_context, render_template_string
from flaskext.mysql import MySQL
from mysql import connector
import re
import os

from pyspark.sql import SQLContext, SparkSession
import pyspark.sql.functions as sqf
import os
from pyspark.sql.types import *
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql.functions import col
from skmultiflow.drift_detection.adwin import ADWIN
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "sdfsdfssefe"
socketio = SocketIO(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'icu'

patientdata = None
doctordata = None

flag = False
state = 0
index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
dict = {}
cond = {}
rows = None
previous_variance = {}
adwin = {}


def temp():
    return render_template("data.html", data=patientdata)


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # rv.enable_buffering(5)
    return rv


def int_or_float(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def trendline(data, order=1):
    index = list(range(1, len(data) + 1))
    data = list(map(int, data))

    coeffs = np.polyfit(index, data, order)
    slope = coeffs[-2]
    return float(slope)


def find_current_nature(name, val1, val2=0, val3=0):
    flag = False
    state = 0
    message = ""
    if (name == "RESP"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) < 12):
                message += "respiratory rate is low.\n"
                state = -1
            elif (int_or_float(val1) > 27):
                message += "respiratory rate is critically high.\n"
                state = 1
                flag = True
            elif (int_or_float(val1) > 24):
                message += "respiratory rate is high.\n"
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "CBP"):
        if (val1 != '0' and val2 != '0' and val3 != '0' and val1[0] != '['):
            if ((int_or_float(val2) > 180) or (int_or_float(val3) > 120)):
                message += "Patient have Hypertensive Central Blood Pressure.\n"
                state = 1
                flag = True
            elif ((int_or_float(val2) > 160) or (int_or_float(val3) > 90)):
                message += "Central Blood Pressure is high at stage2.\n"
                state = 1
            elif ((int_or_float(val2) > 140) or (int_or_float(val3) > 80)):
                message += "Central Blood Pressure is high at stage1.\n"
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "ABP"):
        if (val1 != '0' and val2 != '0' and val3 != '0' and val1[0] != '['):
            if ((int_or_float(val2) > 148) or (int_or_float(val3) > 94)):
                message += "Patient is in hypertensive arterial blood pressure.\n"
                state = 1
                flag = True
            elif ((int_or_float(val2) > 160) or (int_or_float(val3) > 88)):
                message += "Arterial Blood Pressure is high at stage2.\n"
                state = 1
            elif ((int_or_float(val2) > 140) or (int_or_float(val3) > 80)):
                message += "Arterial Blood Pressure is high at stage1.\n"
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "NBP"):
        if (val1 != '0' and val2 != '0' and val3 != '0' and val1[0] != '['):
            if ((int_or_float(val2) > 160) or (int_or_float(val3) > 100)):
                message += "Patient have Stage-2 hypertensive non-invasive blood pressure.\n"
                state = 1
                flag = True
            elif ((int_or_float(val2) > 160) or (int_or_float(val3) > 88)):
                message += "Patient is in Stage-1 hypertensive non-invasive blood pressure.\n"
                state = 1
            elif ((int_or_float(val2) > 140) or (int_or_float(val3) > 80)):
                message += "Non-invasive blood pressure is higher than normal."
                state = 1
            elif (((int_or_float(val2) < 90) or (int_or_float(val3) < 60))):
                message += "Patient have Hypotensive non-invasive blood pressure."
                stage = -1
            else:
                state = 0
        else:
            state = 0
    elif (name == "SpO2"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) < 85):
                message += "Patient is severly hypoxic"
                state = -1
                flag = True
            elif (int_or_float(val1) < 88):
                message += "Patient is hypoxic"
                state = -1
                flag = True
            elif (int_or_float(val1) < 93):
                message += "Oxygen level is below normal range."
                state = -1
            else:
                state = 0
        else:
            state = 0
    elif (name == "CO"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) <= 2):
                message += "Cardiac output is critically low."
                state = -1
            else:
                state = 0
        else:
            state = 0
    elif (name == "PAP"):
        if (val1 != '0' and val3 != '0' and val2 != '0' and val1[0] != '['):
            if ((int_or_float(val1) > 25) or (int_or_float(val2) > 40) or (int_or_float(val3) > 18)):
                flag = True
                message += "Pulmonary artery Pressure is abnormally high.\n"
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "LAP"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) < 20):
                message += "LAP Score is extremely low.\n"
                state = -1
                flag = True
            elif (int_or_float(val1) < 40):
                message += "LAP Score is below normal.\n"
                state = -1
            elif (int_or_float(val1) > 120):
                message += "LAP Score is higher than normal range.\n"
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "EtCO2"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) > 50):
                message += "End tidal CO2 level is above critical range.\n"
                flag = True
                state = 1
            elif (int_or_float(val1) < 10):
                message += "End tidal CO2 level is below critical level.\n"
                flag = True
                state = -1
            elif (int_or_float(val1) > 45):
                message += "End tidal CO2 level is high in the patient.\n"
                state = 1
            elif (int_or_float(val1) < 35):
                message += "End tidal CO2 level is low in the patient.\n"
                state = -1
            else:
                state = 0
        else:
            state = 0
    elif (name == "AWRR"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) < 9):
                message += "Airway Respiratory Rate is low in the patient.\n"
                flag = True
                state = -1
            elif (int_or_float(val1) > 30):
                message += "Airway Respiratory Rate is high in the patient.\n"
                flag = True
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "PAWP"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) < 4):
                message += "Pulmonary Artery wedge pressure is at critical level.\n"
                flag = True
                state = -1
            elif (int_or_float(val1) < 6):
                message += "Pulmonary Artery Wedge Pressure is below normal level.\n"
                state = -1
            elif (int_or_float(val1) > 18):
                message += "Pulmonary Artery wedge pressure is at critical level.\n"
                flag = True
                state = 1
            elif (int_or_float(val1) > 12):
                message += "Pulmonary Artery Wedge Pressure is aboe normal range.\n"
                state = 1
            else:
                state = 0
        else:
            state = 0
    elif (name == "IMCO2"):
        if (val1 != '0' and val1[0] != '['):
            if (int_or_float(val1) < 2):
                message += "Inspired minimum CO2 is below normal level.\n"
                state = -1
                flag = True

    if (flag == True):
        message += "Patient needs urgent care and medication."

    return [message, state, flag]



@app.route('/data_stream', methods=['GET','POST'])
def generate():
    temp()
    def inner():

        global rows
        global dict
        # simulate a long process to watch
        ntu = ""
        # print(rows)

        for i in rows:
            name = i[0]
            val1 = i[1]
            val2 = i[2]
            val3 = i[3]

            time.sleep(1)
            # this value should be inserted into an HTML template
            if (val3 != None and val2 != None):
                if (len(dict[name]) <= 10):
                    dict[name].append(val3)
                else:
                    dict[name].pop(0)
                    dict[name].append(val3)
                    # yield str(name) + " " + str(val1) + " " + str(val2) + " " + str(val3) + '<br/>\n'
                print(name + " : " + val1 + "\t" + val2 + "\t" + val3)
                templist = find_current_nature(str(name), str(val1), str(val2), str(val3))
                adwin[name].add_element(int_or_float(val3))
                if (templist[2] == True):
                    print("Current Nature: Critical")
                    condition = "Critical"
                    message = templist[0]

                    if ((templist[1] > 0) and (trendline(data=dict[name]) > 0)):
                        ntu = "Depreciating at high rate"
                    elif ((templist[1] < 0) and (trendline(data=dict[name]) < 0)):
                        ntu = "Depreciating at high rate"
                    else:
                        ntu = "recovery would take time"
                    print("Nature: " + ntu)
                elif (templist[1] != 0):
                    print("Current Nature: Needs Care")
                    condition = "Needs Care"
                    message = templist[0]
                    if (len(dict[name]) >= 10):
                        if ((templist[1] > 0) and (trendline(data=dict[name]) > 0)):
                            ntu = "Degrading"
                        elif ((templist[1] < 0) and (trendline(data=dict[name]) < 0)):
                            ntu = "Degrading"
                        else:
                            ntu = "Improving"
                        print("Nature: " + ntu)
                else:
                    print("Current Nature: Normal")
                    condition = "Normal"

                if adwin[name].detected_change():
                    print("Percentage Variance for name: {}".format(adwin[name].variance))
                    previous_variance[name] = adwin[name].variance
                data2 = {
                    "name": name,
                    "val1": val1,
                    "val2": val2,
                    "val3": val3,
                    "condition": cond,
                    "message": message,
                    "change": ntu
                }
                json_file = json.dumps(data2)
                json_file = json.loads(json_file)
                yield json_file
            else:
                if (len(dict[name]) <= 10):
                    dict[name].append(val1)
                else:
                    dict[name].pop(0)
                    dict[name].append(val1)
                    # yield str(name) + " " + str(val1) + '<br/>\n'
                print(name + " : " + val1)
                templist = find_current_nature(str(name), str(val1))
                condition = templist[0]
                adwin[name].add_element(int_or_float(val1))
                if (templist[2] == True):
                    print("Current Nature: Critical")
                    print(templist[0])
                    condition = "Critical"
                    message = templist[0]

                    if ((templist[1] > 0) and (trendline(data=dict[name]) > 0)):
                        ntu = "Depreciating at high rate"
                    elif ((templist[1] < 0) and (trendline(data=dict[name]) < 0)):
                        ntu = "Depreciating at high rate"
                    else:
                        ntu = "recovery would take time"
                    print("Nature: " + ntu)
                elif (templist[1] != 0):
                    print("Current Nature: Needs Care")
                    print(templist[0])
                    condition = "Needs Care"
                    message = templist[0]

                    if (len(dict[name]) >= 10):
                        if ((templist[1] > 0) and (trendline(data=dict[name]) > 0)):
                            ntu = "Degrading"
                        elif ((templist[1] < 0) and (trendline(data=dict[name]) < 0)):
                            ntu = "Degrading"
                        else:
                            ntu = "Improving"
                        print("Nature: " + ntu)
                else:
                    print("Current Nature: Normal")

                if adwin[name].detected_change():
                    print("Percentage Variance{}".format(adwin[name].variance))
                previous_variance[name] = adwin[name].variance
                data2 = {
                    "name": name,
                    "val1": val1,
                    "val2": val2,
                    "val3": val3,
                    "condition": cond,
                    "message": message,
                    "change": ntu
                }
                json_file = json.dumps(data2)
                json_file = json.loads(json_file)
                yield json_file
    return Response(stream_with_context(stream_template("data2.html", data=patientdata, data2=inner())))



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/about")
def about():
     return render_template('about.html')
@app.route("/contact")
def contact():
     return render_template('contact.html')
@app.route('/login', methods=['GET','POST'])
def do_admin_login():
     if request.method=='POST':
          name = request.form.get('username')
          password = request.form.get('password')
          cnx = mysql.connector.connect(user='root', password='', host='localhost', database='icu')
          cursor = cnx.cursor()
          cursor.execute('SELECT * FROM DOCTOR WHERE Name = %s and Password = %s', (name,password,))
          account = cursor.fetchall()
          cursor.close()
          if account:
               global doctordata
               doctordata = account
               return render_template("find_patient.html", data=doctordata)
          else:
               msg = "Invalid Username or password"
               return render_template('index.html', msg = msg)

@app.route('/find_patient', methods=['POST','GET'])
def find_patient():
     msg = ""
     if(request.method == 'POST'):
          print(request.form['pid'])
          if 'pid' in request.form:
               pid = request.form['pid']
               if re.match(r'[A-Za-z]+', pid):
                    msg += "Patient id should be numeric in value."
                    return render_template("find_patient.html",  data=doctordata, msg=msg)
               elif re.match(r'[0-9]+', pid):
                    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='icu')
                    cursor = cnx.cursor()
                    cursor.execute('SELECT * FROM Patient_Information WHERE pid = %s', (pid,))
                    details = cursor.fetchall()
                    cursor.close()
                    global patientdata
                    patientdata = details
                    if patientdata:
                         return redirect(url_for('data'))
                    else:
                         msg = "Patient record not found"
                         return render_template("find_patient.html", data=doctordata, msg=msg)
               else:
                    msg += "Please enter valid input."
                    return render_template("find_patient.html", data=doctordata, msg=msg)
          else:
               msg += "Please fill the form."
               return render_template("find_patient.html", data=doctordata, msg=msg)

@app.route('/data', methods=['POST','GET'])
def data():

     global rows
     dict.clear()
     spark = SparkSession.builder.master('local[*]').appName('ICULux').config("spark.files.overwrite", "true") \
          .config("spark.worker.cleanup.enabled", "true").getOrCreate()
     sc = spark.sparkContext
     url = "https://physionet.org/files/mimicdb/1.0.0/037/03700001.txt"
     sc.addFile(url)

     # first get all lines from file
     with open(SparkFiles.get("03700001.txt"), 'r') as f:
          lines = f.readlines()

     # remove spaces
     lines = [line.replace(' ', '') for line in lines]

     # finally, write lines in the file
     with open("tmp/temp.txt", 'w') as f:
          f.writelines(lines)

     schema = StructType([
          StructField("Name", StringType(), True),
          StructField("val1", StringType(), True),
          StructField("val2", StringType(), True),
          StructField("val3", StringType(), True)])

     readfrmfile = spark.read.csv("tmp/temp.txt", header="false", schema=schema, sep='\\t')

     readfrmfile = readfrmfile.filter((col('Name').startswith('[') == False) & (col('Name') != "INOP")
                                      & (col('Name') != "ALARM"))
     distinct_rows = readfrmfile.select(readfrmfile.Name).distinct().collect()
     distinct_rows = [r.Name for r in distinct_rows]

     global adwin
     for name in distinct_rows:
          dict[name] = []
          cond[name] = False
          adwin[name] = ADWIN()
          previous_variance[name] = 0


     rows = readfrmfile.collect()

     os.remove("tmp/temp.txt")
     return render_template("data.html", data=patientdata)


if __name__ == '__main__':
    socketio.run(app)