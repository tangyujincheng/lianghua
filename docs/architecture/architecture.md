# Architecture Design: Lianghua

## 系统概述

本系统是一个模块化的量化交易系统，设计目标是：

1. **可扩展性**: 易于添加新策略、新数据源、新执行接口
2. **可测试性**: 策略可以方便地进行回测和参数优化
3. **可靠性**: 完善的错误处理和日志记录
4. **性能**: 高效处理大量历史数据和实时数据

## 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
├─────────────────────────────────────────────────────────────┤
│                    Strategy Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Strategy A  │ │ Strategy B  │ │ ...                 │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Signal Generation                          │
├─────────────────────────────────────────────────────────────┤
│                   Risk Management                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Position    │ │ Drawdown    │ │ Volatility           │   │
│  │ Limiting    │ │ Control     │ │ Adjustment           │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Order Execution                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Backtest    │ │ Broker A   │ │ Broker B            │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Data Layer                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Market Data │ │ Resampler  │ │ Feature Engineering │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Persistence Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ OHLCV       │ │ Orders/Trades│ │ Portfolio History   │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. Data Layer

**职责**: 数据获取、清洗、存储、特征工程

**主要类**:

```python
class BaseDataProvider:
    """数据源基类"""
    def get_ohlcv(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        raise NotImplementedError
    
    def get_realtime_quote(self, symbol: str) -> dict:
        raise NotImplementedError
```

**具体实现**:
- `TushareDataProvider`: Tushare A股数据
- `AkShareDataProvider`: AkShare 开源财经数据
- `YahooFinanceDataProvider`: 雅虎财经美股数据
- `BinanceDataProvider`: 币安加密货币数据
- `MongoDBDataProvider`: 本地数据库存储

### 2. Strategy Layer

**职责**: 生成交易信号

**主要类**:

```python
class BaseStrategy(ABC):
    """策略基类"""
    
    @abstractmethod
    def initialize(self) -> None:
        """策略初始化"""
        pass
    
    @abstractmethod
    def on_bar(self, bar: BarData) -> Signal | None:
        """处理每个K线，生成信号"""
        pass
    
    def on_order(self, order: Order) -> None:
        """订单状态更新回调"""
        pass
    
    def on_trade(self, trade: Trade) -> None:
        """成交回调"""
        pass
```

**设计要点**:
- 每个策略独立管理自己的参数和状态
- 通过 `on_bar` 方法接收数据，返回信号
- 支持多股票、多时间周期

### 3. Risk Management Layer

**职责**: 风险控制，调整最终下单规模

**主要类**:
- `PositionSizer`: 仓位大小计算
- `RiskManager`: 综合风险管理
- `StopLoss`: 止损管理
- `TakeProfit`: 止盈管理

**风险管理规则**:
1. 单票仓位不超过 X%
2. 单日亏损不超过 Y%
3. 总回撤不超过 Z%
4. 根据波动率调整仓位 (Volatility Targeting)

### 4. Execution Layer

**职责**: 执行订单，处理成交回调

**主要类**:

```python
class BaseExecutor(ABC):
    """执行器基类"""
    
    @abstractmethod
    def execute_order(self, order: Order) -> ExecutionResult:
        """执行订单"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """获取账户信息"""
        pass
```

**具体实现**:
- `BacktestExecutor`: 回测执行（模拟成交）
- `XTPExecutor`: 中信证券XTP接口
- `CTPExecutor`: 期货CTP接口
- `BinanceExecutor`: 币安交易接口

### 5. Backtesting Engine

**职责**: 运行历史回测，统计绩效

**主要组件**:
- `BacktestEngine`: 回测引擎主类
- `CommissionModel`: 手续费模型
- `SlippageModel`: 滑点模型
- `Portfolio`: 组合净值管理
- `PerformanceAnalyzer`: 绩效分析

**回测流程**:
1. 加载历史数据
2. 按时间顺序推送K线给策略
3. 策略生成信号
4. 风险模块调整仓位
5. 执行器模拟成交
6. 更新组合状态
7. 回测完成后生成分析报告

### 6. Analytics Layer

**职责**: 绩效评估和可视化

**指标**:
- 累计收益率 (Cumulative Return)
- 年化收益率 (Annualized Return)
- 波动率 (Volatility)
- 夏普比率 (Sharpe Ratio)
- 最大回撤 (Max Drawdown)
- 卡玛比率 (Calmar Ratio)
- 索提诺比率 (Sortino Ratio)
- 胜率 (Win Rate)
- 盈亏比 (Profit Loss Ratio)

**可视化**:
- 净值曲线
- 回撤曲线
- 持仓分布
- 月度收益热力图
- 因子暴露分析

## 数据流

```
Historical Data
       ↓
DataProvider → Clean → Resample → Feature Engineering
       ↓
BacktestEngine / LiveEngine
       ↓
Strategy.on_bar() → Signal
       ↓
RiskManager → Filtered Signal + Position Size
       ↓
Executor → Order → Trade
       ↓
Portfolio → Update Net Value
       ↓
Logger → Save to DB
       ↓
Analyzer → Generate Report
```

## 并发设计

- **数据获取**: 使用异步IO (aiohttp) 并行获取多标的数据
- **回测**: 支持多进程并行参数搜索
- **实时交易**: 事件驱动架构，使用消息队列处理订单

## 配置管理

使用 YAML 配置文件，分层配置:

```yaml
data:
  provider: tushare
  api_key: xxx
  
strategy:
  name: MovingAverageCrossover
  params:
    fast_period: 5
    slow_period: 20
    
risk:
  max_position_size: 0.1
  max_daily_loss: 0.05
  max_drawdown: 0.2
  
execution:
  broker: xtp
  account: xxx
  password: xxx
```

## 日志和监控

- 结构化日志 (JSON格式)
- 关键指标推送 (Prometheus)
- 异常报警 (邮件/企业微信)
- 交易记录完整审计追踪

## 部署架构

### 开发环境
```
Developer → Jupyter Notebook → Local Backtest
```

### 生产环境
```
┌─────────────┐
│  Cron Job   │ → 定时拉取数据
└─────────────┘
┌─────────────┐
│  Strategy   │ → 定时运行策略生成信号
└─────────────┘
┌─────────────┐
│  Execution  │ → 执行订单
└─────────────┘
┌─────────────┐
│  Monitoring │ → 监控和报警
└─────────────┘
```

## 技术选型

| 层级 | 技术选型 | 理由 |
|------|---------|------|
| 语言 | Python 3.10+ | 丰富的数据科学库，量化生态好 |
| 数据处理 | pandas, numpy | 标准工具链 |
| 数据存储 | MongoDB / SQLite | 灵活的文档存储 |
| 绘图 | matplotlib, plotly | 静态+交互式可视化 |
| 科学计算 | scipy, scikit-learn | 统计和机器学习 |
| 异步IO | aiohttp | 高性能数据获取 |
| 配置 | pyyaml | 人类可读配置格式 |
| 日志 | structlog | 结构化日志 |
| 测试 | pytest | 成熟的测试框架 |

## 设计原则

1. **依赖注入**: 组件之间通过接口依赖，便于替换实现
2. **开闭原则**: 对扩展开放，对修改关闭
3. **单一职责**: 每个组件只做一件事
4. **约定大于配置**: 合理的默认值，减少配置负担
5. **可测试性**: 组件易于单元测试
6. **防御式编程**: 完整的参数校验和错误处理

## 未来扩展

- 支持高频交易 (需要C++扩展)
- 支持分布式回测
- 添加WebUI管理界面
- 支持订单流预测机器学习模型
- 集成因子选股库
