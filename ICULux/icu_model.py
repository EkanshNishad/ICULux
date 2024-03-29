# -*- coding: utf-8 -*-
"""icu_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Uf_UnRm5dZQ206bxQV9el6CHrOGwXlbi
"""

# Commented out IPython magic to ensure Python compatibility.
import io
import os
import string
import pandas as pd 
import numpy as np 
import datetime
from datetime import time
from datetime import date
import matplotlib.pyplot as plt 
# %matplotlib inline
from datetime import datetime

import requests
from pandas import Series
from logging import Logger
from pandas._typing import Level
from pyspark.sql.functions import col
from pyspark.shell import spark
from pyspark.sql import SQLContext, SparkSession
from pyspark.sql.types import *
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql import HiveContext, window
import pyspark.sql.functions as sqf
from pyspark.streaming import StreamingContext
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.eval_measures import rmse, aic


def download_txt(example_txt, name):
    filename = name + ".txt"
    r = requests.get(example_txt)
    with open(filename, 'wb') as f:
        f.write(r.content)

# In this block all the files of a patient is combined in one. The main takeaway is resp.txt which contains the mean values of RESP every 1 minute window.

spark = SparkSession.builder.master('local[*]').appName('ICULux').config("spark.files.overwrite", "true")\
    .config("spark.worker.cleanup.enabled", "true").getOrCreate()
sc = spark.sparkContext
ssc = StreamingContext(sc, 1)
conf = SparkConf().setMaster("local[2]").setAppName("NetworkWordCount")

url = "https://physionet.org/files/mimicdb/1.0.0/252/RECORDS"
sc.addFile(url)

with open(SparkFiles.get("RECORDS"), 'r') as f:
    fileDirectory = f.readlines()

del fileDirectory[0]
del fileDirectory[0]

schema = StructType([
    StructField("Variable", StringType(), True),
    StructField("Val1", FloatType(), True),
    StructField("Val2", FloatType(), True),
    StructField("Val3", FloatType(), True)])

for fileName in fileDirectory:
    fileName= fileName[:-1]+'.txt'
    print(fileName)
    spark = SparkSession.builder.master('local[*]').appName('ICULux').config("spark.files.overwrite", "true")\
    .config("spark.worker.cleanup.enabled", "true").getOrCreate()
    sc = spark.sparkContext
    ssc = StreamingContext(sc, 1)
    conf = SparkConf().setMaster("local[2]").setAppName("NetworkWordCount")
    url = "https://physionet.org/files/mimicdb/1.0.0/252/"+fileName
    sc.addFile(url)

    with open(SparkFiles.get(fileName),'r') as infile:
        lines = infile.readlines()
    lines = [line.replace(' ','') for line in lines]
    with open('output_file.txt', 'w') as outfile:
        outfile.writelines(lines)

    readfrmfile = spark.read.csv(
    "./output_file.txt", header="false", schema=schema, sep='\\t')
    readfrmfile = readfrmfile.filter((col('Variable').startswith('[') == False) & (
    col('Variable') != "INOP") & (col('Variable') != "ALARM"))

    spark.conf.set("spark.sql.execution.arrow.enabled", "false")
    readfrmfile = readfrmfile.toPandas()

    # mention the parameter to separate
    resp= readfrmfile[readfrmfile['Variable']=="RESP"]
    del resp['Val2']
    del resp['Val3']

    hr= readfrmfile[readfrmfile['Variable']=="HR"]
    del hr['Val2']
    del hr['Val3']
    
    pulse= readfrmfile[readfrmfile['Variable']=="PULSE"]
    del pulse['Val2']
    del pulse['Val3']
    
    spo2= readfrmfile[readfrmfile['Variable']=="SpO2"]
    del spo2['Val2']
    del spo2['Val3']

    # partitioning dataframe, window size: approx 1 minute
    resp_split = np.array_split(resp, 10)
    hr_split = np.array_split(hr, 10)
    pulse_split = np.array_split(pulse, 10)
    spo2_split = np.array_split(spo2, 10)

    #creating file for RESP(resp.txt)
    file_object = open('./resp.txt', 'a')
    for i in resp_split:
        temp=i.mean(axis=0,skipna= True)
        file_object.write(str(temp)+'\n')
    file_object.close()

    #creating file for HR(hr.txt)
    file_object = open('./hr.txt', 'a')
    for i in hr_split:
        temp=i.mean(axis=0,skipna= True)
        file_object.write(str(temp)+'\n')
    file_object.close()

    #creating file for PULSE(pulse.txt)
    file_object = open('./pulse.txt', 'a')
    for i in pulse_split:
        temp=i.mean(axis=0,skipna= True)
        file_object.write(str(temp)+'\n')
    file_object.close()

    #creating file for SpO2(spo2.txt)
    file_object = open('./spo2.txt', 'a')
    for i in spo2_split:
        temp=i.mean(axis=0,skipna= True)
        file_object.write(str(temp)+'\n')
    file_object.close()

resp_db= pd.read_csv("./resp.txt",header=None,sep="    ",names=['Name','resp'],index_col=False)

del resp_db['Name']
resp_db=resp_db.dropna()

resp_db= resp_db.reset_index(drop=True)
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

from statsmodels.tsa.stattools import grangercausalitytests
maxlag=12
test = 'ssr_chi2test'
def grangers_causation_matrix(data, variables, test='ssr_chi2test', verbose=False):    
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    for c in df.columns:
        for r in df.index:
            test_result = grangercausalitytests(data[[r, c]], maxlag=maxlag, verbose=False)
            p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
            if verbose: print(f'Y = {r}, X = {c}, P Values = {p_values}')
            min_p_value = np.min(p_values)
            df.loc[r, c] = min_p_value
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    return df

grangers_causation_matrix(main_db, variables = main_db.columns)

from statsmodels.tsa.vector_ar.vecm import coint_johansen

def cointegration_test(df, alpha=0.05): 
    out = coint_johansen(df,-1,5)
    d = {'0.90':0, '0.95':1, '0.99':2}
    traces = out.lr1
    cvts = out.cvt[:, d[str(1-alpha)]]
    def adjust(val, length= 6): return str(val).ljust(length)

    # Summary
    print('Name   ::  Test Stat > C(95%)    =>   Signif  \n', '--'*20)
    for col, trace, cvt in zip(df.columns, traces, cvts):
        print(adjust(col), ':: ', adjust(round(trace,2), 9), ">", adjust(cvt, 8), ' =>  ' , trace > cvt)

cointegration_test(main_db)

nobs = 30
train, test = main_db[0:-nobs], main_db[-nobs:]

print(train.shape)
print(test.shape)

def adfuller_test(series, signif=0.05, name='', verbose=False):
    r = adfuller(series, autolag='AIC')
    output = {'test_statistic':round(r[0], 4), 'pvalue':round(r[1], 4), 'n_lags':round(r[2], 4), 'n_obs':r[3]}
    p_value = output['pvalue'] 
    def adjust(val, length= 6): return str(val).ljust(length)

    # Print Summary
    print(f'    Augmented Dickey-Fuller Test on "{name}"', "\n   ", '-'*47)
    print(f' Null Hypothesis: Data has unit root. Non-Stationary.')
    print(f' Significance Level    = {signif}')
    print(f' Test Statistic        = {output["test_statistic"]}')
    print(f' No. Lags Chosen       = {output["n_lags"]}')

    for key,val in r[4].items():
        print(f' Critical value {adjust(key)} = {round(val, 3)}')

    if p_value <= signif:
        print(f" => P-Value = {p_value}. Rejecting Null Hypothesis.")
        print(f" => Series is Stationary.")
    else:
        print(f" => P-Value = {p_value}. Weak evidence to reject the Null Hypothesis.")
        print(f" => Series is Non-Stationary.")

# ADF Test on each column
for name, column in train.iteritems():
    adfuller_test(column, name=column.name)
    print('\n')

model = VAR(train)
for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
    result = model.fit(i)
    print('Lag Order =', i)
    print('AIC : ', result.aic)
    print('BIC : ', result.bic)
    print('FPE : ', result.fpe)
    print('HQIC: ', result.hqic, '\n')

x = model.select_order(maxlags=12)
x.summary()

model_fitted = model.fit(10)
model_fitted.summary()

# Input data for forecasting
forecast_input = train.values[-10:]
forecast_input

# Forecasting
fc = model_fitted.forecast(y=forecast_input, steps=nobs)
df_forecast = pd.DataFrame(fc, index=main_db.index[-nobs:], columns=train.columns + '_pred')
    
print(df_forecast)

fig, axes = plt.subplots(nrows=int(len(main_db.columns)/2), ncols=2, dpi=150, figsize=(10,10))
for i, (col,ax) in enumerate(zip(main_db.columns, axes.flatten())):
    df_forecast[col+'_pred'].plot(legend=True, ax=ax).autoscale(axis='x',tight=True)
    test[col][-nobs:].plot(legend=True, ax=ax);
    ax.set_title(col + ": Forecast vs Actuals")
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.spines["top"].set_alpha(0)
    ax.tick_params(labelsize=6)

plt.tight_layout();

temp_train= train.copy(deep=True)
temp_db= main_db.copy(deep=True)

for idx, row in test.iterrows():
    x= {
        'resp': row['resp'],
        'hr': row['hr'],
        'pulse': row['pulse'],
        'spo2': row['spo2'],
        }
    
    temp_train= temp_train.append(x,ignore_index= True)
    temp_db= temp_db.append(x,ignore_index= True)

    # Train the model
    #model = VAR(temp_train)
    #model_fitted = model.fit(10)

    # Input data for forecasting
    forecast_input = temp_train.values[-10:]
    forecast_input

    # Forecasting
    fc = model_fitted.forecast(y=forecast_input, steps=nobs)
    df_forecast = pd.DataFrame(fc, index=temp_db.index[-nobs:], columns=train.columns + '_pred')
    
    print(df_forecast)

import pickle
pickle.dump(model, open('model.pkl','wb'))

