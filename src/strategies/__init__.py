"""
Base Strategy class that all strategies inherit from
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict
from ..data.bar_data import BarData
from .base import Signal


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, params: Dict = None):
        self.params = params or {}
        self.name = self.__class__.__name__
        self.initialized = False
        
    @abstractmethod
    def initialize(self) -> None:
        """
        策略初始化
        在回测/实盘开始前调用，用于计算初始指标
        """
        pass
    
    @abstractmethod
    def on_bar(self, bar: BarData) -> Optional[Signal]:
        """
        处理每个K线，生成信号
        
        参数:
            bar: 当前K线数据
            
        返回:
            交易信号或None（不交易）
        """
        pass
    
    def on_order(self, order) -> None:
        """
        订单状态更新回调
        
        参数:
            order: 订单对象
        """
        pass
    
    def on_trade(self, trade) -> None:
        """
        成交回调
        
        参数:
            trade: 成交对象
        """
        pass
    
    def get_parameters(self) -> Dict:
        """获取策略参数"""
        return self.params
    
    def set_parameters(self, params: Dict) -> None:
        """设置策略参数"""
        self.params.update(params)
    
    @property
    def description(self) -> str:
        """策略描述"""
        return self.__doc__ or "No description"
