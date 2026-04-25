"""
Performance analysis - 绩效分析
"""
import numpy as np
import pandas as pd
from typing import Dict
from ..execution.portfolio import Portfolio, Trade


class PerformanceAnalyzer:
    """绩效分析器"""
    
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        
    def calculate_metrics(self) -> Dict:
        """计算所有绩效指标"""
        equity_curve = self.portfolio.get_equity_curve()
        
        if equity_curve.empty:
            return {}
        
        total_value = equity_curve['total_value']
        initial_value = self.portfolio.initial_cash
        final_value = total_value.iloc[-1]
        
        # 收益率
        total_return = (final_value - initial_value) / initial_value
        
        # 年化收益率
        n_days = len(equity_curve)
        if n_days < 1:
            annual_return = 0
        else:
            annual_return = (1 + total_return) ** (252 / n_days) - 1
        
        # 日收益率
        daily_returns = total_value.pct_change().dropna()
        
        # 波动率（年化）
        volatility = daily_returns.std() * np.sqrt(252)
        
        # 夏普比率（假设无风险利率0）
        if volatility > 0:
            sharpe_ratio = annual_return / volatility
        else:
            sharpe_ratio = 0
        
        # 最大回撤
        drawdown = self._calculate_drawdown(total_value)
        max_drawdown = drawdown.min()
        
        # 卡玛比率
        if max_drawdown < 0 and abs(max_drawdown) > 1e-8:
            calmar_ratio = annual_return / abs(max_drawdown)
        else:
            calmar_ratio = 0
        
        # 索提诺比率
        downside_returns = daily_returns[daily_returns < 0]
        if len(downside_returns) > 0:
            downside_vol = downside_returns.std() * np.sqrt(252)
            if downside_vol > 0:
                sortino_ratio = annual_return / downside_vol
            else:
                sortino_ratio = 0
        else:
            sortino_ratio = 0
        
        # 交易统计
        trades_df = self.get_trades_df()
        total_trades = len(trades_df)
        win_rate = 0
        profit_factor = 0
        avg_profit_per_trade = 0
        
        if total_trades > 0:
            # 只统计卖出交易计算盈亏
            sells = trades_df[trades_df['direction'] == 'SELL']
            if len(sells) > 0:
                # 简化：假设买入后卖出，计算盈亏
                # 实际更准确的方法是配对交易
                wins = len(sells[sells['pnl'] > 0])
                win_rate = wins / len(sells)
                
                gross_profit = sells[sells['pnl'] > 0]['pnl'].sum()
                gross_loss = abs(sells[sells['pnl'] < 0]['pnl'].sum())
                if gross_loss > 0:
                    profit_factor = gross_profit / gross_loss
                avg_profit_per_trade = sells['pnl'].mean()
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_profit_per_trade': avg_profit_per_trade
        }
    
    def _calculate_drawdown(self, equity: pd.Series) -> pd.Series:
        """计算回撤序列"""
        rolling_max = equity.expanding().max()
        drawdown = (equity - rolling_max) / rolling_max
        return drawdown
    
    def get_trades_df(self) -> pd.DataFrame:
        """获取交易记录DataFrame"""
        trades = self.portfolio.trade_history
        if not trades:
            return pd.DataFrame()
        
        data = []
        for trade in trades:
            # 简化计算，实际需要配对买入卖出
            # 这里只记录基本信息
            pnl = 0
            if trade.direction == 'SELL':
                # 估算pnl
                pnl = (trade.price - trade.commission) * trade.quantity
                # 减去成本（简化估算）
                avg_cost = 0  # 需要从position获取
                if trade.order_id in self.portfolio.positions:
                    pass
            
            data.append({
                'trade_id': trade.trade_id,
                'symbol': trade.symbol,
                'direction': trade.direction.value,
                'quantity': trade.quantity,
                'price': trade.price,
                'commission': trade.commission,
                'timestamp': trade.timestamp,
                'pnl': pnl,
                'strategy': trade.strategy_name
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('timestamp')
        return df
    
    def plot_equity_curve(self, save_path: str = None):
        """绘制净值曲线"""
        import matplotlib.pyplot as plt
        equity_curve = self.portfolio.get_equity_curve()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        
        # 净值曲线
        total_value = equity_curve['total_value']
        ax1.plot(equity_curve.index, total_value, label='Portfolio Value', linewidth=2)
        ax1.set_title('Equity Curve', fontsize=14)
        ax1.set_ylabel('Value')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 回撤
        drawdown = self._calculate_drawdown(total_value)
        ax2.fill_between(equity_curve.index, drawdown * 100, 0, color='red', alpha=0.3)
        ax2.set_title('Drawdown', fontsize=14)
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_monthly_returns(self, save_path: str = None):
        """绘制月度收益热力图"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        equity_curve = self.portfolio.get_equity_curve()
        
        if equity_curve.empty:
            return
        
        daily_returns = equity_curve['total_value'].pct_change().dropna()
        monthly_returns = daily_returns.resample('M').sum()
        
        # 重新整理成行（年）x 列（月）
        monthly_table = monthly_returns.groupby([
            monthly_returns.index.year,
            monthly_returns.index.month
        ]).first().unstack()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(monthly_table * 100, annot=True, fmt=".2f", 
                    cmap="RdYlGn", center=0, ax=ax)
        ax.set_title('Monthly Returns (%)', fontsize=14)
        ax.set_xlabel('Month')
        ax.set_ylabel('Year')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
