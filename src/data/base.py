"""
Base class for all data providers
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import pandas as pd

from .bar_data import BarData


class BaseDataProvider(ABC):
    """数据源基类"""
    
    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "daily"
    ) -> pd.DataFrame:
        """
        获取OHLCV历史数据
        
        参数:
            symbol: 股票代码
            start: 开始时间
            end: 结束时间
            timeframe: 时间周期，daily, 1h, 5m等
        
        返回:
            DataFrame，包含 [timestamp, open, high, low, close, volume]
        """
        pass
    
    @abstractmethod
    def get_realtime_quote(self, symbol: str) -> Optional[dict]:
        """
        获取实时报价
        
        参数:
            symbol: 股票代码
        
        返回:
            包含最新行情的字典，None表示获取失败
        """
        pass
    
    @abstractmethod
    def get_symbols(self) -> List[str]:
        """
        获取可交易标的列表
        
        返回:
            标的代码列表
        """
        pass
    
    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "daily"
    ) -> List[BarData]:
        """将OHLCV数据转换为BarData列表"""
        df = self.get_ohlcv(symbol, start, end, timeframe)
        bars = []
        for _, row in df.iterrows():
            bar = BarData(
                symbol=symbol,
                timestamp=row.name if isinstance(row.name, datetime) else row['timestamp'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume']
            )
            bars.append(bar)
        return bars
    
    def get_last_n_bars(
        self,
        symbol: str,
        n: int,
        end: datetime,
        timeframe: str = "daily"
    ) -> List[BarData]:
        """获取最后n根K线"""
        # 简化实现，实际需要根据时间计算开始时间
        all_bars = self.get_bars(symbol, datetime(1990, 1, 1), end, timeframe)
        return all_bars[-n:] if len(all_bars) > n else all_bars
