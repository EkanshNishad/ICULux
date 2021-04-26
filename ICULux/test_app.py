import json
import pickle
import random
import time

import flask
import mysql
import numpy as np
import requests

from flask import Flask, render_template, flash, redirect, request, session, abort, jsonify, url_for, Response, \
     stream_with_context, render_template_string
from flaskext.mysql import MySQL
from mysql import connector
import pandas as pd
from pyspark.sql import SQLContext, SparkSession
import pyspark.sql.functions as sqf
import os
from pyspark.sql.types import *
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql.functions import col, countDistinct
from skmultiflow.drift_detection.adwin import ADWIN
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader


import re
import os


app = Flask(__name__)
model_fitted = pickle.load(open('model.pkl', 'rb'))

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
div = 1
pid = None
def temp():
     return render_template("data.html", data=patientdata)

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

def int_or_float(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def trendline(data, order=1):
     index = list(range(1, len(data)+1))
     data = list(map(int, data))

     coeffs = np.polyfit(index, data, order)
     slope = coeffs[-2]
     return float(slope)

def download_txt(example_txt, name):

     filename = name + ".txt"
     r = requests.get(example_txt)
     with open(filename, 'wb') as f:
          f.write(r.content)


def update_page(name, val1, val2, val3, cond, message, ntu):
     return jsonify(name=name, val1=val1, val2=val2, val3=val3, condition=cond, message=message, change=ntu)


def find_current_nature(name, val1, val2=0, val3=0):
     flag = False
     state = 0
     message = ""
     if(name == "RESP"):
          if(val1 != '0' and val1[0] != '['):
               if(int_or_float(val1) < 12):
                    message += "respiratory rate is low.\n"
                    state = -1
               elif(int_or_float(val1) > 27):
                    message += "respiratory rate is critically high.\n"
                    state = 1
                    flag = True
               elif(int_or_float(val1) > 24):
                    message += "respiratory rate is high.\n"
                    state = 1
               else:
                    state = 0
          else:
               state = 0
     elif(name == "CBP"):
          if(val1 != '0' and val2 != '0' and val3 != '0' and val1[0] != '['):
               if((int_or_float(val2) > 180) or (int_or_float(val3) > 120)):
                    message += "Patient have Hypertensive Central Blood Pressure.\n"
                    state = 1
                    flag = True
               elif((int_or_float(val2) > 160) or (int_or_float(val3) > 90)):
                    message += "Central Blood Pressure is high at stage2.\n"
                    state = 1
               elif((int_or_float(val2) > 140) or (int_or_float(val3) > 80)):
                    message += "Central Blood Pressure is high at stage1.\n"
                    state = 1
               else:
                    state = 0
          else:
               state = 0
     elif(name == "ABP"):
          if(val1 != '0' and val2 != '0' and val3 != '0' and val1[0] != '['):
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
     elif(name == "NBP"):
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
          if(val1 != '0' and val1[0] != '['):
               if (int_or_float(val1) <= 2):
                    message += "Cardiac output is critically low."
                    state = -1
               else:
                    state = 0
          else:
               state = 0
     elif (name == "PAP"):
          if(val1 != '0' and val3 != '0' and val2 != '0' and val1[0] != '['):
               if ((int_or_float(val1) > 25) or (int_or_float(val2) > 40) or (int_or_float(val3) > 18)):
                    flag = True
                    message += "Pulmonary artery Pressure is abnormally high.\n"
                    state = 1
               else:
                    state = 0
          else:
               state = 0
     elif (name == "LAP"):
          if(val1 != '0' and val1[0] != '['):
               if(int_or_float(val1) < 20):
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
               if(int_or_float(val1) > 50):
                    message += "End tidal CO2 level is above critical range.\n"
                    flag = True
                    state = 1
               elif(int_or_float(val1) < 10):
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
               if(int_or_float(val1) < 9):
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
               if(int_or_float(val1) < 4):
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
               if(int_or_float(val1) < 2):
                    message += "Inspired minimum CO2 is below normal level.\n"
                    state = -1
                    flag = True



     if(flag == True):
          message += "Patient needs urgent care and medication."

     return [message, state, flag]



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
def login():
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

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
     return render_template("newuser.html")

@app.route('/register',  methods=['POST', 'GET'])
def register():
     if (request.method == 'POST'):
          username = request.form['username']
          gender = request.form['gender']
          age = request.form['age']
          email = request.form['email']
          password = request.form['password']
          phno = request.form['phone']
          spec = request.form['spec']
          id = random.SystemRandom()
          id = id.randint(12183, 13000)
          cnx = mysql.connector.connect(user='root', password='', host='localhost', database='icu')
          cursor = cnx.cursor()
          cursor.execute('INSERT INTO DOCTOR VALUES (%s,%s,%s,%s,%s,%s)',
                         (username, age, id, email, password, spec))
          cnx.commit()
          cursor.close()
          return render_template("index.html")

@app.route('/find_patient', methods=['POST','GET'])
def find_patient():
     msg = ""
     if(request.method == 'POST'):
          print(request.form['pid'])
          if 'pid' in request.form:
               global pid
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
     url = "https://physionet.org/files/mimicdb/1.0.0/" + pid + "/RECORDS"
     download_txt(url, "tmp/RECORDS")

     with open("tmp/RECORDS.txt", 'r') as f:
         fileDirectory = f.readlines()


     del fileDirectory[0]
     del fileDirectory[0]
     os.remove("tmp/RECORDS.txt")
     flag = False

     schema = StructType([
         StructField("Name", StringType(), True),
         StructField("val1", StringType(), True),
         StructField("val2", StringType(), True),
         StructField("val3", StringType(), True)])

     for fileName in fileDirectory:
         fileName = fileName[:-1] + '.txt'
         print(fileName)
         spark = SparkSession.builder.master('local[*]').appName('ICULux').config("spark.files.overwrite", "true") \
             .config("spark.worker.cleanup.enabled", "true").getOrCreate()
         sc = spark.sparkContext
         ssc = StreamingContext(sc, 1)
         conf = SparkConf().setMaster("local[2]").setAppName("NetworkWordCount")
         url = "https://physionet.org/files/mimicdb/1.0.0/" + pid + "/" + fileName
         if os.path.isfile("tmp/" + fileName + ".txt"):
               print("file present")
         else:
               download_txt(url, "tmp/" + fileName)

         with open("tmp/" + fileName +".txt", 'r') as infile:
             lines = infile.readlines()
         lines = [line.replace(' ', '') for line in lines]
         with open('output_file.txt', 'w') as outfile:
             outfile.writelines(lines)

         readfrmfile = spark.read.csv(
             "./output_file.txt", header="false", schema=schema, sep='\\t')
         readfrmfile = readfrmfile.filter((col('Name').startswith('[') == False) & (
                 col('Name') != "INOP") & (col('Name') != "ALARM"))

         spark.conf.set("spark.sql.execution.arrow.enabled", "false")

         if flag == False:

             global distinct_rows
             distinct_rows = readfrmfile.select(readfrmfile.Name).distinct().collect()
             distinct_rows = [r.Name for r in distinct_rows]

             flag = True
             global adwin
             for name in distinct_rows:
                 dict[name] = []
                 cond[name] = False
                 adwin[name] = ADWIN()
                 previous_variance[name] = 0

             rows = readfrmfile
         else:
             rows = rows.union(readfrmfile)

         readfrmfile = readfrmfile.toPandas()

         # mention the parameter to separate
         resp = readfrmfile[readfrmfile['Name'] == "RESP"]
         del resp['val2']
         del resp['val3']

         hr = readfrmfile[readfrmfile['Name'] == "HR"]
         del hr['val2']
         del hr['val3']

         pulse = readfrmfile[readfrmfile['Name'] == "PULSE"]
         del pulse['val2']
         del pulse['val3']

         spo2 = readfrmfile[readfrmfile['Name'] == "SpO2"]
         del spo2['val2']
         del spo2['val3']

         # partitioning dataframe, window size: approx 1 minute
         resp_split = np.array_split(resp, 10)
         hr_split = np.array_split(hr, 10)
         pulse_split = np.array_split(pulse, 10)
         spo2_split = np.array_split(spo2, 10)

         # creating file for RESP(resp.txt)
         file_object = open('./resp.txt', 'a')
         for i in resp_split:
             temp = i.mean(axis=0, skipna=True)
             file_object.write(str(temp) + '\n')
         file_object.close()

         # creating file for HR(hr.txt)
         file_object = open('./hr.txt', 'a')
         for i in hr_split:
             temp = i.mean(axis=0, skipna=True)
             file_object.write(str(temp) + '\n')
         file_object.close()

         # creating file for PULSE(pulse.txt)
         file_object = open('./pulse.txt', 'a')
         for i in pulse_split:
             temp = i.mean(axis=0, skipna=True)
             file_object.write(str(temp) + '\n')
         file_object.close()

         # creating file for SpO2(spo2.txt)
         file_object = open('./spo2.txt', 'a')
         for i in spo2_split:
             temp = i.mean(axis=0, skipna=True)
             file_object.write(str(temp) + '\n')
         file_object.close()

     rows = rows.collect()

     resp_db = pd.read_csv("./resp.txt", header=None, sep="    ", names=['Name', 'RESP'], index_col=False)

     del resp_db['Name']
     resp_db = resp_db.dropna()
     resp_db = resp_db.reset_index(drop=True)
     print(resp_db.shape)

     hr_db = pd.read_csv("./hr.txt", header=None, sep="    ", names=['Name', 'HR'], index_col=False)

     del hr_db['Name']
     hr_db = hr_db.dropna()

     hr_db = hr_db.reset_index(drop=True)
     print(hr_db.shape)

     pulse_db = pd.read_csv("./pulse.txt", header=None, sep="    ", names=['Name', 'PULSE'], index_col=False)

     del pulse_db['Name']
     pulse_db = pulse_db.dropna()

     pulse_db = pulse_db.reset_index(drop=True)
     print(pulse_db.shape)

     spo2_db = pd.read_csv("./spo2.txt", header=None, sep="    ", names=['Name', 'SpO2'], index_col=False)

     del spo2_db['Name']
     spo2_db = spo2_db.dropna()

     spo2_db = spo2_db.reset_index(drop=True)
     print(spo2_db.shape)

     global  main_db
     main_db = pd.merge(resp_db, hr_db, left_index=True, right_index=True)
     main_db = pd.merge(main_db, pulse_db, left_index=True, right_index=True)
     main_db = pd.merge(main_db, spo2_db, left_index=True, right_index=True)
     # print(main_db)

     nobs = 60
     global train, test
     train, test = main_db[0:-nobs], main_db[-nobs:]
     global div
     div = 1/len(distinct_rows)


     return render_template("data2.html", data=patientdata)

@app.route('/data_stream', methods=['POST', 'GET'])
def data_stream():
     temp()




     nobs = 60
     model_fitted = pickle.load(open('model.pkl', 'rb'))

     def inner(rows, dict):

          temp_train = train.copy(deep=True)
          temp_db = main_db.copy(deep=True)
          cnr = 0
          cnhr = 0
          cnpul = 0
          cnsp = 0
          # simulate a long process to watch
          ntu = ""
          # print(rows)
          print(len(distinct_rows))
          for i in rows[-3156*len(distinct_rows):]:

               name = i[0]
               val1 = i[1]
               val2 = i[2]
               val3 = i[3]

               if name == 'RESP':
                    cnr = cnr + 1
               if name == 'HR':
                    cnhr = cnhr + 1
               if name == 'PULSE':
                    cnpul = cnpul + 1
               if name == 'SpO2':
                    cnsp = cnsp + 1

               x = {
                    'RESP': float(test.iloc[[cnr]]['RESP']),
                    'HR': float(test.iloc[[cnhr]]['HR']),
                    'PULSE': float(test.iloc[[cnpul]]['PULSE']),
                    'SpO2': float(test.iloc[[cnsp]]['SpO2']),
               }

               temp_train = temp_train.append(x, ignore_index=True)
               temp_db = temp_db.append(x, ignore_index=True)

               forecast_input = temp_train.values[-10:]
               # print(forecast_input)
               print("-----------------------------------------")
               # Forecasting
               fc = model_fitted.forecast(y=forecast_input, steps=nobs)
               df_forecast = pd.DataFrame(fc, index=temp_db.index[-nobs:], columns=train.columns)


               time.sleep(div)
               # this value should be inserted into an HTML template
               if (val3 != None and val2 != None):
                    if (len(dict[name]) <= 30):
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
                         message = ""
                         ntu = "Normal"

                    if (int_or_float(val3) == 0):
                         condition = "[INACTIVE]"
                         ntu = "[INACTIVE]"

                    if (int_or_float(val3) == dict[name][len(dict[name]) - 1]):
                         ntu = "No change detected"

                    variance_det = "No drift detected"
                    if adwin[name].detected_change():
                         print("Percentage Variance{}".format(adwin[name].variance))
                         variance_det = adwin[name].variance
                    previous_variance[name] = adwin[name].variance
                    data2 = {
                         "name": name,
                         "val1": val1,
                         "val2": val2,
                         "val3": val3,
                         "condition": condition,
                         "message": message,
                         "change": ntu,
                         "drift": variance_det
                    }



                    _data = json.dumps(data2)
                    yield f"id: 1\ndata: {_data}\nevent: online\n\n"
               else:
                    if (len(dict[name]) <= 30):
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
                         condition = "Normal"
                         message = ""
                         ntu = "Normal"

                    if(int_or_float(val1) == 0):
                         condition = "[INACTIVE]"
                         ntu = "[INACTIVE]"

                    if(int_or_float(val1) == dict[name][len(dict[name])-1]):
                         ntu = "No change detected"
                    variance_det = "No significant drift detected"
                    if adwin[name].detected_change():
                         print("Percentage Variance{}".format(adwin[name].variance))
                         variance_det = adwin[name].variance
                    previous_variance[name] = adwin[name].variance

                    if(name == 'RESP' or name == 'HR' or name == 'SpO2' or name == 'PULSE'):
                         prevalue = float(df_forecast[name].iloc[-1])
                         perchange = ((prevalue - float(val1))/float(val1))*100
                         #print(str(prevalue) + " " + str(perchange))
                         data2 = {
                              "name": name,
                              "val1": val1,
                              "val2": val2,
                              "val3": val3,
                              "condition": condition,
                              "message": message,
                              "change": ntu,
                              "drift": variance_det,
                              "prediction": str(prevalue),
                              "perchange": str(perchange)
                         }
                    else:
                         data2 = {
                              "name": name,
                              "val1": val1,
                              "val2": val2,
                              "val3": val3,
                              "condition": condition,
                              "message": message,
                              "change": ntu,
                              "drift": variance_det
                         }

                    print(data2)
                    _data = json.dumps(data2)
                    yield f"id: 1\ndata: {_data}\nevent: online\n\n"

     return Response(inner(rows,dict), mimetype='text/event-stream')



if __name__ == "__main__":
     app.secret_key = os.urandom(12)
     app.run(debug=True)
