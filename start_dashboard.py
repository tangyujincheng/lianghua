#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lianghua 量化决策系统 - 快速启动脚本

使用方法:
    python start_dashboard.py
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    required = ['streamlit', 'pandas', 'numpy', 'plotly']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print("❌ 缺少以下依赖包:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n正在自动安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("✅ 依赖安装完成!")
    else:
        print("✅ 所有依赖已安装")

def main():
    print("=" * 70)
    print("🌟 Lianghua 量化决策系统 - Web 仪表盘")
    print("=" * 70)
    print()
    
    # 检查依赖
    check_dependencies()
    print()
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(project_root, "src", "dashboard", "app.py")
    
    print("📖 使用说明:")
    print("  - 浏览器将自动打开 http://localhost:8501")
    print("  - 如果没有自动打开，请手动访问上面的地址")
    print("  - 按 Ctrl+C 停止服务")
    print()
    print("🚀 正在启动仪表盘...")
    print()
    
    # 运行streamlit
    os.chdir(project_root)
    sys.path.insert(0, project_root)
    
    try:
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", app_path,
                   "--server.port", "8501",
                   "--server.address", "127.0.0.1",
                   "--browser.gatherUsageStats", "false"]
        stcli.main()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 请尝试手动启动:")
        print(f"   cd {project_root}")
        print(f"   streamlit run src/dashboard/app.py --server.port 8501")
        sys.exit(1)

if __name__ == "__main__":
    main()