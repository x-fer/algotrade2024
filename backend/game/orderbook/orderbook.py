from collections import deque
import pandas as pd
from xheap import XHeap
from functools import reduce
from .trade import Trade
from db import Order, OrderSide, OrderStatus, OrderType


class OrderBook():
    def __init__(self):
        self._limit_inf = int(1e18)
        self.buy_side = XHeap(
            key=lambda x: (-x.price, x.timestamp, x.order_id))
        self.sell_side = XHeap(key=lambda x: (
            x.price, x.timestamp, x.order_id))

        self.expire_heap = XHeap(key=lambda x: (
            x.expiration_tick, x.timestamp, x.order_id))

        self.map_to_heaps = {}
        self.queue = deque()

        self.callbacks = {
            'check_add': [],
            'on_add_fail': [],
            'on_order_update': [],
            'on_cancel': [],
            'on_begin_match': [],
            'check_trade': [],
            'on_trade': [],
            'on_end_match': [],
            'on_complete': [],
        }
        self.prev_price = None

    def register_callback(self, callback_type, callback):
        """Register a callback function for a specific type."""
        if not callback_type in self.callbacks:
            raise ValueError("Invalid callback type")
        if not callable(callback):
            raise ValueError("Callback is not callable")
        self.callbacks[callback_type].append(callback)

    def _invoke_callbacks(self, callback_type, *args, **kwargs):
        """Invoke callbacks of a specific type and collect their return values."""
        return_values = []
        if callback_type in self.callbacks:
            for callback in self.callbacks[callback_type]:
                return_value = callback(*args, **kwargs)
                return_values.append(return_value)
        return return_values

    def add_order(self, order: Order):
        if all(self._invoke_callbacks('check_add', order)):
            order.status = OrderStatus.IN_QUEUE
            self.queue.append(order)
            self._invoke_callbacks('on_order_update', order)
        else:
            order.status = OrderStatus.REJECTED
            self._invoke_callbacks('on_order_update', order)
            self._invoke_callbacks('on_add_fail', order)

    def cancel_all(self):
        for order_id in list(self.map_to_heaps.keys()):
            self.cancel_order(order_id)

    def cancel_order(self, order_id: int):
        if order_id not in self.map_to_heaps:
            raise ValueError(f"Order with id {order_id} not found")
        order = self.map_to_heaps[order_id]
        order.status = OrderStatus.CANCELLED
        self._invoke_callbacks('on_cancel', order)
        self._invoke_callbacks('on_order_update', order)
        self._remove_order(order_id)

    def _remove_order(self, order_id: int):
        order = self.map_to_heaps[order_id]

        self.expire_heap.remove(order)

        if order.order_side == OrderSide.BUY:
            self.buy_side.remove(order)
        else:
            self.sell_side.remove(order)

        del self.map_to_heaps[order_id]

    def _min_expire_time(self):
        if len(self.expire_heap) == 0:
            return None
        return self.expire_heap.peek()

    def match(self, timestamp: pd.Timestamp):
        self._invoke_callbacks('on_begin_match')
        self._remove_expired(timestamp)
        self.match_trades = []
        while len(self.queue) > 0:
            order = self.queue.popleft()
            order.status = OrderStatus.ACTIVE
            self._invoke_callbacks('on_order_update', order)
            self._add_order(order)
            self._match(timestamp)
        self._invoke_callbacks('on_end_match', self.match_trades)

    def _remove_expired(self, timestamp: pd.Timestamp):
        while self._min_expire_time() is not None and self._min_expire_time().expiration_tick < timestamp:
            order = self.expire_heap.peek()
            order.status = OrderStatus.EXPIRED
            self._invoke_callbacks('on_order_update', order)
            self._invoke_callbacks('on_cancel', order)
            self._remove_order(order.order_id)

    def _add_order(self, order: Order):
        if order.order_id in self.map_to_heaps:
            raise ValueError(f"Order with id {order.order_id} already exists")

        if order.expiration_tick < order.timestamp:
            raise ValueError(
                f"Order with id {order.order_id} has expiration earlier than timestamp")

        if order.size <= 0:
            raise ValueError(f"Order with id {order.order_id} has size <= 0")

        order.filled_money = 0
        order.filled_size = 0

        order.status = OrderStatus.ACTIVE

        if order.order_side == OrderSide.BUY:
            self.buy_side.push(order)
        else:
            self.sell_side.push(order)

        self.expire_heap.push(order)
        self.map_to_heaps[order.order_id] = order
        self._invoke_callbacks('on_order_update', order)

    def _match(self, timestamp: pd.Timestamp):
        while self._match_condition():
            buy_order = self.buy_side.peek()
            sell_order = self.sell_side.peek()
            self._match_one(buy_order, sell_order, timestamp)

    def _match_condition(self):
        if len(self.sell_side) == 0 or len(self.buy_side) == 0:
            return False
        return self.buy_side.peek().price >= self.sell_side.peek().price

    def _match_one(self, buy_order: Order, sell_order: Order, timestamp: pd.Timestamp):
        trade_price = self._get_trade_price(buy_order, sell_order)
        trade_size = self._get_trade_size(buy_order, sell_order)
        filled_money = trade_price * trade_size

        trade_before = Trade(buy_order, sell_order, timestamp,
                             filled_money, trade_size, trade_price)

        status = self._invoke_callbacks('check_trade', trade_before)

        status_reduced = reduce(
            lambda x, y: {i: x[i] and y[i] for i in x},
            status, {'can_buy': True, 'can_sell': True})

        if status_reduced['can_buy'] and status_reduced['can_sell']:
            self.prev_price = trade_price

            buy_order.filled_size += trade_size
            sell_order.filled_size += trade_size

            buy_order.filled_money += filled_money
            sell_order.filled_money += filled_money
            
            self._invoke_callbacks('on_order_update', buy_order)
            self._invoke_callbacks('on_order_update', sell_order)

            self._remove_if_filled(buy_order.order_id)
            self._remove_if_filled(sell_order.order_id)

            trade = Trade(buy_order, sell_order, timestamp,
                          filled_money, trade_size, trade_price)
            self._invoke_callbacks('on_trade', trade)
            self.match_trades.append(trade)
        if not status_reduced['can_buy']:
            self.cancel_order(buy_order.order_id)
        if not status_reduced['can_sell']:
            self.cancel_order(sell_order.order_id)

    def _get_trade_price(self, buy_order: Order, sell_order: Order):
        first_order = buy_order if buy_order.timestamp < sell_order.timestamp else sell_order
        second_order = sell_order if buy_order.timestamp < sell_order.timestamp else buy_order

        if first_order.order_type != OrderType.MARKET:
            return first_order.price
        elif second_order.order_type != OrderType.MARKET:
            return second_order.price
        return self.prev_price

    def _get_trade_size(self, buy_order: Order, sell_order: Order):
        return min(buy_order.size - buy_order.filled_size,
                   sell_order.size - sell_order.filled_size)

    def _remove_if_filled(self, order_id: int):
        order = self.map_to_heaps[order_id]
        if order.filled_size == order.size:
            order.status = OrderStatus.COMPLETED
            self._invoke_callbacks('on_order_update', order)
            self._invoke_callbacks('on_complete', order)
            self._remove_order(order_id)
