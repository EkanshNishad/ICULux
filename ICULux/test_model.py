import pickle
import pandas as pd
import numpy as np

forecast_input = temp_train.values[-10:]
forecast_input

model = pickle.load(open('model.pkl', 'rb'))
print("forcasting")
fc = model.forecast(y=forecast_input, steps=nobs)
df_forecast = pd.DataFrame(fc, index=temp_db.index[-nobs:], columns=train.columns + '_pred')

print(df_forecast)