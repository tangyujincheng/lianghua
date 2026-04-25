"""
Backtest simulation executor - 回测模拟执行器
"""
import uuid
from datetime import datetime
from typing import List
from .base import BaseExecutor, AccountInfo, ExecutionResult
from .order import Order, Trade, OrderStatus, OrderDirection
from .portfolio import Portfolio


class SimulationExecutor(BaseExecutor):
    """回测模拟执行器"""
    
    def __init__(
        self,
        initial_cash: float = 1000000,
        commission_rate: float = 0.0003,
        min_commission: float = 5.0,
        slippage_pct: float = 0.001
    ):
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.slippage_pct = slippage_pct
        self.current_prices = {}  # symbol -> current price
        self.pending_orders: List[Order] = []
        
    def calculate_commission(self, notional: float) -> float:
        """计算佣金"""
        commission = notional * self.commission_rate
        return max(commission, self.min_commission) if commission > 0 else 0
    
    def apply_slippage(self, price: float, is_buy: bool) -> float:
        """应用滑点"""
        if is_buy:
            # 买入滑点向上
            return price * (1 + self.slippage_pct)
        else:
            # 卖出滑点向下
            return price * (1 - self.slippage_pct)
    
    def execute_order(self, order: Order, current_price: float = None) -> ExecutionResult:
        """模拟执行订单，假设全成交"""
        # 使用当前价格，如果没提供用订单价格
        fill_price = current_price if current_price is not None else order.price
        
        # 如果仍然没有价格，报错
        if fill_price is None:
            return ExecutionResult(
                success=False,
                order=order,
                trades=[],
                message="No price available for execution"
            )
        
        # 应用滑点
        fill_price = self.apply_slippage(fill_price, order.is_buy)
        
        # 计算成交金额和佣金
        quantity = order.quantity
        notional = fill_price * quantity
        commission = self.calculate_commission(notional)
        
        # 检查现金够不够买入
        if order.is_buy:
            required_cash = notional + commission
            if self.portfolio.cash < required_cash:
                # 现金不够，拒绝
                order.status = OrderStatus.REJECTED
                return ExecutionResult(
                    success=False,
                    order=order,
                    trades=[],
                    message="Insufficient cash"
                )
        
        # 创建成交记录
        trade = Trade(
            trade_id=str(uuid.uuid4())[:8],
            order_id=order.order_id,
            symbol=order.symbol,
            direction=order.direction,
            quantity=quantity,
            price=fill_price,
            commission=commission,
            timestamp=datetime.now(),
            strategy_name=order.strategy_name
        )
        
        # 更新组合
        self.portfolio.process_trade(trade)
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = quantity
        order.filled_avg_price = fill_price
        
        return ExecutionResult(
            success=True,
            order=order,
            trades=[trade],
            message="Filled completely"
        )
    
    def get_account_info(self) -> AccountInfo:
        """获取账户信息"""
        positions = {
            symbol: pos.quantity
            for symbol, pos in self.portfolio.current_positions.items()
        }
        
        # 计算总资产
        total_value = self.portfolio.total_value(self.current_prices)
        
        return AccountInfo(
            cash=self.portfolio.cash,
            total_value=total_value,
            available_cash=self.portfolio.cash,
            positions=positions
        )
    
    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        for i, order in enumerate(self.pending_orders):
            if order.order_id == order_id:
                order.status = OrderStatus.CANCELLED
                self.pending_orders.pop(i)
                return True
        return False
    
    def update_current_price(self, symbol: str, price: float) -> None:
        """更新当前价格"""
        self.current_prices[symbol] = price
    
    def get_portfolio(self) -> Portfolio:
        """获取组合"""
        return self.portfolio
