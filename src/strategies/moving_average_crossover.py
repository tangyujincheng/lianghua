"""
Moving Average Crossover Strategy
当短期均线从下往上穿过长期均线时买入，反之卖出
"""
import pandas as pd

from ..utils.indicators import sma
from .base import BaseStrategy


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    双均线交叉策略
    
    策略逻辑:
    - 当短期均线上穿长期均线（金叉）时买入
    - 当短期均线下穿长期均线（死叉）时卖出
    """
    
    def __init__(self, fast_period: int = 5, slow_period: int = 20, name: str = "MA_Crossover"):
        super().__init__(name)
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算均线"""
        df = data.copy()
        df['fast_ma'] = sma(df['close'], self.fast_period)
        df['slow_ma'] = sma(df['close'], self.slow_period)
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        df = self.prepare_data(data)
        
        # 计算金叉死叉
        df['signal'] = 0
        
        # 金叉：fast_ma 上穿 slow_ma
        golden_cross = (df['fast_ma'] > df['slow_ma']) & (df['fast_ma'].shift(1) <= df['slow_ma'].shift(1))
        df.loc[golden_cross, 'signal'] = 1
        
        # 死叉：fast_ma 下穿 slow_ma
        death_cross = (df['fast_ma'] < df['slow_ma']) & (df['fast_ma'].shift(1) >= df['slow_ma'].shift(1))
        df.loc[death_cross, 'signal'] = -1
        
        return df
