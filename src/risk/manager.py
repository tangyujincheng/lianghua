"""
Risk Management - 风险管理
"""
from dataclasses import dataclass
from typing import Optional, Dict
from ..strategies.base import Signal
from ..execution.portfolio import Portfolio
from ..execution.base import AccountInfo


@dataclass
class RiskConfig:
    """风险配置"""
    max_single_position: float = 0.1    # 单票最大仓位 (10%)
    max_daily_loss: float = 0.05       # 单日最大亏损 (5%)
    max_total_drawdown: float = 0.2    # 总最大回撤 (20%)
    target_volatility: Optional[float] = 0.15  # 目标年化波动率
    position_scaling: str = "fixed"    # fixed, volatility, equal
    use_stop_loss: bool = True
    stop_loss_atr_multiple: float = 2.0
    use_take_profit: bool = False
    take_profit_pct: float = 0.10


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.peak_value = None
        self.daily_pnl = 0.0
        self.last_date = None
        
    def check_signal(
        self,
        signal: Signal,
        portfolio: Portfolio,
        current_prices: Dict[str, float],
        current_volatility: Optional[Dict[str, float]] = None
    ) -> tuple[bool, float]:
        """
        检查信号是否符合风险规则
        
        返回:
            (allowed: bool, adjusted_quantity: float)
        """
        total_value = portfolio.total_value(current_prices)
        
        if signal.is_buy:
            # 计算目标仓位大小
            if self.config.position_scaling == "fixed":
                # 固定仓位比例
                target_value = total_value * self.config.max_single_position
                quantity = int(target_value / signal.price)
            elif self.config.position_scaling == "volatility":
                # 波动率调整仓位
                vol = current_volatility.get(signal.symbol, 0.15) if current_volatility else 0.15
                if vol > 0 and self.config.target_volatility:
                    scaling = self.config.target_volatility / (vol * (252 ** 0.5))
                    target_value = total_value * self.config.max_single_position * scaling
                    quantity = int(target_value / signal.price)
                else:
                    target_value = total_value * self.config.max_single_position
                    quantity = int(target_value / signal.price)
            elif self.config.position_scaling == "equal":
                # 等权分配
                n_symbols = len(current_prices)
                target_value = total_value / max(n_symbols, 1)
                quantity = int(target_value / signal.price)
            else:
                quantity = signal.quantity
            
            # 检查不超过最大单票仓位
            current_position = portfolio.get_position(signal.symbol).quantity
            current_value = current_position * signal.price
            new_value = current_value + quantity * signal.price
            new_weight = new_value / total_value if total_value > 0 else 0
            
            if new_weight > self.config.max_single_position * 1.05:  # 5%容差
                # 调整数量不超限
                max_value = total_value * self.config.max_single_position
                adjusted_quantity = int((max_value - current_value) / signal.price)
                if adjusted_quantity <= 0:
                    return False, 0
                quantity = adjusted_quantity
            
            # 检查现金够不够
            required_cash = quantity * signal.price * (1 + 0.001)  # 预留滑点佣金
            if required_cash > portfolio.cash:
                quantity = int(portfolio.cash / (signal.price * (1 + 0.001)))
                if quantity <= 0:
                    return False, 0
            
            return True, quantity
        
        else:  # SELL
            # 卖出总是允许
            return True, signal.quantity
    
    def check_daily_loss(self, current_value: float, previous_close: float) -> bool:
        """检查单日亏损是否超限"""
        if previous_close <= 0:
            return True
        
        daily_pnl_pct = (current_value - previous_close) / previous_close
        self.daily_pnl = daily_pnl_pct
        
        if daily_pnl_pct < -self.config.max_daily_loss:
            # 单日亏损超限，停止新开仓
            return False
        
        return True
    
    def check_total_drawdown(self, current_value: float) -> bool:
        """检查总回撤是否超限"""
        if self.peak_value is None or current_value > self.peak_value:
            self.peak_value = current_value
            return True
        
        drawdown = (self.peak_value - current_value) / self.peak_value
        
        if drawdown > self.config.max_total_drawdown:
            # 回撤超限，停止交易
            return False
        
        return True
    
    def calculate_stop_loss_price(
        self,
        entry_price: float,
        atr: float
    ) -> float:
        """计算止损价格"""
        if self.config.use_stop_loss:
            return entry_price - self.config.stop_loss_atr_multiple * atr
        return 0.0
    
    def calculate_take_profit_price(
        self,
        entry_price: float
    ) -> float:
        """计算止盈价格"""
        if self.config.use_take_profit:
            return entry_price * (1 + self.config.take_profit_pct)
        return float('inf')
    
    def reset_daily(self):
        """重置每日统计"""
        self.daily_pnl = 0.0
