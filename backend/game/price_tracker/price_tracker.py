from typing import List
from game.orderbook import OrderBook
from model import Trade


class PriceTracker:
    def __init__(self, orderbook: OrderBook = None):
        self.last_high = 0
        self.last_low = 0
        self.last_open = 0
        self.last_close = 0
        self.last_average = 0
        self.volume = 0

        self.high = None
        self.low = None
        self.open = None
        self.close = None
        self.average = None

        if orderbook is not None:
            orderbook.register_callback(
                'on_end_match', self._calculate_low_high)

    def on_end_match(self, trades: List[Trade]):
        self._calculate_low_high(trades)

    def _calculate_low_high(self, trades: List[Trade]):
        self.high = None
        self.low = None
        self.open = None
        self.close = None
        self.average = None

        money_sum = 0
        money_size = 0

        if len(trades) != 0:
            self.open = trades[0].trade_price
            self.close = trades[-1].trade_price

        for trade in trades:
            price = trade.trade_price
            money_sum += trade.total_price
            money_size += trade.trade_size

            if self.high is None:
                self.high = price
            if self.high < price:
                self.high = price

            if self.low is None:
                self.low = price
            if self.low > price:
                self.low = price

        if money_size > 0:
            self.average = money_sum / money_size
        self.volume = money_size

        self._save_last()

    def _save_last(self):
        if self.average is not None:
            self.last_average = self.average
            self.last_high = self.high
            self.last_low = self.low
            self.last_open = self.open
            self.last_close = self.close

    def get_low(self):
        return self.low if self.low is not None else self.last_low

    def get_high(self):
        return self.high if self.high is not None else self.last_high

    def get_average(self):
        return self.average if self.average is not None else self.last_average

    def get_open(self):
        return self.open if self.open is not None else self.last_open

    def get_close(self):
        return self.close if self.close is not None else self.last_close

    def get_volume(self):
        return self.volume
