#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lianghua 量化决策系统 - 仪表盘启动脚本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("=" * 60)
    print("🌟 Lianghua 量化决策系统 - Web 仪表盘")
    print("=" * 60)
    print()
    print("📖 使用说明:")
    print("  - 浏览器将自动打开 http://localhost:8501")
    print("  - 如果没有自动打开，请手动访问上面的地址")
    print("  - 按 Ctrl+C 停止服务")
    print()
    
    # 导入streamlit并运行
    from streamlit.web import cli as stcli
    
    app_path = os.path.join(project_root, "src", "dashboard", "app.py")
    
    # 运行streamlit应用
    sys.argv = ["streamlit", "run", app_path, 
                "--server.port", "8501",
                "--server.address", "127.0.0.1",
                "--browser.gatherUsageStats", "false"]
    
    try:
        stcli.main()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        sys.exit(0)