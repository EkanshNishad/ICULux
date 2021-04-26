import requests

example_txt = "https://physionet.org/files/mimicdb/1.0.0/252/RECORDS"

r = requests.get(example_txt)
with open('file.txt', 'wb') as f:
    f.write(r.content)