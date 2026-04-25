# Strategy Development Guide

## 如何创建新策略

### 1. 创建策略文件

在 `src/strategies/` 目录下创建新文件 `my_strategy.py`

### 2. 继承 BaseStrategy

```python
from src.strategies.base import BaseStrategy, Signal, SignalType
from src.data.bar_data import BarData

class MyStrategy(BaseStrategy):
    """我的新策略描述"""
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        # 在这里初始化参数，设置默认值
        self.param1 = self.params.get('param1', 10)
        self.param2 = self.params.get('param2', 20)
    
    def initialize(self):
        """策略初始化，在回测/实盘开始前调用"""
        self.indicator = self.compute_indicator()
        self.last_position = 0
    
    def on_bar(self, bar: BarData) -> Signal | None:
        """
        处理每个K线，生成交易信号
        
        参数:
            bar: 当前K线数据，包含 open, high, low, close, volume, timestamp
        
        返回:
            Signal 对象或 None
        """
        # 你的策略逻辑在这里
        current_price = bar.close
        
        if buy_condition:
            return Signal(
                signal_type=SignalType.BUY,
                symbol=bar.symbol,
                price=current_price,
                quantity=calculate_quantity(),
                strategy_name=self.name
            )
        elif sell_condition:
            return Signal(
                signal_type=SignalType.SELL,
                symbol=bar.symbol,
                price=current_price,
                quantity=calculate_quantity(),
                strategy_name=self.name
            )
        return None
```

### 3. 在策略注册表中注册

编辑 `src/strategies/__init__.py`，添加你的策略:

```python
from .my_strategy import MyStrategy

STRATEGY_REGISTRY = {
    ...
    'MyStrategy': MyStrategy,
}
```

### 4. 编写单元测试

在 `tests/strategies/` 目录下创建 `test_my_strategy.py`

### 5. 运行回测测试

```bash
python scripts/run_backtest.py --strategy MyStrategy --symbols 000001.SH --start 2020-01-01 --end 2024-01-01
```

## 策略参数约定

- 使用 `self.params` 字典存储所有可调参数
- 提供合理的默认值
- 参数名使用下划线命名法

## 信号类型

```python
class SignalType(Enum):
    BUY = "BUY"           # 买入
    SELL = "SELL"         # 卖出
    HOLD = "HOLD"         # 持有
    CANCEL = "CANCEL"     # 撤单
```

## 常用指标

系统内置了常用技术指标:

```python
from src.utils.indicators import (
    sma,    # 简单移动平均
    ema,    # 指数移动平均
    rsi,    # RSI相对强弱指标
    macd,   # MACD
    bollinger_bands,  # 布林带
    atr,    # 真实波幅
)
```

## 示例：双均线策略

完整示例请参考 `src/strategies/moving_average_crossover.py`

## 示例：RSI策略

完整示例请参考 `src/strategies/rsi_strategy.py`

## 最佳实践

1. **保持简单**: 先实现简单版本，再逐步复杂
2. **避免过拟合**: 使用样本外数据验证
3. **记录日志**: 在关键位置添加日志，方便调试
4. **处理异常**: 做空值检查，异常情况处理
5. **资金管理**: 不要满仓一只股票，考虑分散风险

## 常见问题

**Q: 策略如何访问历史数据?**

A: 在 `initialize()` 阶段可以通过 `self.data_provider` 获取历史数据。

**Q: 如何处理多只股票?**

A: 系统会按时间顺序推送每只股票的K线，策略可以为每只股票维护独立状态。

**Q: 如何使用多个时间周期?**

A: 策略可以自行resample数据，或者在初始化时加载不同周期的数据。
