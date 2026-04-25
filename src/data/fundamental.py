"""
基本面数据获取模块
提供财务数据、估值指标、资金流向等基本面数据获取
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import akshare as ak
import numpy as np


class FundamentalDataProvider:
    """基本面数据提供者"""
    
    def __init__(self):
        pass
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        获取股票基本信息
        """
        try:
            code = symbol.replace('.SH', '').replace('.SZ', '')
            info = ak.stock_individual_info(symbol=code)
            if info.empty:
                return None
            
            result = {}
            for _, row in info.iterrows():
                result[row['item']] = row['value']
            return result
        except Exception:
            return None
    
    def get_financial_report(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取财务报表数据
        """
        try:
            code = symbol.replace('.SH', '').replace('.SZ', '')
            # 获取利润表
            df = ak.stock_financial_report(stock=code, report_type="profit")
            return df
        except Exception:
            return None
    
    def get_financial_indicator(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取财务指标
        """
        try:
            code = symbol.replace('.SH', '').replace('.SZ', '')
            df = ak.stock_financial_indicator(stock=code)
            return df
        except Exception:
            return None
    
    def get_valuation_metrics(self, symbol: str) -> Optional[Dict]:
        """
        获取估值指标 PE/PB/PS 等
        """
        try:
            code = symbol.replace('.SH', '').replace('.SZ', '')
            # 获取最新估值数据
            df = ak.stock_zh_a_spot()
            row = df[df['代码'] == code]
            if row.empty:
                return None
            
            row = row.iloc[0]
            return {
                'pe': float(row.get('p/e', np.nan)) if pd.notna(row.get('p/e')) else None,
                'pb': float(row.get('p/b', np.nan)) if pd.notna(row.get('p/b')) else None,
                'market_cap': float(row.get('总市值', np.nan)) if pd.notna(row.get('总市值')) else None,
                'turnover': float(row.get('换手率', np.nan)) if pd.notna(row.get('换手率')) else None,
                'price': float(row.get('最新价', np.nan)),
                'change_pct': float(row.get('涨跌幅', np.nan))
            }
        except Exception as e:
            print(f"Error getting valuation for {symbol}: {e}")
            return None
    
    def get_roe(self, symbol: str) -> Optional[float]:
        """
        获取最新ROE
        """
        try:
            df = self.get_financial_indicator(symbol)
            if df is None or df.empty:
                return None
            # 最新一期ROE
            if 'roe' in df.columns:
                return float(df['roe'].iloc[-1])
            return None
        except Exception:
            return None
    
    def get_growth_rates(self, symbol: str) -> Optional[Dict]:
        """
        获取成长率数据
        """
        try:
            df = self.get_financial_indicator(symbol)
            if df is None or df.empty:
                return None
            
            latest = df.iloc[-1]
            return {
                'revenue_growth': float(latest.get('tr_yoy', np.nan)) if 'tr_yoy' in latest else None,
                'profit_growth': float(latest.get('profit_yoy', np.nan)) if 'profit_yoy' in latest else None,
            }
        except Exception:
            return None
    
    def get_capital_flow(self, symbol: str) -> Optional[Dict]:
        """
        获取资金流向数据
        """
        try:
            code = symbol.replace('.SH', '').replace('.SZ', '')
            df = ak.stock_zh_fund_flow(stock=code)
            if df.empty:
                return None
            
            latest = df.iloc[-1]
            return {
                'main_inflow': float(latest.get('主力净流入', 0)),
                'main_inflow_pct': float(latest.get('主力净占比', 0)),
                'super_inflow': float(latest.get('超大单净流入', 0)),
                'big_inflow': float(latest.get('大单净流入', 0)),
                'mid_inflow': float(latest.get('中单净流入', 0)),
                'small_inflow': float(latest.get('小单净流入', 0)),
            }
        except Exception:
            return None
    
    def get_north_flow(self) -> Optional[pd.DataFrame]:
        """
        获取北向资金每日流向
        """
        try:
            return ak.stock_hs_north_flow()
        except Exception:
            return None
    
    def get_industry_info(self, symbol: str) -> Optional[Dict]:
        """
        获取行业信息
        """
        try:
            code = symbol.replace('.SH', '').replace('.SZ', '')
            df = ak.stock_board_industry_name()
            # 通过股票代码匹配行业
            info = ak.stock_info(symbol=code)
            if info is not None and '行业' in info:
                return {'industry': info['行业']}
            return None
        except Exception:
            return None


class MacroDataProvider:
    """宏观经济数据提供者"""
    
    def __init__(self):
        pass
    
    def get_china_cpi(self) -> Optional[pd.DataFrame]:
        """获取中国CPI数据"""
        try:
            return ak.cnbs_cpi_monthly()
        except Exception:
            return None
    
    def get_china_ppi(self) -> Optional[pd.DataFrame]:
        """获取中国PPI数据"""
        try:
            return ak.cnbs_ppi_monthly()
        except Exception:
            return None
    
    def get_china_pmi(self) -> Optional[pd.DataFrame]:
        """获取中国PMI数据"""
        try:
            return ak.cnbs_pmi()
        except Exception:
            return None
    
    def get_money_supply(self) -> Optional[pd.DataFrame]:
        """获取货币供应量 M1/M2"""
        try:
            return ak.cnbs_money_supply()
        except Exception:
            return None
    
    def get_social_financing(self) -> Optional[pd.DataFrame]:
        """获取社融数据"""
        try:
            return ak.china_social_financing()
        except Exception:
            return None
    
    def get_rates_china(self) -> Optional[pd.DataFrame]:
        """获取中国国债收益率曲线"""
        try:
            return ak.china_bond_yield()
        except Exception:
            return None
    
    def get_lpr(self) -> Optional[pd.DataFrame]:
        """获取LPR报价"""
        try:
            return ak.china_lpr()
        except Exception:
            return None
    
    def get_exchange_rate(self) -> Optional[pd.DataFrame]:
        """获取人民币汇率"""
        try:
            return ak.cny_central_parity()
        except Exception:
            return None
    
    def get_dollar_index(self) -> Optional[pd.DataFrame]:
        """获取美元指数"""
        try:
            return ak.fx_dollar_index()
        except Exception:
            return None
    
    def get_commodity_prices(self) -> Dict:
        """获取主要大宗商品价格"""
        result = {}
        try:
            # 原油价格
            result['crude_oil'] = ak.fx_spot_hist(symbol="WTIL")
        except Exception:
            pass
        try:
            # 黄金价格
            result['gold'] = ak.fx_spot_hist(symbol="XAUUSD")
        except Exception:
            pass
        try:
            # 铜
            result['copper'] = ak.fx_spot_hist(symbol="CUFX")
        except Exception:
            pass
        return result


class MarketBreadthProvider:
    """市场宽度数据提供者"""
    
    def __init__(self):
        pass
    
    def get_market_breadth(self) -> Optional[Dict]:
        """
        获取市场广度数据：上涨家数、下跌家数、涨停、跌停
        """
        try:
            # 获取全市场涨跌
            df = ak.stock_zh_a_spot()
            if df.empty:
                return None
            
            up = len(df[df['涨跌幅'] > 0])
            down = len(df[df['涨跌幅'] < 0])
            flat = len(df[df['涨跌幅'] == 0])
            
            # 涨停统计
            limit_up = len(df[df['涨跌幅'] >= 9.5])
            limit_down = len(df[df['涨跌幅'] <= -9.5])
            
            # 总成交额
            total_turnover = df['成交额'].sum()
            
            return {
                'date': datetime.now().date(),
                'advance': up,
                'decline': down,
                'unchanged': flat,
                'advance_decline_ratio': up / down if down > 0 else float('inf'),
                'limit_up': limit_up,
                'limit_down': limit_down,
                'total_turnover': total_turnover,
                'stock_count': len(df)
            }
        except Exception as e:
            print(f"Error getting market breadth: {e}")
            return None
    
    def get_north_south_flow(self) -> Optional[Dict]:
        """
        获取北向/南向资金流向
        """
        try:
            df = ak.stock_hs_north_flow_history()
            if df.empty:
                return None
            
            latest = df.iloc[-1]
            return {
                'date': latest.name if hasattr(latest, 'name') else datetime.now().date(),
                'north_flow': float(latest.get('north_money', 0)),
                'south_flow': float(latest.get('south_money', 0)) if 'south_money' in latest else None
            }
        except Exception:
            return None
    
    def get_margin_trading(self) -> Optional[pd.DataFrame]:
        """
        获取融资融券数据
        """
        try:
            return ak.stock_margin_summary()
        except Exception:
            return None
    
    def get_vix(self) -> Optional[float]:
        """
        获取中国VIX（恐慌指数）
        """
        try:
            df = ak.index_vix()
            if df.empty:
                return None
            return float(df['close'].iloc[-1])
        except Exception:
            return None


class IndustryRotationProvider:
    """行业轮动数据提供者"""
    
    def __init__(self):
        pass
    
    def get_industry_performance(self, days: int = 5) -> pd.DataFrame:
        """
        获取各行业表现，用于绘制热力图
        """
        try:
            # 获取申万一级行业每日数据
            df = ak.stock_board_sw_index()
            df = df.sort_values('trade_date')
            
            # 计算近N日涨跌幅
            if len(df) > days:
                df['pct_{}d'.format(days)] = df['close'].pct_change(days) * 100
                df['pct_10d'] = df['close'].pct_change(10) * 100
                df['pct_20d'] = df['close'].pct_change(20) * 100
            
            return df
        except Exception as e:
            print(f"Error getting industry performance: {e}")
            return pd.DataFrame()
    
    def get_sw_industries(self) -> List[str]:
        """获取申万一级行业列表"""
        try:
            df = ak.stock_board_sw_name()
            return df['name'].tolist()
        except Exception:
            return []
    
    def get_industry_capital_flow(self) -> Optional[pd.DataFrame]:
        """获取行业资金流向"""
        try:
            return ak.stock_board_fund_flow()
        except Exception:
            return None
