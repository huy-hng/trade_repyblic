
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
