#!/usr/bin/env python3
"""
Run backtest from command line
"""
import click
import os
from datetime import datetime
import pandas as pd

from src.config.loader import load_config, get_risk_config
from src.data.base import BaseDataProvider
from src.data.tushare_provider import TushareDataProvider
from src.data.akshare_provider import AkShareDataProvider
from src.strategies.registry import get_strategy, list_strategies
from src.backtesting.engine import BacktestEngine


def get_data_provider(config) -> BaseDataProvider:
    """根据配置获取数据源"""
    provider_name = config.get('data.provider', 'tushare')
    api_key = config.get('data.api_key')
    
    if provider_name == 'tushare':
        return TushareDataProvider(api_key=api_key)
    elif provider_name == 'akshare':
        return AkShareDataProvider()
    else:
        raise ValueError(f"Unknown data provider: {provider_name}")


@click.command()
@click.option('--config', '-c', default='config/config.yaml', help='Config file path')
@click.option('--strategy', '-s', help='Strategy name')
@click.option('--symbols', '-t', multiple=True, help='Symbols to backtest')
@click.option('--start', '-S', default='2020-01-01', help='Start date YYYY-MM-DD')
@click.option('--end', '-e', default='2024-01-01', help='End date YYYY-MM-DD')
@click.option('--output', '-o', default='results', help='Output directory')
@click.option('--list-strategies', '-l', is_flag=True, help='List available strategies')
def main(config, strategy, symbols, start, end, output, list_strategies):
    """Run backtest for a strategy"""
    
    if list_strategies:
        print("\nAvailable strategies:")
        for s in list_strategies():
            print(f"  - {s}")
        print()
        return
    
    # 加载配置
    if not os.path.exists(config):
        print(f"Config file {config} not found. Use --config to specify path.")
        print("Copy config/config.yaml.example to config/config.yaml and edit it.")
        return
    
    cfg = load_config(config)
    
    # 获取数据提供者
    data_provider = get_data_provider(cfg)
    
    # 获取策略
    if not strategy:
        strategy = cfg.get('strategy.name')
    if not symbols:
        symbols = cfg.get('portfolio.symbols', [])
    
    strategy_params = cfg.get('strategy.params', {})
    strategy_obj = get_strategy(strategy, strategy_params)
    
    # 解析日期
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    
    # 获取风险配置
    risk_config = get_risk_config(cfg)
    
    # 获取执行配置
    commission_rate = cfg.get('execution.commission_rate', 0.0003)
    min_commission = cfg.get('execution.min_commission', 5)
    slippage_pct = cfg.get('execution.slippage_pct', 0.001)
    initial_cash = cfg.get('portfolio.initial_cash', 1000000)
    
    print(f"\nStarting backtest:")
    print(f"  Strategy: {strategy}")
    print(f"  Symbols: {symbols}")
    print(f"  Period: {start_date.date()} to {end_date.date()}")
    print(f"  Initial Cash: {initial_cash:,.2f}\n")
    
    # 创建回测引擎并运行
    engine = BacktestEngine(
        data_provider=data_provider,
        strategy=strategy_obj,
        initial_cash=initial_cash,
        commission_rate=commission_rate,
        min_commission=min_commission,
        slippage_pct=slippage_pct,
        risk_config=risk_config
    )
    
    results = engine.run(
        symbols=list(symbols),
        start_date=start_date,
        end_date=end_date
    )
    
    # 打印结果
    engine.print_results()
    
    # 保存结果
    os.makedirs(output, exist_ok=True)
    
    # 保存净值曲线
    equity_df = results['equity_curve']
    equity_df.to_csv(os.path.join(output, f'{strategy}_equity.csv'))
    
    # 保存交易记录
    trades_df = results['trades']
    if trades_df is not None and not trades_df.empty:
        trades_df.to_csv(os.path.join(output, f'{strategy}_trades.csv'), index=False)
    
    # 保存指标
    metrics = results['metrics']
    pd.Series(metrics).to_csv(os.path.join(output, f'{strategy}_metrics.csv'))
    
    # 绘图
    try:
        from src.analytics.performance import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(results['portfolio'])
        analyzer.plot_equity_curve(save_path=os.path.join(output, f'{strategy}_equity.png'))
        print(f"Plots saved to {output}/\n")
    except Exception as e:
        print(f"Could not generate plot: {e}\n")
    
    print(f"Results saved to {output}/")


if __name__ == '__main__':
    main()
