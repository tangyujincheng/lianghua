"""
Backtest Engine - 简化版回测引擎
专注于核心回测功能，便于演示和测试
"""
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from ..strategies.base import BaseStrategy


class BacktestEngine:
    """简化版回测引擎"""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
    ):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点比例
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        
        # 回测状态
        self.current_capital = initial_capital
        self.current_position = 0  # 持仓数量
        self.entry_price = 0  # 建仓价格
        
        # 交易记录
        self.trades = []
        
        # 净值曲线
        self.equity_curve = []
        
    def run(self, data: pd.DataFrame, strategy: BaseStrategy, risk_manager=None) -> Dict:
        """
        运行回测
        
        Args:
            data: 包含OHLCV数据的DataFrame
            strategy: 策略实例
            risk_manager: 风险管理器（可选）
            
        Returns:
            回测结果字典
        """
        df = data.copy().reset_index(drop=True)
        
        # 生成策略信号
        signals = strategy.generate_signals(df)
        
        # 按时间顺序遍历
        for i in range(len(df)):
            date = df.iloc[i]['date']
            close = df.iloc[i]['close']
            signal = signals.iloc[i]['signal'] if i < len(signals) else 0
            
            # 执行交易
            if signal == 1 and self.current_position == 0:  # 买入信号，且当前空仓
                # 考虑滑点
                exec_price = close * (1 + self.slippage)
                
                # 计算可买数量（假设可以买部分，实际A股需要整百，但为了简化这里不限制）
                max_shares = int(self.current_capital * (1 - self.commission_rate) / exec_price / 100) * 100
                if max_shares > 0:
                    cost = max_shares * exec_price * (1 + self.commission_rate)
                    self.current_capital -= cost
                    self.current_position = max_shares
                    self.entry_price = exec_price
                    
                    self.trades.append({
                        'date': date,
                        'type': 'buy',
                        'price': exec_price,
                        'quantity': max_shares,
                        'value': cost
                    })
            
            elif signal == -1 and self.current_position > 0:  # 卖出信号，且当前有持仓
                # 考虑滑点
                exec_price = close * (1 - self.slippage)
                revenue = self.current_position * exec_price * (1 - self.commission_rate)
                self.current_capital += revenue
                
                self.trades.append({
                    'date': date,
                    'type': 'sell',
                    'price': exec_price,
                    'quantity': self.current_position,
                    'value': revenue,
                    'profit': revenue - (self.current_position * self.entry_price)
                })
                
                self.current_position = 0
                self.entry_price = 0
            
            # 记录净值
            equity = self.current_capital + self.current_position * close
            self.equity_curve.append({
                'date': date,
                'equity': equity,
                'position': self.current_position,
                'cash': self.current_capital
            })
        
        # 计算回测结果
        result_df = pd.DataFrame(self.equity_curve)
        result_df['returns'] = result_df['equity'].pct_change()
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': result_df['equity'].iloc[-1],
            'equity_curve': result_df,
            'trades': self.trades,
            'total_trades': len([t for t in self.trades if t['type'] == 'buy'])
        }
