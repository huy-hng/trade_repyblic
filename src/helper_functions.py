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
