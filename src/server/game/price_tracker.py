from .orderbook import OrderBook, Trade

class PriceTracker:
    def __init__(self, orderbook: OrderBook):
        self.last_high = 0
        self.last_low = 0
        self.last_market = 0

        self.high = None
        self.low = None
        self.market = None
        orderbook.register_callback('on_end_match', self._calculate_low_high)

    def _calculate_low_high(self, trades: list[Trade]):
        self.high = None
        self.low = None
        self.market = None

        money_sum = 0
        money_size = 0
        
        for trade in trades:
            price = trade.filled_price
            money_sum += trade.filled_money
            money_size += trade.filled_size
            
            if self.high is None:
                self.high = price
            if self.high < price:
                self.high = price

            if self.low is None:
                self.low = price
            if self.low > price:
                self.low = price
        
        if money_size > 0:
            self.market = money_sum / money_size
        
        self._save_last()
    
    def _save_last(self):
        if self.market is not None:
            self.last_market = self.market
            self.last_high = self.high
            self.last_low = self.low
    
    def get_low(self):
        return self.low if self.low is not None else self.last_low
    
    def get_high(self):
        return self.high if self.high is not None else self.last_high
    
    def get_market(self):
        return self.market if self.market is not None else self.last_market
