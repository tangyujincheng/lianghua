#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lianghua 量化决策系统 - 简化版演示
展示核心功能：数据获取、技术指标、股票评分、策略信号
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print("🌟 Lianghua 量化决策系统 - 核心功能演示")
print("=" * 80)
print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# =============================================================================
# 1. 数据获取和技术指标计算
# =============================================================================
print("📊 【1/4】数据获取与技术指标计算")
print("-" * 80)

try:
    import akshare as ak
    from src.utils.indicators import (
        sma, ema, rsi, macd, bollinger_bands, atr, adx,
        calculate_all_indicators
    )
    
    # 获取贵州茅台数据
    symbol = '600519'
    symbol_name = '贵州茅台'
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=120)).strftime('%Y%m%d')
    
    print(f"正在获取 {symbol_name} ({symbol}) 数据...")
    print(f"时间范围: {start_date} 至 {end_date}")
    
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                            start_date=start_date, end_date=end_date,
                            adjust="qfq")
    
    # 重命名列
    df = df.rename(columns={
        '日期': 'date',
        '开盘': 'open',
        '最高': 'high',
        '最低': 'low',
        '收盘': 'close',
        '成交量': 'volume'
    })
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"成功获取 {len(df)} 条K线数据")
    print(f"最新收盘价: {df.iloc[-1]['close']:.2f} 元")
    print(f"最新日期: {df.iloc[-1]['date'].strftime('%Y-%m-%d')}")
    print()
    
    # 计算技术指标
    print("正在计算技术指标...")
    df = calculate_all_indicators(df)
    
    latest = df.iloc[-1]
    
    print("📈 技术指标概览:")
    print(f"  SMA5:   {latest['sma5']:.2f}")
    print(f"  SMA10:  {latest['sma10']:.2f}")
    print(f"  SMA20:  {latest['sma20']:.2f}")
    print(f"  SMA50:  {latest['sma50']:.2f}")
    print(f"  RSI(14): {latest['rsi14']:.2f}")
    print(f"  MACD(DIF):  {latest['macd_diff']:.4f}")
    print(f"  MACD(DEA):  {latest['macd_signal']:.4f}")
    print(f"  MACD柱:    {latest['macd_hist']:.4f}")
    print(f"  ATR(14):  {latest['atr14']:.2f}")
    print(f"  ADX:     {latest['adx']:.2f}")
    
    # 布林带
    print(f"  布林带上轨: {latest['bb_upper']:.2f}")
    print(f"  布林带中轨: {latest['bb_mid']:.2f}")
    print(f"  布林带下轨: {latest['bb_lower']:.2f}")
    
    # 趋势判断
    if latest['close'] > latest['sma20'] and latest['sma5'] > latest['sma20']:
        trend = "🟢 上升趋势"
    elif latest['close'] < latest['sma20'] and latest['sma5'] < latest['sma20']:
        trend = "🔴 下降趋势"
    else:
        trend = "🟡 震荡整理"
    
    # RSI判断
    if latest['rsi14'] < 30:
        rsi_status = "🟢 超卖区间"
    elif latest['rsi14'] > 70:
        rsi_status = "🔴 超买区间"
    else:
        rsi_status = "🟡 中性区间"
    
    print()
    print("🎯 技术分析结论:")
    print(f"  趋势判断: {trend}")
    print(f"  RSI状态: {rsi_status}")
    
    if latest['adx'] > 25:
        print(f"  ADX强度: {latest['adx']:.1f} - 趋势较强")
    elif latest['adx'] > 20:
        print(f"  ADX强度: {latest['adx']:.1f} - 有一定趋势")
    else:
        print(f"  ADX强度: {latest['adx']:.1f} - 趋势较弱")
    
    print()
    print("✅ 技术指标计算演示完成！")
    
except Exception as e:
    print(f"❌ 出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 2. 多维度股票评分
# =============================================================================
print("⭐ 【2/4】多维度股票评分")
print("-" * 80)

try:
    # 简化版评分逻辑（避免依赖问题）
    latest_close = latest['close']
    
    print(f"对 {symbol_name} 进行多维度评分...")
    print(f"评分维度: 技术面(30%) + 基本面(30%) + 资金面(20%) + 情绪面(20%)")
    print()
    
    # 技术面评分 (0-30分)
    tech_score = 0
    # 均线排列
    if latest['sma5'] > latest['sma10'] > latest['sma20']:
        tech_score += 10
    elif latest['sma5'] < latest['sma10'] < latest['sma20']:
        tech_score += 2
    else:
        tech_score += 5
    
    # 价格位置
    if latest['close'] > latest['sma20']:
        tech_score += 5
    else:
        tech_score += 2
    
    # RSI
    if 30 < latest['rsi14'] < 70:
        tech_score += 5
    elif latest['rsi14'] < 30:
        tech_score += 7
    else:
        tech_score += 3
    
    # MACD
    if latest['macd_diff'] > latest['macd_signal']:
        tech_score += 5
    else:
        tech_score += 3
    
    # 趋势强度 (ADX)
    if latest['adx'] > 25:
        tech_score += 5
    elif latest['adx'] > 20:
        tech_score += 3
    else:
        tech_score += 2
    
    # 基本面评分 (简化版)
    fund_score = 22  # 假设贵州茅台基本面良好
    
    # 资金面评分 (简化版)
    capital_score = 15  # 假设资金面中性
    
    # 情绪面评分
    sentiment_score = 12
    if latest['rsi14'] > 60:
        sentiment_score -= 2
    elif latest['rsi14'] < 40:
        sentiment_score += 2
    
    total_score = tech_score + fund_score + capital_score + sentiment_score
    
    # 评级
    if total_score >= 85:
        rating = "强力买入"
    elif total_score >= 75:
        rating = "买入"
    elif total_score >= 65:
        rating = "增持"
    elif total_score >= 55:
        rating = "持有"
    elif total_score >= 45:
        rating = "减持"
    else:
        rating = "卖出"
    
    print("📋 评分详情:")
    print("-" * 50)
    print(f"  技术面评分: {tech_score}/30")
    print(f"    - 均线排列: {10 if latest['ma5'] > latest['ma10'] > latest['ma20'] else 2 if latest['ma5'] < latest['ma10'] < latest['ma20'] else 5}/10")
    print(f"    - 价格位置: {5 if latest['close'] > latest['ma20'] else 2}/5")
    print(f"    - RSI状态: {7 if latest['rsi'] < 30 else 5 if latest['rsi'] < 70 else 3}/5")
    print(f"    - MACD状态: {5 if latest['macd'] > latest['signal_line'] else 3}/5")
    print(f"    - 趋势强度: {5 if latest['adx'] > 25 else 3 if latest['adx'] > 20 else 2}/5")
    print(f"  基本面评分: {fund_score}/30")
    print(f"  资金面评分: {capital_score}/20")
    print(f"  情绪面评分: {sentiment_score}/20")
    print("-" * 50)
    print(f"  综合评分: {total_score}/100")
    print(f"  投资评级: {rating}")
    print()
    
    if "买入" in rating:
        print(f"  🎯 结论: 该股票当前评分较高，建议关注或建仓")
    elif "持有" in rating:
        print(f"  🎯 结论: 该股票当前评分中性，建议持有观望")
    else:
        print(f"  🎯 结论: 该股票当前评分较低，建议谨慎或减仓")
    
    print()
    print("✅ 股票评分演示完成！")
    
except Exception as e:
    print(f"❌ 出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 3. 策略信号生成
# =============================================================================
print("📈 【3/4】策略信号生成")
print("-" * 80)

try:
    print(f"标的: {symbol_name} ({symbol})")
    print()
    
    signals = []
    
    # 策略1: 双均线交叉
    print("1️⃣ 双均线交叉策略:")
    ma5 = latest['sma5']
    ma20 = latest['sma20']
    ma5_prev = df.iloc[-2]['sma5']
    ma20_prev = df.iloc[-2]['sma20']
    
    if ma5_prev <= ma20_prev and ma5 > ma20:
        ma_signal = "🟢 金叉信号 - 买入"
        signals.append(1)
    elif ma5_prev >= ma20_prev and ma5 < ma20:
        ma_signal = "🔴 死叉信号 - 卖出"
        signals.append(-1)
    else:
        if ma5 > ma20:
            ma_signal = "🟡 多头排列 - 持有"
            signals.append(0.5)
        else:
            ma_signal = "🟡 空头排列 - 观望"
            signals.append(-0.5)
    
    print(f"  MA5: {ma5:.2f}, MA20: {ma20:.2f}")
    print(f"  结论: {ma_signal}")
    print()
    
    # 策略2: RSI超买超卖
    print("2️⃣ RSI超买超卖策略:")
    rsi_val = latest['rsi14']
    if rsi_val < 30:
        rsi_signal = "🟢 超卖区域 - 考虑买入"
        signals.append(1)
    elif rsi_val > 70:
        rsi_signal = "🔴 超买区域 - 考虑卖出"
        signals.append(-1)
    elif rsi_val > 55:
        rsi_signal = "🟡 偏强 - 持有"
        signals.append(0.3)
    elif rsi_val < 45:
        rsi_signal = "🟡 偏弱 - 观望"
        signals.append(-0.3)
    else:
        rsi_signal = "🟡 中性 - 观望"
        signals.append(0)
    
    print(f"  RSI(14): {rsi_val:.2f}")
    print(f"  结论: {rsi_signal}")
    print()
    
    # 策略3: 布林带
    print("3️⃣ 布林带策略:")
    bb_upper = latest['bb_upper']
    bb_middle = latest['bb_mid']
    bb_lower = latest['bb_lower']
    close = latest['close']
    
    bb_position = (close - bb_lower) / (bb_upper - bb_lower) * 100
    
    if close < bb_lower:
        bb_signal = "🟢 跌破下轨 - 超卖反弹机会"
        signals.append(1)
    elif close > bb_upper:
        bb_signal = "🔴 突破上轨 - 超买注意回调"
        signals.append(-1)
    elif close > bb_middle:
        bb_signal = "🟡 中轨上方运行 - 偏多"
        signals.append(0.3)
    else:
        bb_signal = "🟡 中轨下方运行 - 偏空"
        signals.append(-0.3)
    
    print(f"  上轨: {bb_upper:.2f}, 中轨: {bb_middle:.2f}, 下轨: {bb_lower:.2f}")
    print(f"  当前价格在布林带位置: {bb_position:.1f}%")
    print(f"  结论: {bb_signal}")
    print()
    
    # 策略4: MACD
    print("4️⃣ MACD趋势策略:")
    macd_val = latest['macd_diff']
    signal_val = latest['macd_signal']
    hist_val = latest['macd_hist']
    macd_prev = df.iloc[-2]['macd_diff']
    signal_prev = df.iloc[-2]['macd_signal']
    
    if macd_prev <= signal_prev and macd_val > signal_val:
        macd_signal = "🟢 金叉信号 - 买入"
        signals.append(1)
    elif macd_prev >= signal_prev and macd_val < signal_val:
        macd_signal = "🔴 死叉信号 - 卖出"
        signals.append(-1)
    elif hist_val > 0 and macd_val > 0:
        macd_signal = "🟡 多头动能 - 持有"
        signals.append(0.5)
    elif hist_val < 0 and macd_val < 0:
        macd_signal = "🟡 空头动能 - 观望"
        signals.append(-0.5)
    else:
        macd_signal = "🟡 动能转换 - 观望"
        signals.append(0)
    
    print(f"  MACD: {macd_val:.4f}, Signal: {signal_val:.4f}, Hist: {hist_val:.4f}")
    print(f"  结论: {macd_signal}")
    print()
    
    # 信号汇总
    print("📊 信号汇总与投票:")
    print("-" * 50)
    total_signal = sum(signals)
    
    bullish = sum(1 for s in signals if s > 0.3)
    bearish = sum(1 for s in signals if s < -0.3)
    neutral = 4 - bullish - bearish
    
    print(f"  🟢 看多信号: {bullish} 个")
    print(f"  🟡 中性信号: {neutral} 个")
    print(f"  🔴 看空信号: {bearish} 个")
    print(f"  综合得分: {total_signal:.2f}")
    print()
    
    if total_signal >= 2:
        final = "🎯 强烈看多 - 多策略一致看多，可考虑建仓"
    elif total_signal >= 1:
        final = "🎯 偏多 - 多数策略看多，可以关注"
    elif total_signal >= 0:
        final = "🎯 中性 - 信号分歧，建议观望"
    elif total_signal >= -1:
        final = "🎯 偏空 - 多数策略看空，谨慎操作"
    else:
        final = "🎯 强烈看空 - 多策略一致看空，建议回避"
    
    print(final)
    print()
    print("✅ 策略信号生成演示完成！")
    
except Exception as e:
    print(f"❌ 出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 4. 风险控制与仓位建议
# =============================================================================
print("🛡️ 【4/4】风险控制与仓位建议")
print("-" * 80)

try:
    current_price = latest['close']
    atr_20 = latest['atr20'] if 'atr20' in latest else latest['atr14']
    volatility = atr_20 / current_price
    
    print(f"标的: {symbol_name} ({symbol})")
    print(f"当前价格: {current_price:.2f} 元")
    print(f"20日ATR: {atr_20:.2f} 元")
    print(f"ATR波动率: {volatility*100:.2f}%")
    print()
    
    print("💡 基于ATR的仓位计算:")
    print("原理: 波动率越高，仓位越小，保证单笔风险一致")
    print()
    
    total_capital = 100000  # 总资金
    signal_confidence = 0.75  # 75%的信号置信度
    
    print(f"假设总资金: {total_capital:,} 元")
    print(f"信号置信度: {signal_confidence*100:.0f}%")
    print()
    
    # 三种风险偏好
    risk_profiles = [
        ("保守型", 0.01),  # 单笔风险1%
        ("平衡型", 0.02),  # 单笔风险2%
        ("激进型", 0.03),  # 单笔风险3%
    ]
    
    print("-" * 80)
    print(f"{'风险偏好':<10} {'单笔风险':<12} {'建议仓位':<15} {'止损价':<12} {'止盈价':<12} {'盈亏比':<10}")
    print("-" * 80)
    
    for profile_name, risk_pct in risk_profiles:
        # 单笔风险金额
        risk_amount = total_capital * risk_pct
        
        # 基于ATR的股数
        shares_atr = int(risk_amount / atr_20 / 100) * 100  # 取整到百股
        
        # 置信度调整
        shares = int(shares_atr * signal_confidence / 100) * 100
        if shares < 100:
            shares = 100  # 最少100股
        
        position_value = shares * current_price
        position_pct = position_value / total_capital
        
        # ATR止损止盈
        stop_loss = current_price - 2 * atr_20  # 2倍ATR止损
        take_profit = current_price + 3.5 * atr_20  # 3.5倍ATR止盈
        rr_ratio = (take_profit - current_price) / (current_price - stop_loss)
        
        print(f"{profile_name:<10} "
              f"{risk_amount:>8,.0f}元 ({risk_pct*100:.0f}%) "
              f"{position_value:>8,.0f}元 ({position_pct*100:.0f}%) "
              f"{stop_loss:>10.2f} "
              f"{take_profit:>10.2f} "
              f"{rr_ratio:.2f}:1")
    
    print()
    print("💡 风险管理要点:")
    print("  1. 单笔交易风险控制在总资金的1%-3%之间")
    print("  2. 波动率越高，仓位应该越小（ATR仓位管理法）")
    print("  3. 盈亏比至少要大于1.5:1才值得交易，优先选择2:1以上的机会")
    print("  4. 信号置信度越高，可以适当增加仓位")
    print("  5. 永远不要忽视止损，即使是再看好的股票")
    print("  6. 单只股票仓位建议不超过总资金的30%")
    
    print()
    print("✅ 风险控制与仓位计算演示完成！")
    
except Exception as e:
    print(f"❌ 出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 总结
# =============================================================================
print("=" * 80)
print("🎉 Lianghua 量化决策系统 - 演示完成！")
print("=" * 80)
print()
print("📋 已完成的演示模块:")
print("  ✅ 数据获取与技术指标计算")
print("  ✅ 多维度股票评分系统")
print("  ✅ 多策略信号生成与投票")
print("  ✅ 风险控制与智能仓位建议")
print()
print("💡 系统核心价值:")
print("  • 客观数据分析，避免情绪化决策")
print("  • 多维度综合评分，发现投资机会")
print("  • 多策略交叉验证，提高信号可靠性")
print("  • 科学的仓位管理，控制风险，放大收益")
print()
print("📚 下一步建议:")
print("  1. 建立自己的股票池，每天运行评分分析")
print("  2. 回测不同策略参数，找到最适合的参数组合")
print("  3. 坚持风险控制，严格执行止损止盈")
print("  4. 持续学习，不断优化自己的交易系统")
print()
print("=" * 80)
print("🌟 Lianghua - 让投资决策更科学、更理性")
print("=" * 80)
