"""
Tushare data provider implementation
"""
import os
from datetime import datetime
from typing import List, Optional
import pandas as pd
import tushare as ts

from .base import BaseDataProvider


class TushareDataProvider(BaseDataProvider):
    """Tushare A股数据源"""
    
    def __init__(self, api_key: str = None):
        """
        初始化
        
        参数:
            api_key: Tushare API token，如果为None则从环境变量读取
        """
        api_key = api_key or os.getenv('TUSHARE_TOKEN')
        if not api_key:
            raise ValueError("Tushare API token is required. "
                             "Set TUSHARE_TOKEN environment variable or pass api_key.")
        self.pro = ts.pro_api(api_key)
    
    def get_ohlcv(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "daily"
    ) -> pd.DataFrame:
        """获取OHLCV数据"""
        start_str = start.strftime('%Y%m%d')
        end_str = end.strftime('%Y%m%d')
        
        if timeframe == "daily":
            df = self.pro.daily(ts_code=symbol, start_date=start_str, end_date=end_str)
        elif timeframe == "weekly":
            df = self.pro.weekly(ts_code=symbol, start_date=start_str, end_date=end_str)
        elif timeframe == "monthly":
            df = self.pro.monthly(ts_code=symbol, start_date=start_str, end_date=end_str)
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        
        if df.empty:
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        
        # 转换列名和格式
        df = df.rename(columns={
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'trade_date': 'date'
        })
        
        # 转换日期并排序
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.sort_values('date')
        df = df.set_index('date')
        
        # 按时间顺序排列（Tushare默认倒序）
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def get_realtime_quote(self, symbol: str) -> Optional[dict]:
        """获取实时报价"""
        try:
            df = ts.get_realtime_quotes([symbol])
            if df.empty:
                return None
            row = df.iloc[0]
            return {
                'symbol': symbol,
                'price': float(row['price']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'volume': float(row['volume']),
                'timestamp': datetime.now()
            }
        except Exception:
            return None
    
    def get_symbols(self) -> List[str]:
        """获取所有股票列表"""
        df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code')
        return df['ts_code'].tolist()
    
    def get_index_components(self, index_code: str = "000001.SH") -> List[str]:
        """获取指数成分股"""
        df = self.pro.index_weight(index_code=index_code)
        if df.empty:
            return []
        return df['con_code'].tolist()
