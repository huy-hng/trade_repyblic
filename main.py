# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

#%%
import os
import datetime as dt
import json

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

# %%
start = dt.datetime(2000, 1, 1)
end = dt.datetime(2021, 2, 26)
df = web.DataReader('SPY', 'yahoo', start, end)
df.to_csv('prices/spy.csv')
# df

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

# %%
def calc_mav(arr, rolling_window=50):
	counter = 1
	vals = []
	mav = []

	for val in arr:
		vals.append(val)

		if counter < rolling_window:
			mav.append(sum(vals)/counter)
		else:
			mav.append(sum(vals[-rolling_window:])/rolling_window)

		counter += 1

	return mav

# %%
counter = 1
vals = []
man_mav = []
seven_day_lows = []
seven_day_highs = []

rolling_window = 50
for curr_price in df[OHLC].values:
	vals.append(curr_price)

	if counter < rolling_window:
		man_mav.append(sum(vals)/counter)
	else:
		man_mav.append(sum(vals[-rolling_window:])/rolling_window)

	seven_day_lows.append(min(vals[-7:]))
	seven_day_highs.append(max(vals[-7:]))

		
	counter += 1


# %%
def get_moving_average(OHLC, window):
	return df[OHLC].rolling(window, min_periods=0).mean().values



mav_long = get_moving_average(OHLC, 200)
mav_short = get_moving_average(OHLC, 20)



mavdf = pd.DataFrame({
	# 'mav_long': mav_long,
	'seven_day_lows': seven_day_lows,
	'seven_day_highs': seven_day_highs,
	'man_mav': man_mav,
	}, index=df.index)

# print(mavdf.resample('20D').ohlc())
# ap = mpf.make_addplot(mavdf.resample(RESAMPLE).mean(), type='line')



additional_plots = [
	mpf.make_addplot(mavdf, type='line'),
	mpf.make_addplot((df['atr']),panel=1,color='g',linestyle='dotted')
]

# mpf.plot(df[OHLC].resample(RESAMPLE).ohlc(),
mpf.plot(df,
        type='candle',
        style='charles',
        addplot=additional_plots)

# %%
# region buyer
class Buyer:
	def __init__(self, starting_money, ohlc):
		self.money = starting_money
		self.shares = 0
		self.transaction_cost = 1
		self.transactions = []
		self.ohlc = ohlc


	def buy(self, row, money_to_buy):
		price_per_share = row[self.ohlc]

		if self.money - (money_to_buy + self.transaction_cost) < 0:
			print(f'{row.name}, buy warning: not enough money')
			return

		self.shares += money_to_buy / price_per_share
		self.money -= money_to_buy + self.transaction_cost

		self.transactions.append({
			'date': row.name,
			'price': round(price_per_share, 2),
			'holding_shares': round(self.shares, 4),
			'money': round(self.money, 2),
			'share_transaction': round(money_to_buy / price_per_share, 4),
		})

	def sell(self, row, shares_to_sell):
		price_per_share = row[self.ohlc]

		if self.shares - shares_to_sell < 0:
			print(f'{row.name}, sell warning: not enough shares')
			return
		if shares_to_sell * price_per_share - self.transaction_cost < 0:
			print(f'{row.name}, sell warning: not enough money')
			return

		self.shares -= shares_to_sell
		self.money += shares_to_sell * price_per_share - self.transaction_cost

		self.transactions.append({
			'date': row.name,
			'price': round(price_per_share, 2),
			'holding_shares': round(self.shares, 4),
			'money': round(self.money, 2),
			'share_transaction': round(-shares_to_sell, 4),
		})

	def is_holding(self):
		return True if self.shares > 0 else False
# endregion

# %%
def print_endresult(starting_money, baseline_buyer, buyer, last_price):
	buyer_profit = round(buyer.money + buyer.shares * last_price, 2)
	baseline_profit = round(baseline_buyer.money + baseline_buyer.shares * last_price, 2)
	print(f'Money at the end: {buyer.money}, shares still left: {buyer.shares}, last_price: {round(last_price, 2)}')
	print(f'Money in total: {buyer_profit}')
	print(f'Transaction costs: {len(buyer.transactions)}')

	print(f'Baseline to beat: {baseline_profit}')
	print(f'Improvement compared to baseline: {round(((buyer_profit / baseline_profit) -1) * 100, 2)}%')
	print(f'Profit: {round(((buyer_profit / starting_money)-1) * 100, 2)}%')

# %%
# region 
buyer = Buyer(1000)

rolling_window = 200

counter = 1
vals = []
last_price = None
for index, row in df.iterrows():
	# print(dir(row))
	date: pd._libs.tslibs.timestamps.Timestamp = row.name

	curr_price = row[OHLC]

	vals.append(curr_price)

	if counter < rolling_window:
		current_mav = sum(vals)/counter
	else:
		current_mav = sum(vals[-rolling_window:])/rolling_window

	counter += 1
		
	seven_day_low = min(vals[-7:])
	seven_day_high = max(vals[-7:])


	if buyer.is_holding():

		if seven_day_low > current_mav:
			if last_price > curr_price:
				buyer.sell(curr_price, buyer.shares)
	else:
		if seven_day_high < current_mav:
			if last_price < curr_price:
				buyer.buy(curr_price, buyer.money * 0.8)
				pass

	last_price = curr_price

# print(f'Money at the end: {buyer.money}, shares still left: {buyer.shares}, last_price: {last_price}')
# total_money = buyer.money + buyer.shares * last_price
# print(f'Money in total: {total_money}')
# print(f'Transaction costs: {len(buyer.transactions)}')

trans = buyer.transactions
# endregion
# %%
# region 
OHLC = 'Close'

money = 10000
buyer = Buyer(money, OHLC)
baseline_buyer = Buyer(money, OHLC)

rolling_window = 200

counter = 1
vals = []
last_price = None
for index, row in df.iterrows():
	curr_price = row[OHLC]
	
	if not baseline_buyer.is_holding():
		baseline_buyer.buy(row, baseline_buyer.money - 1)

	vals.append(curr_price)

	if counter < rolling_window:
		current_mav = sum(vals)/counter
	else:
		current_mav = sum(vals[-rolling_window:])/rolling_window

	counter += 1
		
	seven_day_low = min(vals[-7:])
	seven_day_high = max(vals[-7:])


	if not buyer.is_holding():
		if curr_price < current_mav:
			if row['Low'] < seven_day_low:
				buyer.buy(row, buyer.money * 0.75)
	else:
		if curr_price < current_mav:
			if row['High'] > seven_day_high:
				buyer.sell(row, buyer.shares)

	last_price = curr_price

print_endresult(baseline_buyer, buyer, last_price)

trans = buyer.transactions
# endregion

# %%
# region
OHLC = 'Close'
starting_money = 10000
buyer = Buyer(starting_money, OHLC)
baseline_buyer = Buyer(starting_money, OHLC)

rolling_window = 200

counter = 1
vals = []
last_price = None
for index, row in df.iterrows():
	curr_price = row[OHLC]
	
	if not baseline_buyer.is_holding():
		baseline_buyer.buy(row, baseline_buyer.money - 1)


	vals.append(curr_price)

	x_days = 5
	x_day_low = min(vals[-x_days:])
	x_day_high = max(vals[-x_days:])

	if not buyer.is_holding():
		if row['Low'] < x_day_low and buyer.money > 1:
			buyer.buy(row, buyer.money - 1)
	else:
		if row['High'] > x_day_high and buyer.shares > 0:
			buyer.sell(row, buyer.shares)
	
	# print(f'curr_price: {round(curr_price, 2)}')
	# print(f'x_day_low: {round(x_day_low, 2)}')
	# print(f'Low: {round(row["Low"], 2)}')
	# print(f'x_day_high: {round(x_day_high, 2)}')
	# print(f'High: {round(row["High"], 2)}')
	# print(f'shares: {round(buyer.shares, 2)}')
	# print()

	last_price = curr_price
	counter += 1

print_endresult(starting_money, baseline_buyer, buyer, last_price)

trans = buyer.transactions
# endregion