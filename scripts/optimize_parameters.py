#!/usr/bin/env python3
"""
Parameter optimization for strategies
"""
import click
import os
from datetime import datetime
from itertools import product
import pandas as pd
import numpy as np
from typing import List, Dict

from src.config.loader import load_config, get_risk_config
from src.data.base import BaseDataProvider
from src.data.tushare_provider import TushareDataProvider
from src.data.akshare_provider import AkShareDataProvider
from src.strategies.registry import get_strategy
from src.backtesting.engine import BacktestEngine


def get_data_provider(config) -> BaseDataProvider:
    provider_name = config.get('data.provider', 'tushare')
    api_key = config.get('data.api_key')
    
    if provider_name == 'tushare':
        return TushareDataProvider(api_key=api_key)
    elif provider_name == 'akshare':
        return AkShareDataProvider()
    else:
        raise ValueError(f"Unknown data provider: {provider_name}")


def grid_search(
    strategy_name: str,
    param_grid: Dict,
    data_provider,
    symbols: List[str],
    start_date: datetime,
    end_date: datetime,
    initial_cash: float,
    commission_rate: float,
    risk_config,
    metric: str = 'sharpe_ratio'
) -> pd.DataFrame:
    """网格搜索参数优化"""
    
    # 生成所有参数组合
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    
    results = []
    
    for combo in product(*values):
        params = dict(zip(keys, combo))
        print(f"\nTesting parameters: {params}")
        
        strategy = get_strategy(strategy_name, params)
        engine = BacktestEngine(
            data_provider=data_provider,
            strategy=strategy,
            initial_cash=initial_cash,
            commission_rate=commission_rate,
            risk_config=risk_config
        )
        
        try:
            result = engine.run(symbols, start_date, end_date)
            metrics = result['metrics']
            metrics.update(params)
            results.append(metrics)
            print(f"  {metric}: {metrics.get(metric, 0):.4f}")
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    df = pd.DataFrame(results)
    
    # 按目标指标排序
    if metric in ['max_drawdown', 'drawdown']:
        df = df.sort_values(metric, ascending=True)
    else:
        df = df.sort_values(metric, ascending=False)
    
    return df


@click.command()
@click.option('--config', '-c', default='config/config.yaml', help='Config file')
@click.option('--strategy', '-s', help='Strategy name')
@click.option('--symbols', '-t', multiple=True, required=True, help='Symbols')
@click.option('--start', '-S', default='2020-01-01', help='Start date')
@click.option('--end', '-e', default='2024-01-01', help='End date')
@click.option('--metric', '-m', default='sharpe_ratio', help='Metric to optimize')
@click.option('--output', '-o', default='results/grid_search.csv', help='Output file')
def main(config, strategy, symbols, start, end, metric, output):
    """Parameter grid search optimization"""
    
    cfg = load_config(config)
    data_provider = get_data_provider(cfg)
    
    if not strategy:
        strategy = cfg.get('strategy.name')
    
    # 定义参数网格
    # 需要根据策略修改，这里是示例
    if strategy == 'MovingAverageCrossover':
        param_grid = {
            'fast_period': [3, 5, 8, 10],
            'slow_period': [15, 20, 25, 30]
        }
    elif strategy == 'RSIStrategy':
        param_grid = {
            'period': [6, 9, 14, 21],
            'oversold': [20, 25, 30, 35],
            'overbought': [65, 70, 75, 80]
        }
    elif strategy == 'BollingerBands':
        param_grid = {
            'period': [10, 20, 30],
            'num_std': [1.5, 2.0, 2.5]
        }
    else:
        # 默认参数网格
        param_grid = cfg.get('optimization.param_grid', {})
        if not param_grid:
            print(f"Please define param_grid for strategy {strategy}")
            return
    
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    initial_cash = cfg.get('portfolio.initial_cash', 1000000)
    commission_rate = cfg.get('execution.commission_rate', 0.0003)
    risk_config = get_risk_config(cfg)
    
    print(f"\nStarting grid search:")
    print(f"  Strategy: {strategy}")
    print(f"  Parameters: {param_grid}")
    print(f"  Optimizing for: {metric}")
    print(f"  Symbols: {symbols}")
    print(f"  Period: {start_date.date()} to {end_date.date()}\n")
    
    results_df = grid_search(
        strategy,
        param_grid,
        data_provider,
        list(symbols),
        start_date,
        end_date,
        initial_cash,
        commission_rate,
        risk_config,
        metric
    )
    
    # 保存结果
    os.makedirs(os.path.dirname(output), exist_ok=True)
    results_df.to_csv(output, index=False)
    
    print(f"\n{'='*60}")
    print(f"Top 5 parameters by {metric}:")
    print(f"{'='*60}")
    print(results_df.head(5).to_string())
    print(f"\nFull results saved to {output}")
    
    best_params = results_df.iloc[0].to_dict()
    print(f"\nBest parameters:")
    for k, v in best_params.items():
        if k in param_grid:
            print(f"  {k}: {v}")
    print(f"Best {metric}: {best_params.get(metric, 0):.4f}")


if __name__ == '__main__':
    main()
