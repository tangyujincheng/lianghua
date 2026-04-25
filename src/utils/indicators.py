"""
Technical indicator calculations
"""
import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Simple Moving Average - 简单移动平均
    
    参数:
        series: 价格序列
        period: 周期
    """
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average - 指数移动平均
    """
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index - 相对强弱指标
    
    范围: 0-100，通常RSI < 30 超卖，> 70 超买
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def macd(series: pd.Series, fast_period: int = 12, slow_period: int = 26, 
         signal_period: int = 9) -> dict:
    """
    MACD - Moving Average Convergence Divergence
    
    返回:
        {
            'diff': DIF线 (快速EMA - 慢速EMA),
            'signal': DEA信号线 (diff的EMA),
            'histogram': MACD柱 (diff - signal)
        }
    """
    ema_fast = ema(series, fast_period)
    ema_slow = ema(series, slow_period)
    diff = ema_fast - ema_slow
    signal = ema(diff, signal_period)
    histogram = diff - signal
    
    return {
        'diff': diff,
        'signal': signal,
        'histogram': histogram
    }


def bollinger_bands(series: pd.Series, period: int = 20, 
                   num_std: float = 2.0) -> dict:
    """
    Bollinger Bands - 布林带
    
    返回:
        {
            'middle': 中轨 (SMA),
            'upper': 上轨 (中轨 + num_std * std),
            'lower': 下轨 (中轨 - num_std * std)
        }
    """
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    
    return {
        'middle': middle,
        'upper': upper,
        'lower': lower
    }


def atr(high: pd.Series, low: pd.Series, close: pd.Series, 
        period: int = 14) -> pd.Series:
    """
    Average True Range - 平均真实波幅
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def stoch(high: pd.Series, low: pd.Series, close: pd.Series, 
          k_period: int = 14, d_period: int = 3) -> dict:
    """
    Stochastic Oscillator - 随机指标
    
    返回:
        {
            'k': %K线,
            'd': %D线
        }
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = sma(k, d_period)
    
    return {
        'k': k,
        'd': d
    }


def adx(high: pd.Series, low: pd.Series, close: pd.Series, 
        period: int = 14) -> pd.Series:
    """
    Average Directional Index - 平均方向指数
    """
    up_move = high.diff()
    down_move = -low.diff()
    
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
    
    tr_atr = atr(high, low, close, period)
    plus_di = 100 * ema(plus_dm, period) / tr_atr
    minus_di = 100 * ema(minus_dm, period) / tr_atr
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = ema(dx, period)
    
    return adx


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    On-Balance Volume - 能量潮
    """
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Williams %R - 威廉指标
    范围: -100 到 0，-20 以上超买，-80 以下超卖
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    r = -100 * (highest_high - close) / (highest_high - lowest_low)
    return r


def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """
    Commodity Channel Index - 顺势指标
    通常 CCI > 100 超买，< -100 超卖
    """
    typical_price = (high + low + close) / 3
    mean_tp = typical_price.rolling(window=period).mean()
    mean_deviation = abs(typical_price - mean_tp).rolling(window=period).mean()
    cci = (typical_price - mean_tp) / (0.015 * mean_deviation)
    return cci


def dma(close: pd.Series, short_period: int = 10, long_period: int = 50) -> dict:
    """
    DMA - 平行线差指标
    """
    dma_ma = close.rolling(window=short_period).mean() - close.rolling(window=long_period).mean()
    ama = dma_ma.rolling(window=10).mean()
    return {
        'dma': dma_ma,
        'ama': ama
    }


def kdj(high: pd.Series, low: pd.Series, close: pd.Series, 
        fastk_period: int = 9, slowk_period: int = 3, slowd_period: int = 3) -> dict:
    """
    KDJ 随机指标
    """
    lowest_low = low.rolling(window=fastk_period).min()
    highest_high = high.rolling(window=fastk_period).max()
    
    rsv = 100 * (close - lowest_low) / (highest_high - lowest_low)
    rsv = rsv.fillna(50)
    
    k = rsv.ewm(com=slowk_period-1, adjust=False).mean()
    d = k.ewm(com=slowd_period-1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return {
        'k': k,
        'd': d,
        'j': j
    }


def momentum(close: pd.Series, period: int = 10) -> pd.Series:
    """
    Momentum - 动量指标
    """
    return close / close.shift(period) * 100


def roc(close: pd.Series, period: int = 12) -> pd.Series:
    """
    Rate of Change - 变动率指标
    """
    return (close - close.shift(period)) / close.shift(period) * 100


def tr(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """
    True Range - 真实波幅
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)


def chop(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Chop Zone - 震荡区间指标
    """
    ci = (close - close.shift(14)) / close.shift(14) * 100
    return ci


def relative_strength(close: pd.Series, benchmark_close: pd.Series) -> pd.Series:
    """
    Relative Strength - 相对强度 (个股相对大盘)
    """
    return close / benchmark_close


def donchian_channels(high: pd.Series, low: pd.Series, period: int = 20) -> dict:
    """
    Donchian Channels - 唐奇安通道 (海龟交易法则使用)
    """
    upper = high.rolling(window=period).max()
    lower = low.rolling(window=period).min()
    middle = (upper + lower) / 2
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }


def volume_ma(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Volume Moving Average - 成交量移动平均
    """
    return volume.rolling(window=period).mean()


def volume_ratio(volume: pd.Series, period: int = 5) -> pd.Series:
    """
    Volume Ratio - 量比
    """
    return volume / volume.rolling(window=period).mean()


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算所有常用技术指标并添加到DataFrame中
    输入需要包含: open, high, low, close, volume
    """
    result = df.copy()
    
    # 移动平均
    result['sma5'] = sma(result['close'], 5)
    result['sma10'] = sma(result['close'], 10)
    result['sma20'] = sma(result['close'], 20)
    result['sma50'] = sma(result['close'], 50)
    result['sma200'] = sma(result['close'], 200)
    result['ema12'] = ema(result['close'], 12)
    result['ema26'] = ema(result['close'], 26)
    
    # RSI
    result['rsi6'] = rsi(result['close'], 6)
    result['rsi12'] = rsi(result['close'], 12)
    result['rsi14'] = rsi(result['close'], 14)
    
    # MACD
    macd_result = macd(result['close'])
    result['macd_diff'] = macd_result['diff']
    result['macd_signal'] = macd_result['signal']
    result['macd_hist'] = macd_result['histogram']
    
    # 布林带
    bb_result = bollinger_bands(result['close'])
    result['bb_mid'] = bb_result['middle']
    result['bb_upper'] = bb_result['upper']
    result['bb_lower'] = bb_result['lower']
    
    # KDJ
    kdj_result = kdj(result['high'], result['low'], result['close'])
    result['kdj_k'] = kdj_result['k']
    result['kdj_d'] = kdj_result['d']
    result['kdj_j'] = kdj_result['j']
    
    # ATR
    result['atr14'] = atr(result['high'], result['low'], result['close'], 14)
    
    # ADX
    result['adx14'] = adx(result['high'], result['low'], result['close'], 14)
    
    # OBV
    result['obv'] = obv(result['close'], result['volume'])
    
    # 威廉指标
    result['wr14'] = williams_r(result['high'], result['low'], result['close'], 14)
    
    # CCI
    result['cci20'] = cci(result['high'], result['low'], result['close'], 20)
    
    # DMA
    dma_result = dma(result['close'])
    result['dma'] = dma_result['dma']
    result['dma_ama'] = dma_result['ama']
    
    # 动量
    result['momentum10'] = momentum(result['close'], 10)
    result['roc12'] = roc(result['close'], 12)
    
    # 成交量指标
    result['volume_ma5'] = volume_ma(result['volume'], 5)
    result['volume_ma20'] = volume_ma(result['volume'], 20)
    result['volume_ratio'] = volume_ratio(result['volume'], 5)
    
    # 唐奇安通道 (海龟)
    donchian = donchian_channels(result['high'], result['low'], 20)
    result['donchian_upper'] = donchian['upper']
    result['donchian_lower'] = donchian['lower']
    
    # 趋势判断
    # 均线多头排列: 短期 > 中期 > 长期
    result['ma_bullish'] = (result['sma5'] > result['sma20']) & (result['sma20'] > result['sma50'])
    # 均线空头排列
    result['ma_bearish'] = (result['sma5'] < result['sma20']) & (result['sma20'] < result['sma50'])
    
    # MACD金叉死叉
    result['macd_cross_up'] = (result['macd_diff'] > result['macd_signal']) & (result['macd_diff'].shift(1) <= result['macd_signal'].shift(1))
    result['macd_cross_down'] = (result['macd_diff'] < result['macd_signal']) & (result['macd_diff'].shift(1) >= result['macd_signal'].shift(1))
    
    # 金叉死叉 RSI
    result['rsi_oversold'] = result['rsi14'] < 30
    result['rsi_overbought'] = result['rsi14'] > 70
    
    # 布林带
    result['bb_below_lower'] = result['close'] < result['bb_lower']
    result['bb_above_upper'] = result['close'] > result['bb_upper']
    
    # KDJ金叉死叉
    result['kdj_cross_up'] = (result['kdj_k'] > result['kdj_d']) & (result['kdj_k'].shift(1) <= result['kdj_d'].shift(1))
    result['kdj_cross_down'] = (result['kdj_k'] < result['kdj_d']) & (result['kdj_k'].shift(1) >= result['kdj_d'].shift(1))
    result['kdj_oversold'] = result['kdj_k'] < 20
    result['kdj_overbought'] = result['kdj_k'] > 80
    
    # 成交量放大
    result['volume_spike'] = result['volume'] > (result['volume_ma20'] * 2)
    
    # 相对波动率
    result['volatility'] = result['atr14'] / result['close'] * 100
    
    return result
