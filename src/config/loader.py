"""
Configuration loader - 配置加载
"""
import os
from typing import Dict, Any
import yaml
from dotenv import load_dotenv


class Config:
    """配置类"""
    
    def __init__(self, config_dict: Dict):
        self._config = config_dict
        
    def get(self, key: str, default=None) -> Any:
        """获取配置，支持点分隔路径"""
        parts = key.split('.')
        current = self._config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def __getitem__(self, key: str) -> Any:
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._config
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return self._config.copy()


def load_config(config_path: str = "config/config.yaml") -> Config:
    """加载配置文件"""
    # 加载环境变量
    load_dotenv()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    
    # 环境变量替换
    config_dict = _replace_env_vars(config_dict)
    
    return Config(config_dict)


def _replace_env_vars(obj):
    """递归替换环境变量"""
    if isinstance(obj, dict):
        return {k: _replace_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
        env_var = obj[2:-1]
        return os.getenv(env_var, env_var)
    else:
        return obj


def get_risk_config(config: Config) -> dict:
    """从配置获取风险配置"""
    from src.risk.manager import RiskConfig
    
    risk_data = config.get('risk', {})
    return RiskConfig(**risk_data)


def get_backtest_config(config: Config) -> dict:
    """从配置获取回测配置"""
    return config.get('backtest', {})
