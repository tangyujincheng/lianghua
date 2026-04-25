"""
Strategy registry - maps strategy names to classes
"""
from .base import BaseStrategy
from .moving_average_crossover import MovingAverageCrossover
from .rsi_strategy import RSIStrategy
from .bollinger_bands import BollingerBandsStrategy
from .macd_strategy import MACDStrategy


# 策略注册表
STRATEGY_REGISTRY = {
    'MovingAverageCrossover': MovingAverageCrossover,
    'RSIStrategy': RSIStrategy,
    'BollingerBands': BollingerBandsStrategy,
    'MACDStrategy': MACDStrategy,
}


def get_strategy(strategy_name: str, params: dict = None) -> BaseStrategy:
    """
    根据名称获取策略实例
    
    参数:
        strategy_name: 策略名称
        params: 策略参数
        
    返回:
        策略实例
    """
    if strategy_name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy {strategy_name} not found. "
                        f"Available strategies: {list(STRATEGY_REGISTRY.keys())}")
    
    strategy_class = STRATEGY_REGISTRY[strategy_name]
    return strategy_class(params)


def list_strategies() -> list:
    """列出所有可用策略"""
    return list(STRATEGY_REGISTRY.keys())


def register_strategy(name: str, strategy_class: type) -> None:
    """
    注册新策略
    
    参数:
        name: 策略名称
        strategy_class: 策略类
    """
    if not issubclass(strategy_class, BaseStrategy):
        raise ValueError("Strategy must inherit from BaseStrategy")
    
    STRATEGY_REGISTRY[name] = strategy_class
