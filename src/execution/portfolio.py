"""
Portfolio - 组合管理
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from .order import Trade, OrderDirection


@dataclass
class Position:
    """单个持仓"""
    symbol: str
    quantity: float = 0.0
    avg_cost: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    
    @property
    def cost_basis(self) -> float:
        """总成本"""
        return self.quantity * self.avg_cost
    
    def add_trade(self, trade: Trade) -> None:
        """添加成交"""
        if trade.is_buy:
            # 买入，增加持仓
            new_quantity = self.quantity + trade.quantity
            new_cost = (self.cost_basis + trade.notional + trade.commission)
            if new_quantity > 0:
                self.avg_cost = new_cost / new_quantity
            self.quantity = new_quantity
        else:
            # 卖出，减少持仓
            self.quantity -= trade.quantity
            # avg_cost 保持不变（先进先出简化为平均成本法）
        self.trades.append(trade)
    
    def market_value(self, current_price: float) -> float:
        """市值"""
        return self.quantity * current_price
    
    def unrealized_pnl(self, current_price: float) -> float:
        """未实现盈亏"""
        return (current_price - self.avg_cost) * self.quantity
    
    def unrealized_pnl_pct(self, current_price: float) -> float:
        """未实现盈亏百分比"""
        if self.avg_cost == 0:
            return 0.0
        return (current_price - self.avg_cost) / self.avg_cost


class Portfolio:
    """投资组合"""
    
    def __init__(self, initial_cash: float = 1000000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Trade] = []
        self.daily_values: List[Dict] = []
        
    def get_position(self, symbol: str) -> Position:
        """获取持仓，如果不存在返回空持仓"""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]
    
    def process_trade(self, trade: Trade) -> None:
        """处理成交，更新组合"""
        position = self.get_position(trade.symbol)
        position.add_trade(trade)
        
        # 更新现金
        self.cash += trade.net_amount
        self.trade_history.append(trade)
        
        # 如果持仓为0，可以移除（可选）
        if position.quantity == 0:
            del self.positions[trade.symbol]
    
    def total_market_value(self, current_prices: Dict[str, float]) -> float:
        """总市值"""
        mv = 0.0
        for symbol, position in self.positions.items():
            if symbol in current_prices and position.quantity > 0:
                mv += position.market_value(current_prices[symbol])
        return mv
    
    def total_value(self, current_prices: Dict[str, float]) -> float:
        """总资产"""
        return self.cash + self.total_market_value(current_prices)
    
    def record_daily_value(self, date: datetime, current_prices: Dict[str, float]) -> None:
        """记录每日净值"""
        tv = self.total_value(current_prices)
        self.daily_values.append({
            'date': date,
            'cash': self.cash,
            'total_value': tv,
            'returns': (tv - self.initial_cash) / self.initial_cash
        })
    
    def get_equity_curve(self) -> pd.DataFrame:
        """获取净值曲线"""
        df = pd.DataFrame(self.daily_values)
        if not df.empty:
            df = df.sort_values('date')
            df = df.set_index('date')
        return df
    
    @property
    def total_trades(self) -> int:
        return len(self.trade_history)
    
    @property
    def current_positions(self) -> Dict[str, Position]:
        """返回当前非零持仓"""
        return {s: p for s, p in self.positions.items() if p.quantity > 0}
    
    def position_weight(self, symbol: str, current_prices: Dict[str, float]) -> float:
        """获取当前权重"""
        total = self.total_value(current_prices)
        if total == 0:
            return 0.0
        position = self.get_position(symbol)
        if position.quantity == 0:
            return 0.0
        mv = position.market_value(current_prices.get(symbol, position.avg_cost))
        return mv / total
