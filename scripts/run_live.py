#!/usr/bin/env python3
"""
Run live trading
"""
import time
import schedule
import yaml
import structlog
from datetime import datetime

from src.config.loader import load_config, get_risk_config
from src.data.base import BaseDataProvider
from src.data.tushare_provider import TushareDataProvider
from src.data.akshare_provider import AkShareDataProvider
from src.strategies.registry import get_strategy
from src.risk.manager import RiskManager
from src.execution.simulation import SimulationExecutor
# from src.execution.xtp import XTPExecutor  # 实际券商接口需要时启用


logger = structlog.get_logger()


def get_data_provider(config):
    """获取数据源"""
    provider_name = config.get('data.provider', 'tushare')
    api_key = config.get('data.api_key')
    
    if provider_name == 'tushare':
        return TushareDataProvider(api_key=api_key)
    elif provider_name == 'akshare':
        return AkShareDataProvider()
    else:
        raise ValueError(f"Unknown data provider: {provider_name}")


def run_once(config, strategy, data_provider, executor, risk_manager):
    """运行一次策略"""
    logger.info("Running trading job...")
    
    symbols = config.get('portfolio.symbols', [])
    today = datetime.now()
    
    current_prices = {}
    for symbol in symbols:
        quote = data_provider.get_realtime_quote(symbol)
        if quote:
            current_prices[symbol] = quote['price']
            executor.update_current_price(symbol, quote['price'])
    
    account = executor.get_account_info()
    portfolio = executor.get_portfolio()
    
    # 检查风险约束
    total_value = account.total_value
    if not risk_manager.check_total_drawdown(total_value):
        logger.error("Max drawdown exceeded, stopping trading today")
        return False
    
    if not risk_manager.check_daily_loss(total_value, portfolio.initial_cash):
        logger.warning("Daily loss limit exceeded, no new positions")
    
    # 获取最近数据并运行策略
    from src.data.bar_data import BarData
    for symbol in symbols:
        # 获取最近N根K线
        bars = data_provider.get_last_n_bars(symbol, 100, today, 'daily')
        if not bars:
            logger.warning("No data for {symbol}, skipping")
            continue
        
        # 只处理最新的一根
        latest_bar = bars[-1]
        signal = strategy.on_bar(latest_bar)
        
        if signal is None:
            continue
        
        # 风险检查
        allowed, adjusted_qty = risk_manager.check_signal(
            signal, portfolio, current_prices
        )
        
        if not allowed or adjusted_qty <= 0:
            logger.info("Signal rejected by risk manager", 
                       symbol=symbol, reason="position limit")
            continue
        
        signal.quantity = adjusted_qty
        
        # 创建订单并执行
        import uuid
        from src.execution.order import Order, OrderDirection
        order = Order(
            order_id=str(uuid.uuid4())[:8],
            symbol=signal.symbol,
            direction=OrderDirection.BUY if signal.is_buy else OrderDirection.SELL,
            quantity=signal.quantity,
            price=signal.price,
            timestamp=today,
            strategy_name=signal.strategy_name
        )
        
        result = executor.execute_order(order)
        if result.success:
            logger.info("Order executed successfully", 
                       order_id=order.order_id,
                       symbol=symbol,
                       price=signal.price,
                       quantity=adjusted_qty)
            for trade in result.trades:
                strategy.on_trade(trade)
        else:
            logger.error("Order execution failed", 
                        order_id=order.order_id,
                        symbol=symbol,
                        reason=result.message)
    
    # 记录每日净值
    portfolio.record_daily_value(today, current_prices)
    risk_manager.reset_daily()
    
    account_info = executor.get_account_info()
    logger.info("Trading job completed", 
               total_value=account_info.total_value,
               cash=account_info.cash,
               positions=len(account_info.positions))
    
    return True


def main():
    """主函数"""
    import click
    
    @click.command()
    @click.option('--config', '-c', default='config/config.yaml', help='Config file path')
    def run(config_path):
        if not config_path:
            print("Please specify config file with --config")
            return
        
        cfg = load_config(config_path)
        
        # 初始化组件
        data_provider = get_data_provider(cfg)
        strategy_name = cfg.get('strategy.name')
        strategy_params = cfg.get('strategy.params', {})
        strategy = get_strategy(strategy_name, strategy_params)
        strategy.initialize()
        
        initial_cash = cfg.get('portfolio.initial_cash', 1000000)
        commission_rate = cfg.get('execution.commission_rate', 0.0003)
        
        execution_mode = cfg.get('execution.mode', 'backtest')
        if execution_mode == 'live':
            # 这里应该连接实际券商接口
            # executor = XTPExecutor(...)
            executor = SimulationExecutor(
                initial_cash=initial_cash,
                commission_rate=commission_rate
            )
            logger.warning("Using simulation executor for live trading - this is a demo!")
        else:
            executor = SimulationExecutor(
                initial_cash=initial_cash,
                commission_rate=commission_rate
            )
        
        risk_config = get_risk_config(cfg)
        risk_manager = RiskManager(risk_config)
        
        # 定时运行
        interval_minutes = cfg.get('live.interval_minutes', 10)
        logger.info(f"Starting live trading, running every {interval_minutes} minutes")
        
        # 运行一次
        run_once(cfg, strategy, data_provider, executor, risk_manager)
        
        # 设置定时
        schedule.every(interval_minutes).minutes.do(
            run_once, cfg, strategy, data_provider, executor, risk_manager
        )
        
        # 运行循环
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    run()


if __name__ == '__main__':
    main()
