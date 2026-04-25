"""
Order and Trade data structures
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OrderDirection(Enum):
    """订单方向"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """订单"""
    order_id: str
    symbol: str
    direction: OrderDirection
    quantity: float
    price: Optional[float]  # None 表示市价单
    timestamp: datetime
    strategy_name: str
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    filled_avg_price: float = 0.0
    
    @property
    def is_buy(self) -> bool:
        return self.direction == OrderDirection.BUY
    
    @property
    def is_sell(self) -> bool:
        return self.direction == OrderDirection.SELL
    
    @property
    def remaining_quantity(self) -> float:
        return self.quantity - self.filled_quantity
    
    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED
    
    def to_dict(self) -> dict:
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'direction': self.direction.value,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'strategy_name': self.strategy_name,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'filled_avg_price': self.filled_avg_price
        }


@dataclass
class Trade:
    """成交记录"""
    trade_id: str
    order_id: str
    symbol: str
    direction: OrderDirection
    quantity: float
    price: float
    commission: float
    timestamp: datetime
    strategy_name: str
    
    @property
    def notional(self) -> float:
        """成交金额"""
        return self.quantity * self.price
    
    @property
    def net_amount(self) -> float:
        """净额（扣除佣金）"""
        if self.is_buy:
            return -self.notional - self.commission
        else:
            return self.notional - self.commission
    
    @property
    def is_buy(self) -> bool:
        return self.direction == OrderDirection.BUY
    
    def to_dict(self) -> dict:
        return {
            'trade_id': self.trade_id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'direction': self.direction.value,
            'quantity': self.quantity,
            'price': self.price,
            'commission': self.commission,
            'timestamp': self.timestamp.isoformat(),
            'strategy_name': self.strategy_name
        }
