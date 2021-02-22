namespace QuantConnect.Algorithm.CSharp
{
    public class MuscularAsparagusDolphin : QCAlgorithm
    {
        private OrderTicket stopMarketTicket;
        private decimal lastGMEPrice = Decimal.MaxValue;
        private decimal highestGMEPrice = 0;
        private int riseCounter = 0;
        private int buyAmount = 100;
        private bool stop = false;

        public override void Initialize()
        {
            SetStartDate(2021, 1, 15);  //Set Start Date
            SetEndDate(2021, 2, 5);
            SetCash(100000);             //Set Strategy Cash

            AddEquity("GME", Resolution.Hour);
        }

        /// OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        /// Slice object keyed by symbol containing the stock data
        public override void OnData(Slice data)
        {
        	Plot("Data Chart", "Close Price", Securities["GME"].Close);
        	Plot("Cash", "Money", Portfolio.Cash);

            CheckBigPriceJump();
            BuyLogic();
        	if (Portfolio.Invested) {
                MoveTrailingStop();
        	} else {
                highestGMEPrice = Securities["GME"].Close;
            }

            Debug("highest price " + highestGMEPrice * 0.9m);
            Plot("Data Chart", "Stop Price", highestGMEPrice * 0.9m);
            // Plot("Data Chart", "Stop Price", stopMarketTicket.Get(OrderField.StopPrice));


        	lastGMEPrice = Securities["GME"].Close;
        }


		public override void OnOrderEvent(OrderEvent orderEvent) {
		    var order = Transactions.GetOrderById(orderEvent.OrderId);
		    if (orderEvent.Status == OrderStatus.Filled) {
                Console.WriteLine("{0}: {1}", order.Type, orderEvent);
            }
		}


        public void MoveTrailingStop() {
            if (Securities["GME"].Close > highestGMEPrice) {
                highestGMEPrice = Securities["GME"].Close;

                stopMarketTicket.Update(new UpdateOrderFields() { 
                    StopPrice = highestGMEPrice * 0.9m,
                    Quantity = -Portfolio["GME"].Quantity
                });
            }
        }


        public void CheckBigPriceJump() {
            double increase = (double) (Securities["GME"].Close / lastGMEPrice);
            double percentageIncrease = Math.Round((increase - 1) * 100, 1);
            if (increase > 1.10d ) {
                Debug("increase " + percentageIncrease + "%");
                Plot("Data Chart", "Percent rise", percentageIncrease);
                riseCounter++;
            }
        }


        public void BuyLogic() {
            if (riseCounter > 2) {
                float cashToSpend = (float) Portfolio.Cash * (1 / (float) riseCounter);
                int amountToBuy = (int) (cashToSpend / (float) Securities["GME"].Close);
                Debug("cashToSpend "+cashToSpend);
                Debug("amountToBuy "+amountToBuy);
                MarketOrder("GME", 10);
                // highestGMEPrice = Securities["GME"].Close;

                stopMarketTicket = StopMarketOrder("GME", -Portfolio["GME"].Quantity, highestGMEPrice * 0.9m);
            }
        }
    }
}