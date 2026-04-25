"""
RSI Strategy - 相对强弱指标策略
RSI低于超卖区间买入，高于超买区间卖出
"""
from typing import Optional
import pandas as pd

from ..data.bar_data import BarData
from ..utils.indicators import rsi
from .base import BaseStrategy, Signal, SignalType


class RSIStrategy(BaseStrategy):
    """
    RSI策略
    
    策略逻辑:
    - RSI < oversold_threshold (默认 30) 买入
    - RSI > overbought_threshold (默认 70) 卖出
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.period = self.params.get('period', 14)
        self.oversold = self.params.get('oversold', 30)
        self.overbought = self.params.get('overbought', 70)
        
        self.closes = []
        self.in_position = False
        
    def initialize(self):
        """初始化"""
        self.initialized = True
        
    def on_bar(self, bar: BarData) -> Optional[Signal]:
        self.closes.append(bar.close)
        
        if len(self.closes) < self.period + 1:
            return None
        
        current_rsi = rsi(pd.Series(self.closes), self.period).iloc[-1]
        current_price = bar.close
        
        if not self.in_position and current_rsi <= self.oversold:
            # 超卖，买入
            quantity = 100
            self.in_position = True
            return Signal(
                signal_type=SignalType.BUY,
                symbol=bar.symbol,
                price=current_price,
                quantity=quantity,
                strategy_name=self.name,
                reason=f"RSI {current_rsi:.1f} <= oversold {self.oversold}"
            )
            
        elif self.in_position and current_rsi >= self.overbought:
            # 超买，卖出
            quantity = 100
            self.in_position = False
            return Signal(
                signal_type=SignalType.SELL,
                symbol=bar.symbol,
                price=current_price,
                quantity=quantity,
                strategy_name=self.name,
                reason=f"RSI {current_rsi:.1f} >= overbought {self.overbought}"
            )
            
        return None
