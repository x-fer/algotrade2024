from enum import Enum


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1


class OrderSide(Enum):
    BUY = 0
    SELL = 1


class OrderStatus(Enum):
    PENDING = 0
    ACTIVE = 1
    COMPLETED = 2
    CANCELLED = 3
    EXPIRED = 4