"""
Base executor class
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

from .order import Order, Trade


@dataclass
class AccountInfo:
    """账户信息"""
    cash: float
    total_value: float
    available_cash: float
    positions: dict  # symbol -> quantity
    
    def to_dict(self):
        return {
            'cash': self.cash,
            'total_value': self.total_value,
            'available_cash': self.available_cash,
            'positions': self.positions
        }


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    order: Order
    trades: List[Trade]
    message: str = ""


class BaseExecutor(ABC):
    """执行器基类"""
    
    @abstractmethod
    def execute_order(self, order: Order) -> ExecutionResult:
        """执行订单"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """获取账户信息"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        pass
    
    def get_open_orders(self) -> List[Order]:
        """获取未成交订单"""
        return []
    
    def get_position(self, symbol: str) -> float:
        """获取持仓"""
        account = self.get_account_info()
        return account.positions.get(symbol, 0.0)
