#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lianghua 量化决策系统 - 完整功能演示
演示所有核心功能：市场温度计、股票评分、策略信号、回测、仓位计算
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print("🌟 Lianghua 量化决策系统 - 完整功能演示")
print("=" * 80)
print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# =============================================================================
# 1. 市场温度计演示
# =============================================================================
print("📊 【1/5】市场温度计 - 监测大盘整体情况")
print("-" * 80)

try:
    from src.data.fundamental import MarketBreadthProvider
    
    market = MarketBreadthProvider()
    
    # 获取最近交易日的市场数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"统计区间: {start_date} 至 {end_date}")
    print()
    
    # 获取主要指数表现
    print("📈 主要指数表现:")
    index_list = ['sh000001', 'sz399001', 'sz399006', 'sh000300']  # 上证指数、深证成指、创业板指、沪深300
    index_names = {'sh000001': '上证指数', 'sz399001': '深证成指', 
                   'sz399006': '创业板指', 'sh000300': '沪深300'}
    
    for idx_code in index_list:
        try:
            from src.data.akshare_provider import AkShareDataProvider
            provider = AkShareDataProvider()
            df = provider.get_daily_data(idx_code.replace('sh','').replace('sz',''), 
                                        start_date=start_date, end_date=end_date)
            if len(df) > 1:
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                change_pct = (latest['close'] - prev['close']) / prev['close'] * 100
                direction = "🔴" if change_pct < 0 else "🟢"
                print(f"  {index_names[idx_code]:<10}: {latest['close']:>8.2f}  {direction} {change_pct:+.2f}%")
        except Exception as e:
            print(f"  {index_names[idx_code]:<10}: 获取失败 ({str(e)[:30]})")
    
    print()
    print("📊 市场广度指标:")
    try:
        import akshare as ak
        # 获取涨跌家数
        df_em = ak.stock_zh_a_spot_em()
        up_count = len(df_em[df_em['涨跌幅'] > 0])
        down_count = len(df_em[df_em['涨跌幅'] < 0])
        flat_count = len(df_em[df_em['涨跌幅'] == 0])
        limit_up = len(df_em[df_em['涨跌幅'] >= 9.5])
        limit_down = len(df_em[df_em['涨跌幅'] <= -9.5])
        
        print(f"  上涨家数: {up_count} 只")
        print(f"  下跌家数: {down_count} 只")
        print(f"  平盘家数: {flat_count} 只")
        print(f"  涨停家数: {limit_up} 只")
        print(f"  跌停家数: {limit_down} 只")
        print(f"  涨跌比率: {up_count/down_count:.2f}" if down_count > 0 else "  涨跌比率: N/A")
    except Exception as e:
        print(f"  涨跌家数获取失败: {str(e)[:50]}")
    
    # 获取北向资金
    try:
        import akshare as ak
        north_money = ak.stock_hsgt_north_net_flow_in_em()
        if len(north_money) > 0:
            latest_north = north_money.iloc[-1]
            print(f"  北向资金(最新): {latest_north['value']:.1f} 亿元")
    except Exception as e:
        print(f"  北向资金获取失败")
    
    print()
    print("✅ 市场温度计演示完成！")
    
except Exception as e:
    print(f"❌ 市场温度计演示出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 2. 股票多维度评分系统演示
# =============================================================================
print("⭐ 【2/5】多维度股票评分系统 - 智能选股助手")
print("-" * 80)

try:
    from src.analysis.scoring import StockScorer
    
    scorer = StockScorer()
    
    # 测试股票列表
    test_stocks = ['600519', '000858', '002594', '601318', '000333']
    stock_names = {
        '600519': '贵州茅台',
        '000858': '五粮液',
        '002594': '比亚迪',
        '601318': '中国平安',
        '000333': '美的集团'
    }
    
    print(f"对 {len(test_stocks)} 只股票进行多维度评分...")
    print(f"评分维度: 技术面(30%) + 基本面(30%) + 资金面(20%) + 情绪面(20%)")
    print()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    results = []
    for symbol in test_stocks:
        try:
            print(f"  正在分析 {stock_names[symbol]} ({symbol})...")
            score_result = scorer.score_stock(symbol, start_date=start_date, end_date=end_date)
            score_result['symbol'] = symbol
            score_result['name'] = stock_names[symbol]
            results.append(score_result)
        except Exception as e:
            print(f"  ⚠️ {stock_names[symbol]} 分析失败: {str(e)[:40]}")
    
    print()
    print("📋 股票评分结果汇总:")
    print("-" * 80)
    print(f"{'股票名称':<12} {'代码':<10} {'综合评分':<10} {'技术面':<8} {'基本面':<8} {'资金面':<8} {'情绪面':<8} {'评级':<10}")
    print("-" * 80)
    
    for r in sorted(results, key=lambda x: x.get('total_score', 0), reverse=True):
        print(f"{r.get('name', 'N/A'):<12} "
              f"{r.get('symbol', 'N/A'):<10} "
              f"{r.get('total_score', 0):>8.1f}分 "
              f"{r.get('technical_score', 0):>6.1f}分 "
              f"{r.get('fundamental_score', 0):>6.1f}分 "
              f"{r.get('capital_flow_score', 0):>6.1f}分 "
              f"{r.get('sentiment_score', 0):>6.1f}分 "
              f"{r.get('rating', 'N/A'):<10}")
    
    print()
    print("✅ 股票评分系统演示完成！")
    
except Exception as e:
    print(f"❌ 股票评分系统演示出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 3. 策略信号生成演示
# =============================================================================
print("📈 【3/5】策略信号生成 - 多策略信号聚合")
print("-" * 80)

try:
    from src.data.akshare_provider import AkShareDataProvider
    from src.strategies.moving_average_crossover import MovingAverageCrossoverStrategy
    from src.strategies.rsi_strategy import RSIStrategy
    from src.strategies.bollinger_bands import BollingerBandsStrategy
    from src.strategies.macd_strategy import MACDStrategy
    
    provider = AkShareDataProvider()
    
    test_symbol = '600519'  # 贵州茅台
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    print(f"分析标的: {stock_names.get(test_symbol, test_symbol)} ({test_symbol})")
    print(f"分析区间: {start_date} 至 {end_date}")
    print()
    
    # 获取数据
    df = provider.get_daily_data(test_symbol, start_date=start_date, end_date=end_date)
    print(f"成功获取 {len(df)} 条K线数据")
    print(f"最新价格: {df.iloc[-1]['close']:.2f} 元")
    print()
    
    # 初始化策略
    strategies = [
        ("双均线交叉", MovingAverageCrossoverStrategy(fast_period=5, slow_period=20)),
        ("RSI超买超卖", RSIStrategy(rsi_period=14, oversold=30, overbought=70)),
        ("布林带突破", BollingerBandsStrategy(period=20, std_dev=2.0)),
        ("MACD趋势", MACDStrategy(fast_period=12, slow_period=26, signal_period=9)),
    ]
    
    print("🎯 各策略信号分析:")
    print("-" * 80)
    
    signals_summary = []
    
    for name, strategy in strategies:
        try:
            # 准备数据
            data = df.copy()
            data = strategy.prepare_data(data)
            signals = strategy.generate_signals(data)
            
            latest_signal = signals.iloc[-1]['signal']
            latest_date = signals.iloc[-1]['date']
            
            # 信号翻译
            if latest_signal == 1:
                signal_text = "🟢 看多"
                signal_score = 1
            elif latest_signal == -1:
                signal_text = "🔴 看空"
                signal_score = -1
            else:
                signal_text = "🟡 观望"
                signal_score = 0
            
            # 统计历史胜率
            signal_changes = signals[signals['signal'] != signals['signal'].shift(1)]
            if len(signal_changes) > 1:
                print(f"  {name:<15}: {signal_text:<10} (最新信号日: {latest_date})")
                signals_summary.append(signal_score)
            else:
                print(f"  {name:<15}: {signal_text:<10}")
                signals_summary.append(signal_score)
                
        except Exception as e:
            print(f"  {name:<15}: ❌ 计算失败 ({str(e)[:30]})")
    
    print()
    
    # 信号汇总
    bullish_count = sum(1 for s in signals_summary if s == 1)
    bearish_count = sum(1 for s in signals_summary if s == -1)
    neutral_count = sum(1 for s in signals_summary if s == 0)
    
    print("📊 信号投票汇总:")
    print(f"  🟢 看多策略数: {bullish_count}")
    print(f"  🟡 观望策略数: {neutral_count}")
    print(f"  🔴 看空策略数: {bearish_count}")
    print()
    
    if bullish_count > bearish_count * 2:
        print("  🎯 综合结论: 强烈看多，信号一致性高")
    elif bullish_count > bearish_count:
        print("  🎯 综合结论: 偏多，可以考虑建仓")
    elif bearish_count > bullish_count * 2:
        print("  🎯 综合结论: 强烈看空，建议回避")
    elif bearish_count > bullish_count:
        print("  🎯 综合结论: 偏空，谨慎操作")
    else:
        print("  🎯 综合结论: 多空平衡，建议观望")
    
    print()
    print("✅ 策略信号生成演示完成！")
    
except Exception as e:
    print(f"❌ 策略信号生成演示出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 4. 回测系统演示
# =============================================================================
print("📊 【4/5】历史回测系统 - 验证策略有效性")
print("-" * 80)

try:
    from src.backtesting.engine import BacktestEngine
    from src.strategies.moving_average_crossover import MovingAverageCrossoverStrategy
    from src.risk.manager import RiskManager
    from src.analytics.performance import PerformanceAnalyzer
    
    test_symbol = '600519'
    test_symbol_name = stock_names.get(test_symbol, test_symbol)
    
    # 回测参数
    initial_capital = 100000  # 初始资金 10万
    commission_rate = 0.0003  # 万三手续费
    slippage = 0.001  # 0.1%滑点
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')  # 回测3年
    
    print(f"回测标的: {test_symbol_name} ({test_symbol})")
    print(f"回测区间: {start_date} 至 {end_date}")
    print(f"初始资金: {initial_capital:,} 元")
    print(f"手续费率: {commission_rate*100:.2f}%")
    print(f"滑点设置: {slippage*100:.1f}%")
    print()
    
    # 获取数据
    provider = AkShareDataProvider()
    df = provider.get_daily_data(test_symbol, start_date=start_date, end_date=end_date)
    print(f"成功获取 {len(df)} 条K线数据")
    
    if len(df) < 100:
        print("⚠️ 数据量不足，跳过回测演示")
    else:
        # 初始化策略
        strategy = MovingAverageCrossoverStrategy(fast_period=5, slow_period=20)
        
        # 初始化风险管理
        risk_manager = RiskManager(
            max_position_size=0.3,  # 单票最大仓位30%
            max_daily_loss=0.05,    # 单日最大亏损5%
            max_drawdown=0.20,      # 最大回撤20%
        )
        
        # 运行回测
        print("正在运行回测...")
        engine = BacktestEngine(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            slippage=slippage,
        )
        
        result = engine.run(df, strategy, risk_manager)
        
        # 绩效分析
        analyzer = PerformanceAnalyzer()
        metrics = analyzer.calculate_metrics(result)
        
        print()
        print("📈 回测绩效结果:")
        print("-" * 80)
        print(f"  期初资金: {metrics['initial_capital']:>15,.2f} 元")
        print(f"  期末资金: {metrics['final_value']:>15,.2f} 元")
        print(f"  累计收益率: {metrics['total_return']*100:>13.2f} %")
        print(f"  年化收益率: {metrics['annual_return']*100:>13.2f} %")
        print(f"  年化波动率: {metrics['volatility']*100:>13.2f} %")
        print(f"  夏普比率: {metrics['sharpe_ratio']:>15.2f}")
        print(f"  最大回撤: {metrics['max_drawdown']*100:>13.2f} %")
        print(f"  卡玛比率: {metrics['calmar_ratio']:>15.2f}")
        print(f"  索提诺比率: {metrics['sortino_ratio']:>13.2f}")
        print(f"  胜率: {metrics['win_rate']*100:>15.2f} %")
        print(f"  盈亏比: {metrics['profit_loss_ratio']:>15.2f}")
        print(f"  交易次数: {metrics['total_trades']:>13} 次")
        
        print()
        
        # 策略评价
        if metrics['sharpe_ratio'] > 1.5:
            sharpe_eval = "🌟 优秀！风险调整后收益很高"
        elif metrics['sharpe_ratio'] > 1.0:
            sharpe_eval = "✅ 良好！风险调整后收益不错"
        elif metrics['sharpe_ratio'] > 0.5:
            sharpe_eval = "⚠️ 一般，还有优化空间"
        else:
            sharpe_eval = "❌ 较差，需要调整策略参数"
        
        if metrics['max_drawdown'] < 0.15:
            dd_eval = "🌟 优秀！回撤控制很好"
        elif metrics['max_drawdown'] < 0.25:
            dd_eval = "✅ 良好！回撤适中"
        else:
            dd_eval = "⚠️ 较大，注意风险"
        
        print(f"  夏普比率评价: {sharpe_eval}")
        print(f"  最大回撤评价: {dd_eval}")
        
        print()
        print("✅ 回测系统演示完成！")
    
except Exception as e:
    print(f"❌ 回测系统演示出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 5. 风险控制与仓位计算演示
# =============================================================================
print("🛡️ 【5/5】风险控制与智能仓位计算")
print("-" * 80)

try:
    print("📊 智能仓位计算器")
    print("根据波动率、信号置信度、风险偏好计算建议仓位")
    print()
    
    test_symbol = '600519'
    current_price = 1700  # 假设价格
    atr_value = 45  # 20日ATR
    signal_confidence = 0.8  # 80%的信号置信度
    total_capital = 100000  # 总资金
    
    print(f"标的: {stock_names.get(test_symbol, test_symbol)}")
    print(f"当前价格: {current_price:.2f} 元")
    print(f"20日ATR: {atr_value:.2f} 元")
    print(f"ATR波动率: {atr_value/current_price*100:.2f}%")
    print(f"信号置信度: {signal_confidence*100:.0f}%")
    print(f"总资金: {total_capital:,} 元")
    print()
    
    # 三种风险偏好的仓位建议
    risk_profiles = [
        ("保守型", 0.01),  # 预期单笔风险1%
        ("平衡型", 0.02),  # 预期单笔风险2%
        ("激进型", 0.03),  # 预期单笔风险3%
    ]
    
    print("💡 不同风险偏好下的仓位建议:")
    print("-" * 80)
    print(f"{'风险偏好':<10} {'目标仓位':<15} {'建议股数':<12} {'止损价':<12} {'止盈价':<12} {'盈亏比':<10}")
    print("-" * 80)
    
    for profile_name, risk_per_trade in risk_profiles:
        # 波动率调整仓位
        risk_amount = total_capital * risk_per_trade
        position_shares = int(risk_amount / atr_value / 100) * 100  # 取整到百股
        position_value = position_shares * current_price
        position_pct = position_value / total_capital
        
        # 置信度调整
        adjusted_shares = int(position_shares * signal_confidence / 100) * 100
        adjusted_value = adjusted_shares * current_price
        adjusted_pct = adjusted_value / total_capital
        
        # 止损止盈（基于ATR）
        stop_loss = current_price - 2 * atr_value  # 2倍ATR止损
        take_profit = current_price + 3.5 * atr_value  # 3.5倍ATR止盈
        risk_reward_ratio = (take_profit - current_price) / (current_price - stop_loss)
        
        print(f"{profile_name:<10} "
              f"{adjusted_value:>10,.0f}元 ({adjusted_pct*100:.0f}%) "
              f"{adjusted_shares:>8}股 "
              f"{stop_loss:>10.2f} "
              f"{take_profit:>10.2f} "
              f"{risk_reward_ratio:.2f}:1")
    
    print()
    print("💡 风险管理建议:")
    print("  • 单笔交易风险控制在总资金的1%-3%之间")
    print("  • 波动率越高，仓位越小；反之亦然")
    print("  • 信号置信度越高，可以适当增加仓位")
    print("  • 盈亏比至少要大于1.5:1才值得交易")
    print("  • 永远不要满仓单只股票，建议单票不超过30%")
    
    print()
    print("✅ 风险控制与仓位计算演示完成！")
    
except Exception as e:
    print(f"❌ 风险控制与仓位计算演示出错: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# 总结
# =============================================================================
print("=" * 80)
print("🎉 Lianghua 量化决策系统 - 所有功能演示完成！")
print("=" * 80)
print()
print("📋 已完成的演示模块:")
print("  ✅ 市场温度计 - 大盘整体监测")
print("  ✅ 多维度股票评分 - 智能选股辅助")
print("  ✅ 策略信号生成 - 多策略信号聚合")
print("  ✅ 历史回测系统 - 验证策略有效性")
print("  ✅ 风险控制与仓位计算 - 智能仓位建议")
print()
print("💡 系统核心价值:")
print("  • 帮你客观分析市场，避免情绪化决策")
print("  • 多维度评分，发现被低估/高估的股票")
print("  • 多策略交叉验证，提高信号可靠性")
print("  • 历史回测，用数据验证你的交易想法")
print("  • 科学的仓位管理，控制风险，放大收益")
print()
print("📚 下一步建议:")
print("  1. 尝试用更多股票测试评分系统")
print("  2. 回测不同策略参数，找到最适合的参数组合")
print("  3. 建立自己的股票池，每天运行评分和信号分析")
print("  4. 坚持风险控制，永远不要忽视止损")
print()
print("=" * 80)
print("🌟 Lianghua - 让投资决策更科学、更理性")
print("=" * 80)
