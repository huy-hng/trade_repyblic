import os
import datetime as dt

import settings

import matplotlib.pyplot as plt
from matplotlib import style

import pandas as pd
import pandas_datareader as web


 
def get_new_data():
	start = dt.datetime(2000, 1, 1)
	end = dt.datetime(2021, 2, 13)

	df = web.DataReader("AYRO", "av-intraday", start=start, end=end,
										api_key=os.getenv('ALPHAVANTAGE_API_KEY'))

	df.to_csv('ayro_intraday.csv')


def create_df():
	pd.set_option('display.max_columns', 500)
	df = pd.read_csv('ayro_intraday.csv', parse_dates=True, index_col=0)
	return df


def plot(df):
	style.use('ggplot')
	ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
	ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)

	ax1.plot(df.index, df['close'])
	ax2.plot(df.index, df['volume'])

	plt.show()

df = create_df()
print(df.tail())
plot(df)