"""
多维度股票评分系统
对每只股票进行 0-100 分综合评分
- 技术面评分 (30%)
- 基本面评分 (30%)
- 资金面评分 (20%)
- 市场情绪评分 (20%)
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass

from ..utils.indicators import calculate_all_indicators
from lianghua.src.data.fundamental import FundamentalDataProvider
from lianghua.src.data.akshare_provider import AkShareDataProvider


@dataclass
class ScoreResult:
    """评分结果"""
    total_score: float
    technical_score: float
    fundamental_score: float
    capital_score: float
    sentiment_score: float
    details: Dict
    rating: str


class StockScorer:
    """多维度股票评分器"""
    
    def __init__(self):
        self.data_provider = AkShareDataProvider()
        self.fundamental_provider = FundamentalDataProvider()
    
    def score_technical(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        技术面评分 (0-30分)
        包含：趋势强度、动量指标、波动率和相对强度、成交量确认
        """
        score = 0.0
        details = {}
        
        if df.empty or len(df) < 200:
            return 0, {'error': '数据不足'}
        
        # 计算所有指标
        df_ind = calculate_all_indicators(df)
        last = df_ind.iloc[-1]
        
        # 1. 趋势强度 (权重: 10分)
        # ADX 判断趋势强度
        adx = last.get('adx14', 25)
        if adx > 50:
            trend_strength = 10  # 强趋势
        elif adx > 25:
            trend_strength = 7   # 中等趋势
        else:
            trend_strength = 4   # 横盘震荡
        details['adx'] = adx
        details['trend_strength'] = trend_strength
        score += trend_strength
        
        # 2. 均线排列判断趋势方向 (权重: 5分)
        if last.get('ma_bullish', False):
            ma_score = 5  # 多头排列
        elif last.get('ma_bearish', False):
            ma_score = 2  # 空头排列
        else:
            ma_score = 3.5  # 混合
        details['ma_bullish'] = last.get('ma_bullish', False)
        details['ma_score'] = ma_score
        score += ma_score
        
        # 3. 动量指标 (权重: 8分)
        momentum_score = 0
        # RSI
        rsi = last.get('rsi14', 50)
        if 30 < rsi < 70:
            momentum_score += 2  # 健康区间
        elif rsi <= 30:
            momentum_score += 2.5  # 超卖，可能反弹
        else:
            momentum_score += 1  # 超买，风险
        
        # MACD
        if last.get('macd_diff', 0) > last.get('macd_signal', 0):
            momentum_score += 2  # MACD在零线上方/金叉
        if last.get('macd_cross_up', False):
            momentum_score += 1.5  # 刚刚金叉
        
        # KDJ
        if not last.get('kdj_overbought', False) and last.get('kdj_k', 50) < 80:
            momentum_score += 2.5
        
        details['rsi'] = rsi
        details['momentum_score'] = min(momentum_score, 8)
        score += min(momentum_score, 8)
        
        # 4. 波动率和成交量确认 (权重: 7分)
        # ATR波动率，适中最好
        volatility = last.get('volatility', 2)
        if 1 < volatility < 3:
            vol_score = 3  # 波动率适中
        elif volatility < 1:
            vol_score = 2  # 太低，缺乏波动
        else:
            vol_score = 1  # 波动太大
        
        # 成交量确认当前趋势
        if last.get('close', 0) > last.get('sma20', 0) and last.get('volume', 0) > last.get('volume_ma20', 0):
            vol_score += 2  # 上涨放量，健康
        elif last.get('close', 0) < last.get('sma20', 0) and last.get('volume', 0) < last.get('volume_ma20', 0):
            vol_score += 2  # 下跌缩量，健康
        
        # 是否跌破布林带下轨或突破上轨
        if last.get('bb_below_lower', False):
            vol_score += 2  # 超跌机会
        elif not last.get('bb_above_upper', False):
            vol_score += 1
        
        details['volatility'] = volatility
        details['vol_score'] = min(vol_score, 7)
        score += min(vol_score, 7)
        
        final_technical = min(score, 30.0)
        details['final_technical'] = final_technical
        
        return final_technical, details
    
    def score_fundamental(self, symbol: str) -> Tuple[float, Dict]:
        """
        基本面评分 (0-30分)
        包含：估值水平、盈利能力、成长能力、财务健康
        """
        score = 0.0
        details = {}
        
        # 获取估值数据
        valuation = self.fundamental_provider.get_valuation_metrics(symbol)
        if valuation is None:
            return 0, {'error': '无法获取估值数据'}
        
        # 1. 估值水平 (权重: 8分)
        pe = valuation.get('pe')
        pb = valuation.get('pb')
        
        if pe is not None and pe > 0:
            if pe < 15:
                pe_score = 8  # 低估
            elif pe < 25:
                pe_score = 6  # 合理
            elif pe < 40:
                pe_score = 4  # 偏高
            else:
                pe_score = 2  # 高估
        else:
            pe_score = 4  # 亏损，中等
        
        details['pe'] = pe
        details['pe_score'] = pe_score
        score += pe_score
        
        # 2. 盈利能力 (权重: 8分)
        roe = self.fundamental_provider.get_roe(symbol)
        if roe is not None:
            if roe > 20:
                roe_score = 8  # 非常优秀
            elif roe > 15:
                roe_score = 6  # 优秀
            elif roe > 10:
                roe_score = 5  # 良好
            elif roe > 5:
                roe_score = 3  # 一般
            else:
                roe_score = 1  # 较差
        else:
            roe_score = 4
        details['roe'] = roe
        details['roe_score'] = roe_score
        score += roe_score
        
        # 3. 成长能力 (权重: 7分)
        growth = self.fundamental_provider.get_growth_rates(symbol)
        if growth is not None:
            profit_growth = growth.get('profit_growth')
            if profit_growth is not None and profit_growth > 0:
                if profit_growth > 30:
                    growth_score = 7
                elif profit_growth > 20:
                    growth_score = 6
                elif profit_growth > 10:
                    growth_score = 5
                elif profit_growth > 0:
                    growth_score = 3
                else:
                    growth_score = 1
            else:
                growth_score = 2
        else:
            growth_score = 3.5
        details['profit_growth'] = growth.get('profit_growth') if growth else None
        details['growth_score'] = growth_score
        score += growth_score
        
        # 4. 财务健康 (权重: 7分)
        # 这里简化，后续可以扩展更多指标
        market_cap = valuation.get('market_cap')
        if market_cap is not None:
            # 中等市值流动性最好，太大增长不足，太小风险太高
            if 100 < market_cap < 1000:
                cap_score = 7
            elif 50 < market_cap < 2000:
                cap_score = 6
            elif 20 < market_cap < 5000:
                cap_score = 4
            else:
                cap_score = 3
        else:
            cap_score = 4
        details['market_cap'] = market_cap
        details['cap_score'] = cap_score
        score += cap_score
        
        final_fundamental = min(score, 30.0)
        details['final_fundamental'] = final_fundamental
        
        return final_fundamental, details
    
    def score_capital(self, symbol: str) -> Tuple[float, Dict]:
        """
        资金面评分 (0-20分)
        包含：北向资金、机构持仓、龙虎榜、融资买入
        """
        score = 0.0
        details = {}
        
        # 获取资金流向
        capital_flow = self.fundamental_provider.get_capital_flow(symbol)
        
        # 1. 主力资金流向 (权重: 8分)
        if capital_flow is not None:
            main_inflow = capital_flow.get('main_inflow', 0)
            if main_inflow > 0:
                # 主力净流入加分
                if main_inflow > 10000:  # 1亿以上
                    flow_score = 8
                elif main_inflow > 5000:
                    flow_score = 6
                elif main_inflow > 1000:
                    flow_score = 4
                else:
                    flow_score = 2
            else:
                # 主力净流出减分
                flow_score = 1
        else:
            flow_score = 5  # 未知，中等
        
        details['main_inflow'] = capital_flow.get('main_inflow') if capital_flow else None
        details['flow_score'] = flow_score
        score += flow_score
        
        # 2. 北向资金持仓变化 (简化实现，权重: 6分)
        details['north_change'] = None
        details['north_score'] = 3
        score += 3  # 默认中等
        
        # 3. 活跃度 (权重: 6分)
        valuation = self.fundamental_provider.get_valuation_metrics(symbol)
        if valuation is not None and 'turnover' in valuation:
            turnover = valuation.get('turnover', 0)
            if 1 < turnover < 5:
                # 换手率适中，流动性好
                turn_score = 6
            elif 0.5 < turnover < 8:
                turn_score = 4
            else:
                turn_score = 2
        else:
            turn_score = 3
        details['turnover'] = valuation.get('turnover') if valuation else None
        details['turn_score'] = turn_score
        score += turn_score
        
        final_capital = min(score, 20.0)
        details['final_capital'] = final_capital
        
        return final_capital, details
    
    def score_sentiment(self, symbol: str) -> Tuple[float, Dict]:
        """
        市场情绪评分 (0-20分)
        包含：分析师评级、新闻情感、社交媒体热度
        """
        score = 0.0
        details = {}
        
        # 简化版本，后续可接入新闻API做情感分析
        # 当前基于涨跌幅度简单判断
        
        details['analyst_rating'] = 'neutral'
        details['news_sentiment'] = 'neutral'
        
        # 默认给中等分数，预留扩展
        score += 10
        
        # 可以根据近期涨跌调整
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        try:
            df = self.data_provider.get_ohlcv(symbol, start_date, end_date)
            if not df.empty:
                pct = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
                if pct < -10:
                    # 超跌可能反转
                    score += 5
                elif -10 < pct < 5:
                    score += 5
                elif 5 < pct < 15:
                    score += 3
                else:
                    # 涨幅太大，追高风险
                    score += 1
            details['_30d_change'] = pct if not df.empty else None
        except Exception:
            pass
        
        final_sentiment = min(score, 20.0)
        details['final_sentiment'] = final_sentiment
        
        return final_sentiment, details
    
    def calculate_total_score(self, symbol: str) -> ScoreResult:
        """
        计算股票的综合评分
        """
        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 3)  # 3年数据
        df = self.data_provider.get_ohlcv(symbol, start_date, end_date)
        
        if df.empty:
            return ScoreResult(
                total_score=0,
                technical_score=0,
                fundamental_score=0,
                capital_score=0,
                sentiment_score=0,
                details={'error': '无法获取价格数据'},
                rating='无数据'
            )
        
        # 计算各维度评分
        technical_score, technical_details = self.score_technical(df)
        fundamental_score, fundamental_details = self.score_fundamental(symbol)
        capital_score, capital_details = self.score_capital(symbol)
        sentiment_score, sentiment_details = self.score_sentiment(symbol)
        
        # 计算总分 (权重已经在各维度分配好，直接相加)
        total_score = technical_score + fundamental_score + capital_score + sentiment_score
        
        # 综合评级
        if total_score >= 80:
            rating = '强力买入'
        elif total_score >= 70:
            rating = '买入'
        elif total_score >= 60:
            rating = '增持'
        elif total_score >= 50:
            rating = '持有'
        elif total_score >= 40:
            rating = '减持'
        else:
            rating = '卖出'
        
        details = {
            'technical': technical_details,
            'fundamental': fundamental_details,
            'capital': capital_details,
            'sentiment': sentiment_details,
            'symbol': symbol,
            'last_price': df['close'].iloc[-1] if not df.empty else None,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        return ScoreResult(
            total_score=round(total_score, 2),
            technical_score=round(technical_score, 2),
            fundamental_score=round(fundamental_score, 2),
            capital_score=round(capital_score, 2),
            sentiment_score=round(sentiment_score, 2),
            details=details,
            rating=rating
        )
    
    def screen_stocks(self, symbols: list) -> pd.DataFrame:
        """
        批量评分选股
        """
        results = []
        for symbol in symbols:
            try:
                result = self.calculate_total_score(symbol)
                results.append({
                    'symbol': symbol,
                    'total_score': result.total_score,
                    'technical': result.technical_score,
                    'fundamental': result.fundamental_score,
                    'capital': result.capital_score,
                    'sentiment': result.sentiment_score,
                    'rating': result.rating,
                    'last_price': result.details.get('last_price')
                })
            except Exception as e:
                print(f"Error scoring {symbol}: {e}")
                continue
        
        df = pd.DataFrame(results)
        df = df.sort_values('total_score', ascending=False)
        return df
