from enum import Enum


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1


class OrderSide(Enum):
    BUY = 0
    SELL = 1


class OrderStatus(Enum):
    PENDING = 0
    IN_QUEUE = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELLED = 4
    EXPIRED = 5
    REJECTED = 6
