"""
Bollinger Bands Strategy - 布林带策略
价格触碰下轨买入，触碰上轨卖出
"""
from typing import Optional
import pandas as pd

from ..data.bar_data import BarData
from ..utils.indicators import bollinger_bands
from .base import BaseStrategy, Signal, SignalType


class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略
    
    策略逻辑:
    - 价格跌破下轨时，认为超卖，买入
    - 价格涨破上轨时，认为超买，卖出
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.period = self.params.get('period', 20)
        self.num_std = self.params.get('num_std', 2.0)
        
        self.closes = []
        self.in_position = False
        
    def initialize(self):
        self.initialized = True
        
    def on_bar(self, bar: BarData) -> Optional[Signal]:
        self.closes.append(bar.close)
        
        if len(self.closes) < self.period:
            return None
            
        bb = bollinger_bands(pd.Series(self.closes), self.period, self.num_std)
        current_price = bar.close
        current_upper = bb['upper'].iloc[-1]
        current_lower = bb['lower'].iloc[-1]
        
        if not self.in_position and current_price <= current_lower:
            # 触碰下轨，买入
            quantity = 100
            self.in_position = True
            return Signal(
                signal_type=SignalType.BUY,
                symbol=bar.symbol,
                price=current_price,
                quantity=quantity,
                strategy_name=self.name,
                reason=f"Price {current_price:.2f} <= lower band {current_lower:.2f}"
            )
            
        elif self.in_position and current_price >= current_upper:
            # 触碰上轨，卖出
            quantity = 100
            self.in_position = False
            return Signal(
                signal_type=SignalType.SELL,
                symbol=bar.symbol,
                price=current_price,
                quantity=quantity,
                strategy_name=self.name,
                reason=f"Price {current_price:.2f} >= upper band {current_upper:.2f}"
            )
            
        return None
