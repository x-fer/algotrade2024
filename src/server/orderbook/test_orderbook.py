from pprint import pprint
import unittest
from matplotlib import pyplot as plt
import pandas as pd
from orderbook import OrderBook, Order, OrderSide, OrderType, TradeStatus, Trade
import random


class TestOrderBook(unittest.TestCase):

    # def setUp(self):
    #     self.orders = []
    #     self.on_complete_calls = []

    # def on_complete_mock(self, trade: Trade):
    #     self.on_complete_calls.append(trade)

    # def test_add_order(self):
    #     ob = OrderBook(on_complete=self.on_complete_mock)

    #     # Create an order and add it to the order book
    #     t1 = pd.Timestamp('2021-01-01')
    #     expiration = t1 + pd.Timedelta(days=1)
    #     order = Order(t1, expiration, 1, 1, 200, 20, 0, 0,
    #                   OrderSide.BUY, OrderType.LIMIT, TradeStatus.PENDING)

    #     ob.add_order(order)

    #     # Verify the order is in the order book
    #     self.assertEqual(ob.buy_side.peek(), order)
    #     self.assertEqual(ob.expire_heap.peek(), order)
    #     self.assertIn(order.order_id, ob.map_to_heaps)

    # def test_cancel_order(self):
    #     ob = OrderBook(on_complete=self.on_complete_mock)

    #     # Create and add an order to the order book
    #     t1 = pd.Timestamp('2021-01-01')
    #     expiration = t1 + pd.Timedelta(days=1)
    #     order = Order(t1, expiration, 1, 1, 200, 20, 0, 0,
    #                   OrderSide.BUY, OrderType.LIMIT, TradeStatus.ACTIVE)
    #     ob.add_order(order)

    #     # Cancel the order
    #     ob.cancel_order(order.order_id, pd.Timestamp.now())

    #     # Verify the order is canceled
    #     self.assertEqual(order.status, TradeStatus.EXPIRED_CANCELLED)
    #     self.assertNotIn(order.order_id, ob.map_to_heaps)

    # def test_match_orders(self):
    #     ob = OrderBook(on_complete=self.on_complete_mock)

    #     # Create and add buy and sell orders to the order book
    #     t1 = pd.Timestamp('2021-01-01')
    #     expiration = t1 + pd.Timedelta(days=1)
    #     buy_order = Order(t1, expiration, 1, 1, 200, 20, 0, 0,
    #                       OrderSide.BUY, OrderType.LIMIT, TradeStatus.ACTIVE)
    #     sell_order = Order(t1, expiration, 2, 2, 100, 10, 0, 0,
    #                        OrderSide.SELL, OrderType.LIMIT, TradeStatus.ACTIVE)

    #     ob.add_order(buy_order)
    #     ob.add_order(sell_order)

    #     # Match the buy and sell orders
    #     ob.match(pd.Timestamp('2021-01-02'))

    #     # Verify the on_complete callback is called with the correct parameters
    #     self.assertEqual(len(self.on_complete_calls), 1)
    #     trade = self.on_complete_calls[0]

    #     self.assertEqual(trade.buy_order, buy_order)
    #     self.assertEqual(trade.sell_order, sell_order)
    #     self.assertIsInstance(trade.timestamp, pd.Timestamp)

    # def test_cancel_all(self):
    #     ob = OrderBook(on_complete=self.on_complete_mock)

    #     # Create and add an order to the order book
    #     t1 = pd.Timestamp('2021-01-01')
    #     expiration = t1 + pd.Timedelta(days=1)
    #     order = Order(t1, expiration, 1, 1, 200, 20, 0, 0,
    #                   OrderSide.BUY, OrderType.LIMIT, TradeStatus.ACTIVE)
    #     ob.add_order(order)

    #     # Cancel all orders
    #     ob.cancel_all(pd.Timestamp.now())

    #     # Verify the order is canceled
    #     self.assertEqual(order.status, TradeStatus.EXPIRED_CANCELLED)
    #     self.assertNotIn(order.order_id, ob.map_to_heaps)

    # def test_expire_orders(self):
    #     ob = OrderBook(on_complete=self.on_complete_mock)

    #     # Create and add an order with an expiration date in the past
    #     past_timestamp = pd.Timestamp('2021-01-01')
    #     expiration = pd.Timestamp('2021-01-02')
    #     order = Order(past_timestamp, expiration, 1, 1, 200, 20,
    #                   0, 0, OrderSide.BUY, OrderType.LIMIT, TradeStatus.ACTIVE)
    #     ob.add_order(order)

    #     # Verify that the order is initially in the order book
    #     self.assertIn(order.order_id, ob.map_to_heaps)

    #     # Expire the orders
    #     ob.match(pd.Timestamp('2021-01-03'))

    #     # Verify that the order is removed from the order book after expiration
    #     self.assertNotIn(order.order_id, ob.map_to_heaps)

    #     # Verify that the on_complete callback is called with the correct parameters
    #     self.assertEqual(len(self.on_complete_calls), 1)
    #     trade = self.on_complete_calls[0]

    #     self.assertEqual(trade.buy_order, order)
    #     self.assertIsInstance(trade.timestamp, pd.Timestamp)

    def test_zero_sum(self):
        random.seed(42)

        traders = [
            {
                'id': x,
                'money': 100000,
                'stocks': 1000
            }
            for x in range(100)
        ]

        money_sum = sum([x['money'] for x in traders])
        stocks_sum = sum([x['stocks'] for x in traders])

        def on_insert(order: Order):
            nonlocal traders

            return True

        def on_complete(trade: Trade):
            nonlocal traders
            buy_order = trade.buy_order
            sell_order = trade.sell_order

            if buy_order is None or sell_order is None:
                assert trade.filled_money == 0
                assert trade.filled_size == 0
                assert trade.filled_price is None
                return {"can_buy": False, "can_sell": False}

            buyer_id = buy_order.trader_id
            seller_id = sell_order.trader_id

            can_buy = traders[buyer_id]['money'] >= trade.filled_money
            can_sell = traders[seller_id]['stocks'] >= trade.filled_size

            if not can_buy or not can_sell:
                return {"can_buy": can_buy, "can_sell": can_sell}

            traders[buyer_id]['money'] -= trade.filled_money
            traders[buyer_id]['stocks'] += trade.filled_size

            traders[seller_id]['money'] += trade.filled_money
            traders[seller_id]['stocks'] -= trade.filled_size

            return {"can_buy": True, "can_sell": True}

        ob = OrderBook(on_insert=on_insert, on_complete=on_complete)

        order_id = 0

        def get_order_id():
            nonlocal order_id
            order_id += 1
            return order_id

        def get_random_order():
            random_trader = random.choice(traders)

            buy_sell = random.choice([OrderSide.BUY, OrderSide.SELL])
            type = random.choice([OrderType.LIMIT, OrderType.MARKET])
            market_price = ob.get_market_price()
            if market_price is None:
                market_price = 100

            price = random.randint(500, 1500)
            size = random.randint(1, 1000)

            tm = pd.Timestamp.now()

            order = Order(tm, tm + pd.Timedelta(seconds=1),
                          get_order_id(), random_trader['id'],
                          price, size, 0, 0,
                          buy_sell, type,
                          TradeStatus.PENDING)

            return order

        l = []
        for _ in range(1000):
            # t1 = pd.Timestamp.now()
            for _ in range(1000):
                order = get_random_order()
                if order is None:
                    continue
                ob.add_order(order)
            print(ob.match(pd.Timestamp.now()))

            if len(ob.buy_side) == 0 or len(ob.sell_side) == 0:
                continue
            buy_side = ob.buy_side.peek().price
            sell_side = ob.sell_side.peek().price

            l.append((buy_side, sell_side))
            # t1 = (pd.Timestamp.now() - t1).total_seconds()
            # print(t1)
        ob.cancel_all(pd.Timestamp.now())

        plt.plot([x[0] for x in l])
        plt.plot([x[1] for x in l])
        plt.show()

        money_sum_after = sum([x['money'] for x in traders])
        stocks_sum_after = sum([x['stocks'] for x in traders])

        # print(money_sum, money_sum_after)
        # print(stocks_sum, stocks_sum_after)

        self.assertEqual(money_sum, money_sum_after)
        self.assertEqual(stocks_sum, stocks_sum_after)


if __name__ == '__main__':
    unittest.main()
