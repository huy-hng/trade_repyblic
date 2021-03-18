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

# %% 
#region helper functions
def get_moving_average(OHLC, window):
	return df[OHLC].rolling(window, min_periods=0).mean().values

def calc_mav(arr, rolling_window=50):
	vals = []
	mav = []

	for val in arr:
		vals.append(val)

		if len(vals) < rolling_window:
			mav.append(sum(vals)/len(vals))
		else:
			mav.append(sum(vals[-rolling_window:])/rolling_window)

	return mav

def calc_current_mav(vals, window):
	if len(vals) < window:
		mav = sum(vals)/len(vals)
	else:
		mav = sum(vals[-window:])/window
	return mav

def print_endresult(starting_money, baseline_buyer, buyer, last_price):
	buyer_profit = round(buyer.money + buyer.shares * last_price, 2)
	baseline_profit = round(baseline_buyer.money + \
													baseline_buyer.shares * last_price, 2)
	print(f'Money at the end: {buyer.money},\
					shares still left: {buyer.shares},\
					last_price: {round(last_price, 2)}')
	print(f'Money in total: {buyer_profit}')
	print(f'Transaction costs: {len(buyer.transactions)}')

	print(f'Baseline to beat: {baseline_profit}')
	print(f'Improvement compared to baseline:\
					{round(((buyer_profit / baseline_profit) -1) * 100, 2)}%')
	print(f'Profit: {round(((buyer_profit / starting_money)-1) * 100, 2)}%')

#endregion


# %% ###########################################################################
def golden_cross():
	OHLC = 'Close'

	money = 10000
	buyer = Buyer(money, OHLC)
	baseline_buyer = Buyer(money, OHLC)

	mav_window_long = 200

	mav_window_short = 50


	prev_up = None
	vals = []
	for index, row in df.iterrows():
		curr_price = row[OHLC]
		
		if not baseline_buyer.is_holding():
			baseline_buyer.buy(row, baseline_buyer.money - 1)

		vals.append(curr_price)

		mav_long = calc_current_mav(vals, mav_window_long)
		mav_short = calc_current_mav(vals, mav_window_short)

		seven_day_low = min(vals[-7:])
		seven_day_high = max(vals[-7:])

		curr_up = 'long' if mav_long > mav_short else 'short'

		if not buyer.is_holding():
			if curr_up != prev_up and curr_up == 'short' and curr_price > mav_long:
				buyer.buy(row, buyer.money - 1)
		else:
			if curr_up != prev_up and curr_up == 'long':
				buyer.sell(row, buyer.shares)
		prev_up = curr_up

	print_endresult(money, baseline_buyer, buyer, calc_current_mav(vals, 30))


	trans = buyer.transactions
	buyer.equity()
	# mpf.plot(buyer.data,
	# 				type='candle',
	# 				style='charles',
	# 				addplot=mpf.make_addplot(buyer.data['equity'], type='line'))
	return buyer
# golden_cross()

# %% ###########################################################################
def mav_channel():
	OHLC = 'Close'

	money = 10000
	buyer = Buyer(money, OHLC)
	baseline_buyer = Buyer(money, OHLC)

	mav_window_long = 200
	mav_window_short = 20


	prev_up = None
	vals = []
	lows = []
	highs = []
	bars_below_mac = 0
	bars_above_mac = 0
	for index, row in df.iterrows():
		curr_price = row[OHLC]
		
		lows.append(row['Low'])
		highs.append(row['High'])
		vals.append(curr_price)

		if not baseline_buyer.is_holding():
			baseline_buyer.buy(row, baseline_buyer.money - 1)

		mav = calc_current_mav(vals, 200)
		mav_low = calc_current_mav(lows, 10)
		mav_high = calc_current_mav(highs, 10)
		if curr_price > mav_high:
			bars_above_mac += 1
			bars_below_mac = 0
		elif curr_price < mav_low:
			bars_below_mac += 1
			bars_above_mac = 0
		else:
			bars_above_mac = 0
			bars_below_mac = 0

		if not buyer.is_holding():
			if bars_above_mac >= 5 and curr_price > mav:
				buyer.buy(row, buyer.money - 1)
		else:
			if bars_below_mac >= 5:
				buyer.sell(row, buyer.shares)

	print_endresult(money, baseline_buyer, buyer, calc_current_mav(vals, 30))

	trans = buyer.transactions
	buyer.equity()
	return buyer







# %% ###########################################################################
################################################################################
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
################################################################################
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

