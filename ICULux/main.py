import io
import os
import pickle
import string
from logging import Logger
import pandas as pd
import numpy as np
from pandas._typing import Level
from pyspark.sql.functions import col
from pyspark.shell import spark
from pyspark.sql import SQLContext, SparkSession
import pandas
from pyspark.sql.types import *
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql import HiveContext, window
import pyspark.sql.functions as sqf
from pyspark.streaming import StreamingContext

spark = SparkSession.builder.master('local[*]').appName('ICULux').config("spark.files.overwrite", "true")\
    .config("spark.worker.cleanup.enabled","true").getOrCreate()
sc = spark.sparkContext
url = "https://physionet.org/files/mimicdb/1.0.0/" + "252" + "/RECORDS"
sc.addFile(url)

with open(SparkFiles.get("RECORDS"), 'r') as f:
    fileDirectory = f.readlines()

del fileDirectory[0]
del fileDirectory[0]

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
    url = "https://physionet.org/files/mimicdb/1.0.0/252/" + fileName
    sc.addFile(url)

    with open(SparkFiles.get(fileName), 'r') as infile:
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

        distinct_rows = readfrmfile.select(readfrmfile.Name).distinct().collect()
        distinct_rows = [r.Name for r in distinct_rows]

        flag = True


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

resp_db = pd.read_csv("./resp.txt", header=None, sep="    ", names=['Name', 'resp'], index_col=False)

del resp_db['Name']
resp_db = resp_db.dropna()
resp_db = resp_db.reset_index(drop=True)
print(resp_db.shape)

hr_db= pd.read_csv("./hr.txt",header=None,sep="    ",names=['Name','hr'],index_col=False)

del hr_db['Name']
hr_db=hr_db.dropna()

hr_db= hr_db.reset_index(drop=True)
print(hr_db.shape)

pulse_db= pd.read_csv("./pulse.txt",header=None,sep="    ",names=['Name','pulse'],index_col=False)

del pulse_db['Name']
pulse_db=pulse_db.dropna()

pulse_db= pulse_db.reset_index(drop=True)
print(pulse_db.shape)

spo2_db= pd.read_csv("./spo2.txt",header=None,sep="    ",names=['Name','spo2'],index_col=False)

del spo2_db['Name']
spo2_db=spo2_db.dropna()

spo2_db= spo2_db.reset_index(drop=True)
print(spo2_db.shape)

main_db= pd.merge(resp_db,hr_db,left_index=True, right_index=True)
main_db= pd.merge(main_db,pulse_db,left_index=True,right_index=True)
main_db= pd.merge(main_db,spo2_db,left_index=True,right_index=True)
print(main_db)

nobs = 60
train, test = main_db[0:-nobs], main_db[-nobs:]

cnr = 0
cnhr = 0
cnpul = 0
cnsp = 0
cn = 0
model_fitted = pickle.load(open('model.pkl', 'rb'))
temp_train = train.copy(deep=True)
temp_db = main_db.copy(deep=True)
for i in rows[-60:]:
    cn = cn + 1
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
        'resp': float(test.iloc[[cnr]]['resp']),
        'hr': float(test.iloc[[cnhr]]['hr']),
        'pulse': float(test.iloc[[cnpul]]['pulse']),
        'spo2': float(test.iloc[[cnsp]]['spo2']),
    }

    temp_train = temp_train.append(x, ignore_index=True)
    temp_db = temp_db.append(x, ignore_index=True)

    forecast_input = temp_train.values[-10:]
    #print(forecast_input)
    print("-----------------------------------------")
    # Forecasting
    fc = model_fitted.forecast(y=forecast_input, steps=nobs)
    df_forecast = pd.DataFrame(fc, index=temp_db.index[-nobs:], columns=train.columns + '_pred')
    print(df_forecast.iloc[[-1]])


os.remove("tmp/temp.txt")




