from dataclasses import dataclass, field
from enum import Enum
from db.table import Table
from config import config
from .enum_type import enum_type


class ContractStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    CANCELLED = 2


ContractStatusField = enum_type(ContractStatus)


@dataclass
class Contract(Table):
    table_name = "contracts"
    contract_id: int
    game_id: int
    player_id: int
    bot_id: int

    size: int
    price: int
    down_payment: int
    
    start_tick: int
    end_tick: int
    filled_size: int = field(default=0)
    contract_status: ContractStatusField = ContractStatusField(default=ContractStatus.ACTIVE)

    @staticmethod
    def get_down_payment(size: int, price: int) -> int:
        return int(size * price * config["contracts"]["fee_coeff"])