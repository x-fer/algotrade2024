from enum import Enum


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    PENDING = "PENDING"
    IN_QUEUE = "IN_QUEUE"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    USER_CANCELLED = "USER_CANCELLED"
