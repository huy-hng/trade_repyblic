# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

#%%
import os
import datetime as dt
import json
import math

import settings

import matplotlib.pyplot as plt
from matplotlib import style
import mplfinance as mpf

import pandas as pd
import pandas_datareader as web

from strategies.golden_crossover import golden_cross
from strategies.mav_channel import mav_channel

get_ipython().run_line_magic('matplotlib', 'widget')
# %matplotlib widget

OHLC = 'Close'
RESAMPLE = '5D'

# delta = dt.timedelta(days=720)
# end = dt.datetime(2015, 1, 1)
# end = dt.datetime.now()
# df = web.DataReader('SPY', 'yahoo', end-delta, end)
# df.to_csv('prices/spy.csv')

start = dt.datetime(2000, 1, 1)
end = dt.datetime.now()
df = web.DataReader('SPY', 'yahoo', start, end)
df.to_csv('prices/spy.csv')

# for row in df.iterrows():
# 	print(type(row[0]))
# 	break

# %% ###########################################################################
vals = []
man_mav = []
seven_day_lows = []
seven_day_highs = []

mav_window_long = 50
for curr_price in df[OHLC].values:
	vals.append(curr_price)

	if len(vals) < mav_window_long:
		man_mav.append(sum(vals)/len(vals))
	else:
		man_mav.append(sum(vals[-mav_window_long:])/mav_window_long)

	seven_day_lows.append(min(vals[-7:]))
	seven_day_highs.append(max(vals[-7:]))

# %% ###########################################################################
buyer_gc = golden_cross()
buyer_mac = mav_channel()

# %%
close = df['Close'].values
high = df['High'].values
low = df['Low'].values

zipped = zip(close, high, low)
prev_day = None
tr = []
for i, day in enumerate(zipped):
	range_ = day[1] - day[2]
	
	down = 0
	up = 0
	if prev_day is not None:
		down = abs(prev_day[0] - day[2])
		up = abs(prev_day[0] - day[1])

	tr.append(max(range_, up, down))

	prev_day = day


df['atr'] = calc_mav(tr, 20)

mav_long = get_moving_average(OHLC, 200)
mav_short = get_moving_average(OHLC, 20)

crosses = pd.DataFrame(index=df.index, columns=['val', 'date'])
count = 0
prev_up = None
for day in zip(mav_long, mav_short, df.index):
	curr_up = 'long' if day[0] > day[1] else 'short'
	if curr_up != prev_up:
		crosses.loc[day[2], 'val'] = day[0] * 0.9
		crosses.loc[day[2], 'date'] = day[2]
	prev_up = curr_up
	# if count == 10:
	# 	break
	# count += 1

mavdf = pd.DataFrame({
	'mav_long': mav_long,
	'mav_short': mav_short,
	# 'seven_day_lows': seven_day_lows,
	# 'seven_day_highs': seven_day_highs,
	# 'man_mav': man_mav,
	}, index=df.index)

# print(mavdf.resample('20D').ohlc())
# ap = mpf.make_addplot(mavdf.resample(RESAMPLE).mean(), type='line')

last_days = 0
additional_plots = [
	mpf.make_addplot(mavdf, type='line'),
	mpf.make_addplot((df['atr']), panel=1,color='g',linestyle='dotted'),
	# mpf.make_addplot(crosses, type='scatter'),
	# mpf.make_addplot(crosses, type='scatter', marker='^'),
	# mpf.make_addplot(buyer_gc.data.iloc[last_days:, 'equity']),
	# mpf.make_addplot(buyer_mac.data.iloc[last_days:, 'equity'])
	mpf.make_addplot(buyer_gc.data['equity'], panel=2, color='blue'),
	mpf.make_addplot(buyer_mac.data['equity'], panel=2, color='red')
]

# mpf.plot(df[OHLC].resample(RESAMPLE).ohlc(),
mpf.plot(df,
        type='candle',
        style='charles',
        addplot=additional_plots)

