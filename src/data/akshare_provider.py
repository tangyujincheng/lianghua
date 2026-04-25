"""
AkShare data provider implementation
"""
import datetime
from datetime import datetime
from typing import List, Optional
import pandas as pd
import akshare as ak

from .base import BaseDataProvider


class AkShareDataProvider(BaseDataProvider):
    """AkShare 开源财经数据源"""
    
    def __init__(self):
        pass
    
    def get_ohlcv(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "daily"
    ) -> pd.DataFrame:
        """获取OHLCV数据"""
        # AkShare 股票代码格式不同，需要转换
        if '.' in symbol:
            code, market = symbol.split('.')
            if market == 'SH':
                ak_symbol = f"SH{code}"
            elif market == 'SZ':
                ak_symbol = f"SZ{code}"
            else:
                ak_symbol = symbol
        else:
            ak_symbol = symbol
        
        if timeframe == "daily":
            df = ak.stock_zh_a_daily(symbol=ak_symbol, start_date=start.strftime('%Y%m%d'), 
                                     end_date=end.strftime('%Y%m%d'), adjust="hfq")
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        
        if df.empty:
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        
        # 确保列名正确
        df = df.rename(columns={
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        })
        
        return df[['open', 'high', 'low', 'close', 'volume']]
    
    def get_realtime_quote(self, symbol: str) -> Optional[dict]:
        """获取实时报价"""
        try:
            df = ak.stock_zh_a_spot()
            row = df[df['代码'] == symbol.replace('.SH', '').replace('.SZ', '')]
            if row.empty:
                return None
            return {
                'symbol': symbol,
                'price': float(row.iloc[0]['最新价']),
                'open': float(row.iloc[0]['今开']),
                'high': float(row.iloc[0]['最高']),
                'low': float(row.iloc[0]['最低']),
                'volume': float(row.iloc[0]['成交量']),
                'timestamp': datetime.now()
            }
        except Exception:
            return None
    
    def get_symbols(self) -> List[str]:
        """获取所有股票列表"""
        df = ak.stock_info_a_code_name()
        symbols = []
        for _, row in df.iterrows():
            # 默认转换为SH/SZ格式
            code = str(row['code']).zfill(6)
            # 简单判断：6开头是沪市，0/3开头是深市
            if code.startswith('6') or code.startswith('9'):
                symbols.append(f"{code}.SH")
            else:
                symbols.append(f"{code}.SZ")
        return symbols
