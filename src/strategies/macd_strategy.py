"""
MACD Strategy
MACD线上穿信号线买入，下穿卖出
"""
from typing import Optional
import pandas as pd

from ..data.bar_data import BarData
from ..utils.indicators import macd
from .base import BaseStrategy, Signal, SignalType


class MACDStrategy(BaseStrategy):
    """
    MACD策略
    
    策略逻辑:
    - DIF线上穿DEA线（金叉）买入
    - DIF线下穿DEA线（死叉）卖出
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast_period = self.params.get('fast_period', 12)
        self.slow_period = self.params.get('slow_period', 26)
        self.signal_period = self.params.get('signal_period', 9)
        
        self.closes = []
        self.last_macd_diff = None
        self.last_signal = None
        
    def initialize(self):
        self.initialized = True
        
    def on_bar(self, bar: BarData) -> Optional[Signal]:
        self.closes.append(bar.close)
        
        if len(self.closes) < self.slow_period:
            return None
            
        macd_result = macd(pd.Series(self.closes), self.fast_period, 
                          self.slow_period, self.signal_period)
        current_diff = macd_result['diff'].iloc[-1]
        current_signal = macd_result['signal'].iloc[-1]
        
        signal = None
        
        if self.last_macd_diff is not None:
            # 金叉：diff上穿signal -> 买入
            if self.last_macd_diff < self.last_signal and current_diff > current_signal:
                quantity = 100
                signal = Signal(
                    signal_type=SignalType.BUY,
                    symbol=bar.symbol,
                    price=bar.close,
                    quantity=quantity,
                    strategy_name=self.name,
                    reason=f"MACD golden cross: diff({current_diff:.4f}) > signal({current_signal:.4f})"
                )
            # 死叉：diff下穿signal -> 卖出
            elif self.last_macd_diff > self.last_signal and current_diff < current_signal:
                quantity = 100
                signal = Signal(
                    signal_type=SignalType.SELL,
                    symbol=bar.symbol,
                    price=bar.close,
                    quantity=quantity,
                    strategy_name=self.name,
                    reason=f"MACD death cross: diff({current_diff:.4f}) < signal({current_signal:.4f})"
                )
                
        self.last_macd_diff = current_diff
        self.last_signal = current_signal
        
        return signal
