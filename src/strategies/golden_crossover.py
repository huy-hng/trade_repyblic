def golden_cross():
	OHLC = 'Close'

	money = 10000
	buyer = Buyer(money, OHLC)
	baseline_buyer = Buyer(money, OHLC)

	mav_window_long = 200
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
