"""
Bar data structure for OHLCV candles
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BarData:
    """单根K线数据"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    open_interest: Optional[float] = None
    
    @property
    def date(self) -> datetime:
        """兼容旧代码，返回时间戳"""
        return self.timestamp
    
    @property
    def typical_price(self) -> float:
        """典型价格 (high + low + close) / 3"""
        return (self.high + self.low + self.close) / 3
    
    @property
    def hl2(self) -> float:
        """(high + low) / 2"""
        return (self.high + self.low) / 2
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'open_interest': self.open_interest
        }
