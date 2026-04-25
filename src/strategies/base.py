"""
Common signal definition and strategy base class
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any
import pandas as pd


class SignalType(Enum):
    """信号类型"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CANCEL = "CANCEL"


class BaseStrategy:
    """策略基类，所有策略都需要继承这个类"""
    
    def __init__(self, name: str = "BaseStrategy"):
        self.name = name
        self.position = 0  # 当前持仓：0=空仓，1=持有，-1=做空
        
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备数据，计算技术指标等
        子类需要重写这个方法
        """
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        返回包含 'signal' 列的 DataFrame
        signal: 1=买入, -1=卖出, 0=持有
        子类需要重写这个方法
        """
        raise NotImplementedError("子类必须实现 generate_signals 方法")
    
    def get_signal_at(self, data: pd.DataFrame, index: int) -> int:
        """获取指定位置的信号"""
        signals = self.generate_signals(data)
        if index < len(signals):
            return signals.iloc[index]['signal']
        return 0
    
    def get_latest_signal(self, data: pd.DataFrame) -> int:
        """获取最新的信号"""
        return self.get_signal_at(data, len(data) - 1)
    
    def get_name(self) -> str:
        return self.name


@dataclass
class Signal:
    """交易信号"""
    signal_type: SignalType
    symbol: str
    price: float
    quantity: float
    strategy_name: str
    reason: Optional[str] = None
    order_id: Optional[str] = None
    
    @property
    def is_buy(self) -> bool:
        return self.signal_type == SignalType.BUY
    
    @property
    def is_sell(self) -> bool:
        return self.signal_type == SignalType.SELL
    
    @property
    def value(self) -> float:
        """交易金额"""
        return self.price * self.quantity
    
    def to_dict(self) -> dict:
        return {
            'signal_type': self.signal_type.value,
            'symbol': self.symbol,
            'price': self.price,
            'quantity': self.quantity,
            'strategy_name': self.strategy_name,
            'reason': self.reason
        }
