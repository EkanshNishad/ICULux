from pyspark.sql.session import SparkSession
from pyspark.sql.types import *
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql import HiveContext
import pyspark.sql.functions as sqf
from hmmlearn import hmm
import numpy as np
def int_or_float(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


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

# finally, write lines in the file
with open("tmp/temp.txt", 'w') as f:
    f.writelines(lines)


schema = StructType([
    StructField("Name",StringType(),True),
    StructField("val1",StringType(),True),
    StructField("val2",StringType(),True),
    StructField("val3", StringType(), True)])


readfrmfile = spark.read.csv("tmp/temp.txt", header="false", schema=schema, sep='\\t')
readfrmfile = readfrmfile.filter(readfrmfile.Name == "HR")

df = readfrmfile.toPandas()
train_data, test_data = df[0:int(len(df)*0.5)], df[int(len(df)*0.5):]
training_data = train_data['val1'].values
training_data = np.array(training_data)
training_data = training_data.astype(int)
test_data = test_data['val1'].values
test_data = np.array(test_data)
test_data = test_data.astype(int)
model = hmm.GaussianHMM(n_components=3)
model.fit(training_data.reshape(-1,1))
#print(training_data.reshape(-1,1))
predictions = model.predict(test_data.reshape(-1,1))
print(predictions)