class MuscularRedGalago(QCAlgorithm):

	def Initialize(self):
		self.SetStartDate(2020, 8, 14)  # Set Start Date
		self.SetCash(100000)  # Set Strategy Cash
		self.AddEquity("GME", Resolution.Hour)
		
		self.stop_market_ticket: OrderTicket
		self.last_GME_price = 99999
		self.highest_GME_price = 0
		self.rise_counter = 0


	def OnData(self, data):
		'''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
				Arguments:
						data: Slice object keyed by symbol containing the stock data
		'''
		price = self.Securities['GME'].Close
		self.Plot('Data Chart', 'Close Price', price)


		if not self.Portfolio.Invested:
			increase = price / self.last_GME_price

			self.Debug('increase' + str(increase))

			if increase > 1.08:
				self.Plot('Percent', 'Risen', increase - 1)
				self.rise_counter += 1

			if self.rise_counter > 2:
				self.MarketOrder('GME', 50)
				self.highest_GME_price = price
				self.stop_market_ticket = self.StopMarketOrder('GME', -50, self.highest_GME_price * 0.9)
				self.rise_counter = 0

			else:
				self.Plot('Data Chart', 'Stop Price', self.highest_GME_price)

				if price > self.highest_GME_price:
					self.highest_GME_price = price
					self.stop_market_ticket = self.StopMarketOrder('GME', -50, self.highest_GME_price * 0.9)

		self.last_GME_price = price

	def OnOrderEvent(self, orderEvent):
			order = self.Transactions.GetOrderById(orderEvent.OrderId)
			if orderEvent.Status == OrderStatus.Filled: 
					self.Log("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))