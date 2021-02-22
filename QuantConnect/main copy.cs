namespace QuantConnect.Algorithm.CSharp {
	public class MuscularAsparagusDolphin : QCAlgorithm {
		private OrderTicket stopBuyMarketTicket = null;
		private OrderTicket stopSellMarketTicket = null;
		private decimal lastPrice = 999;
		private decimal highestPrice = 0;
		private decimal lowestPrice = 999;
		private int riseCounter = 0;
		private int buyAmount = 100;
		private string stock = "AYRO";

		public override void Initialize() {
			SetStartDate(2020, 11, 1);  //Set Start Date
			SetEndDate(2021, 2, 15);
			SetCash(100000);             //Set Strategy Cash

			AddEquity(stock, Resolution.Hour);
		}

		/// OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
		/// Slice object keyed by symbol containing the stock data
		public override void OnData(Slice data) {
			Plot("Price", "Close Price", Securities[stock].Close);
			Plot("Cash", "Money", Portfolio.Cash);

			CheckBigPriceJump();
			if (!Portfolio.Invested) {
				if (stopBuyMarketTicket == null) {
					BuyLogic();
				} else {
					TrailingStopBuy();
					Plot("Price", "lowestPrice", lowestPrice * 1.2m);
				}

			} else {
				// Debug("highest price " + highestPrice * 0.9m);
				if (stopSellMarketTicket == null) {
					stopSellMarketTicket = StopMarketOrder(stock, -Portfolio[stock].Quantity, highestPrice * 0.9m, "sell");
				} else {
					MoveTrailingStop();
					Plot("Price", "highestPrice", highestPrice * 0.9m);
				}
			}

			lastPrice = Securities[stock].Close;
		}


		public override void OnOrderEvent(OrderEvent orderEvent) {
			var order = Transactions.GetOrderById(orderEvent.OrderId);
			if (orderEvent.Status == OrderStatus.Filled) {
				Console.WriteLine("type {0}: event {1}", order.Type, orderEvent);

				if (order.Tag == "sell") {
					Debug("stocks have been sold.");
					lowestPrice = Securities[stock].Close;
					stopSellMarketTicket = null;
				}

				if (order.Tag == "buy") {
					Debug("Buying stocks");
					highestPrice = Securities[stock].Close;
					stopBuyMarketTicket = null;
				}
			}
		}


		public void MoveTrailingStop() {
			decimal currPrice = Securities[stock].Close;
			if (currPrice > highestPrice) {
				highestPrice = currPrice;

				stopSellMarketTicket.Update(new UpdateOrderFields() {
					StopPrice = highestPrice * 0.9m,
					Quantity = -Portfolio[stock].Quantity
				});
			}

		}

		public void TrailingStopBuy() {
			decimal currPrice = Securities[stock].Close;
			if (currPrice < lowestPrice) {
				lowestPrice = currPrice;

				// int amountToBuy = (int)(Portfolio.Cash / 2) / Portfolio[stock].Quantity;
				int amountToBuy = (int)(Portfolio.Cash / Securities[stock].Close) - 1;

				stopBuyMarketTicket.Update(new UpdateOrderFields() {
					StopPrice = lowestPrice * 1.1m,
					Quantity = amountToBuy
				});
			}
		}


		public void CheckBigPriceJump() {
			double increase = (double)(Securities[stock].Close / lastPrice);
			double percentageIncrease = Math.Round((increase - 1) * 100, 1);
			if (increase > 1.10d) {
				Debug("increase " + percentageIncrease + "%");
				Plot("Percent", "Percent rise", percentageIncrease);
				riseCounter++;
			}
		}


		public void BuyLogic() {
			if (riseCounter > 1) {
				// float cashToSpend = (float) Portfolio.Cash * (1 / (float)riseCounter);
				// int amountToBuy = (int)(cashToSpend / (float)Securities[stock].Close);
				int amountToBuy = (int)(Portfolio.Cash / Securities[stock].Close) - 1;
				stopBuyMarketTicket = StopMarketOrder(stock, amountToBuy, lowestPrice * 1.1m, "buy");
			}
		}
	}
}