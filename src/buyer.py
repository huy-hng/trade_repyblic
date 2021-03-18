import math

class Buyer:
	def __init__(self, starting_money, ohlc):
		self.money = starting_money
		self.shares = 0
		self.transaction_cost = 1
		self.transactions = []
		self.ohlc = ohlc
		self.data = df.copy()
		# self.data['shares'] = 0
		# self.data['money'] = 0
		# self.data['equity'] = 0


	def buy(self, row, money_to_buy):
		price_per_share = row[self.ohlc]

		if self.money - (money_to_buy + self.transaction_cost) < 0:
			print(f'{row.name}, buy warning: not enough money')
			return

		self.shares += money_to_buy / price_per_share
		self.money -= money_to_buy + self.transaction_cost

		self.data.loc[row.name, 'shares'] = self.shares
		self.data.loc[row.name, 'money'] = self.money
		
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

		self.data.loc[row.name, 'shares'] = self.shares
		self.data.loc[row.name, 'money'] = self.money

		self.transactions.append({
			'date': row.name,
			'price': round(price_per_share, 2),
			'holding_shares': round(self.shares, 4),
			'money': round(self.money, 2),
			'share_transaction': round(-shares_to_sell, 4),
		})

	def equity(self):
		# self.money + self.shares * shareprice
		last_money = None
		last_shares = None
		for i, row in self.data.iterrows():

			if row['money']	!= last_money and not math.isnan(row['money']):
				last_money = row['money']
			if math.isnan(row['money']):
				self.data.loc[i, 'money'] = last_money

			if row['shares']	!= last_shares and not math.isnan(row['shares']):
				last_shares = row['shares']
			if math.isnan(row['shares']):
				self.data.loc[i, 'shares'] = last_shares

		self.data['equity'] = self.data['shares'] * self.data[self.ohlc] + \
													self.data['money']
		self.data.dropna()



	def is_holding(self):
		return True if self.shares > 0 else False
