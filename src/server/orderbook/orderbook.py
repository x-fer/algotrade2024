from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pprint import pprint
from collections import deque
import random
import pandas as pd
from xheap import XHeap


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1


class TradeStatus(Enum):
    PENDING = 0
    ACTIVE = 1
    COMPLETED = 2
    PARTIALLY_COMPLETED = 3
    EXPIRED_CANCELLED = 4


class OrderSide(Enum):
    BUY = 0
    SELL = 1


@dataclass
class Order:
    timestamp: pd.Timestamp
    expiration: pd.Timestamp
    order_id: int
    trader_id: int

    price: int
    size: int

    filled_money: int
    filled_size: int

    side: OrderSide
    type: OrderType
    status: TradeStatus = TradeStatus.PENDING

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp


@dataclass
class Trade:
    buy_order: Order
    sell_order: Order
    timestamp: pd.Timestamp

    filled_money: int
    filled_size: int
    filled_price: int


class OrderBook():
    def __init__(self, on_insert: callable = None, on_complete: callable = None):
        self.on_insert = on_insert if on_insert is not None else lambda x: None
        self.on_complete = on_complete if on_complete is not None else lambda x: None

        self._limit_inf = int(1e18)
        self.buy_side = XHeap(
            key=lambda x: (-x.price, x.timestamp, x.order_id))
        self.sell_side = XHeap(key=lambda x: (
            x.price, x.timestamp, x.order_id))

        self.expire_heap = XHeap(key=lambda x: (
            x.expiration, x.timestamp, x.order_id))

        self.map_to_heaps = {}

        self.prev_market_price = None
        self.queue = deque()

    def get_market_price(self):
        no_side = len(self.buy_side) == 0 or len(self.sell_side) == 0

        if no_side and self.prev_market_price is None:
            return None

        if no_side:
            return self.prev_market_price

        self.prev_market_price = (
            self.buy_side.peek().price + self.sell_side.peek().price) // 2

        return self.prev_market_price

    def add_order(self, order: Order):
        self.on_insert(order)
        self.queue.append(order)

    def _add_order(self, order: Order):
        if order.order_id in self.map_to_heaps:
            raise ValueError(f"Order with id {order.order_id} already exists")

        if order.expiration < order.timestamp:
            raise ValueError(
                f"Order with id {order.order_id} has expiration earlier than timestamp")

        if order.size <= 0:
            raise ValueError(f"Order with id {order.order_id} has size <= 0")

        order.filled_money = 0
        order.filled_size = 0

        order.status = TradeStatus.ACTIVE

        if order.side == OrderSide.BUY:
            self.buy_side.push(order)
        else:
            self.sell_side.push(order)

        self.expire_heap.push(order)
        self.map_to_heaps[order.order_id] = order

    def cancel_all(self, timestamp: pd.Timestamp):
        for order_id in list(self.map_to_heaps.keys()):
            self.cancel_order(order_id, timestamp)

    def cancel_order(self, order_id: int, timestamp: pd.Timestamp):
        if order_id not in self.map_to_heaps:
            raise ValueError(f"Order with id {order_id} not found")

        order = self.map_to_heaps[order_id]

        if order.status in [TradeStatus.EXPIRED_CANCELLED, TradeStatus.COMPLETED]:
            return

        order.status = TradeStatus.EXPIRED_CANCELLED

        if order.side == OrderSide.BUY:
            self.on_complete(Trade(order, None, timestamp,
                                   0, 0, None))
        else:
            self.on_complete(Trade(None, order, timestamp,
                                   0, 0, None))

        self._remove_order(order_id)

    def _remove_order(self, order_id: int):
        order = self.map_to_heaps[order_id]

        self.expire_heap.remove(order)

        if order.side == OrderSide.BUY:
            self.buy_side.remove(order)
        else:
            self.sell_side.remove(order)

        del self.map_to_heaps[order_id]

    def _max_buy(self):
        if len(self.buy_side) == 0:
            return None
        return self.buy_side.peek()

    def _min_sell(self):
        if len(self.sell_side) == 0:
            return None
        return self.sell_side.peek()

    def _min_expire_time(self):
        if len(self.expire_heap) == 0:
            return None
        return self.expire_heap.peek()

    def remove_if_filled(self, order_id: int):
        order = self.map_to_heaps[order_id]
        if order.filled_size == order.size:
            self._remove_order(order_id)

    def match(self, timestamp: pd.Timestamp):
        cnt = 0
        while len(self.queue) > 0:
            order = self.queue.popleft()
            self._add_order(order)
            cnt += self._match(timestamp)

        return cnt

    def _match(self, timestamp: pd.Timestamp):
        cnt = 0
        # kill expired orders
        while self._min_expire_time() is not None and self._min_expire_time().expiration < timestamp:
            order = self.expire_heap.peek()

            order.status = TradeStatus.EXPIRED_CANCELLED

            if order.side == OrderSide.BUY:
                self.on_complete(
                    Trade(order, None, timestamp, 0, 0, None))
            else:
                self.on_complete(
                    Trade(None, order, timestamp, 0, 0, None))

            self._remove_order(order.order_id)
            cnt += 1

        # match orders
        while self._max_buy() is not None and \
                self._min_sell() is not None and \
                self._max_buy().price >= self._min_sell().price:
            buy_order = self.buy_side.peek()
            sell_order = self.sell_side.peek()

            to_fill_size = min(buy_order.size - buy_order.filled_size,
                               sell_order.size - sell_order.filled_size)

            buy_order.filled_size += to_fill_size
            sell_order.filled_size += to_fill_size

            first_order = buy_order if buy_order.timestamp < sell_order.timestamp else sell_order
            second_order = sell_order if buy_order.timestamp < sell_order.timestamp else buy_order

            if first_order.type != OrderType.MARKET:
                price = first_order.price
            elif second_order.type != OrderType.MARKET:
                price = second_order.price
            else:
                price = self.get_market_price()

            buy_order.filled_money += to_fill_size * price
            sell_order.filled_money += to_fill_size * price

            if buy_order.filled_size == buy_order.size:
                buy_order.status = TradeStatus.COMPLETED
            else:
                buy_order.status = TradeStatus.PARTIALLY_COMPLETED

            if sell_order.filled_size == sell_order.size:
                sell_order.status = TradeStatus.COMPLETED
            else:
                sell_order.status = TradeStatus.PARTIALLY_COMPLETED

            status = self.on_complete(Trade(buy_order, sell_order, timestamp,
                                            to_fill_size * price, to_fill_size, price))

            if status["can_buy"] and status["can_sell"]:
                self.remove_if_filled(buy_order.order_id)
                self.remove_if_filled(sell_order.order_id)
                continue

            # undo trade

            buy_order.filled_size -= to_fill_size
            sell_order.filled_size -= to_fill_size

            buy_order.filled_money -= to_fill_size * price
            sell_order.filled_money -= to_fill_size * price

            if not status["can_buy"]:
                buy_order.status = TradeStatus.EXPIRED_CANCELLED
                self._remove_order(buy_order.order_id)
            else:
                self.remove_if_filled(buy_order.order_id)

            if not status["can_sell"]:
                sell_order.status = TradeStatus.EXPIRED_CANCELLED
                self._remove_order(sell_order.order_id)
            else:
                self.remove_if_filled(sell_order.order_id)

            cnt += 1

        return cnt
