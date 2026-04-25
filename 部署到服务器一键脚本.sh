#!/bin/bash
# ============================================
# Lianghua 量化系统 - 一键部署到远程服务器
# ============================================

echo "=========================================="
echo "🚀 Lianghua 量化系统 - 服务器部署脚本"
echo "=========================================="
echo ""

# ============ 配置 ============
SERVER_IP="14.103.60.103"
SERVER_PORT="6002"
SERVER_USER="root"
KEY_FILE="newjingacheng.pem"   # 你的密钥文件路径
GITHUB_REPO="https://github.com/tangyujincheng/lianghua.git"
APP_PORT="8501"

echo "📋 部署配置："
echo "   服务器: $SERVER_USER@$SERVER_IP:$SERVER_PORT"
echo "   应用端口: $APP_PORT"
echo "   代码仓库: $GITHUB_REPO"
echo ""

# ============ 确认 ============
read -p "❓ 确认开始部署？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 已取消部署"
    exit 0
fi

echo ""
echo "=========================================="
echo "1/6 🔐 测试服务器连接..."
echo "=========================================="
ssh -i $KEY_FILE -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "echo '✅ 连接成功'; hostname"
if [ $? -ne 0 ]; then
    echo "❌ 服务器连接失败，请检查："
    echo "   1. 密钥文件路径是否正确: $KEY_FILE"
    echo "   2. 服务器IP和端口是否正确: $SERVER_IP:$SERVER_PORT"
    echo "   3. 服务器用户名是否正确: $SERVER_USER"
    echo "   4. 密钥文件权限: chmod 600 $KEY_FILE"
    exit 1
fi

echo ""
echo "=========================================="
echo "2/6 📦 检查并安装系统依赖..."
echo "=========================================="
ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
    # 检查 Python3
    if ! command -v python3 &> /dev/null; then
        echo "安装 Python3..."
        apt update && apt install -y python3 python3-pip python3-venv
    else
        echo "✅ Python3 已安装: $(python3 --version)"
    fi
    
    # 检查 pip3
    if ! command -v pip3 &> /dev/null; then
        echo "安装 pip3..."
        apt install -y python3-pip
    else
        echo "✅ pip3 已安装"
    fi
    
    # 检查并安装 git
    if ! command -v git &> /dev/null; then
        echo "安装 git..."
        apt install -y git
    else
        echo "✅ git 已安装"
    fi
EOF

echo ""
echo "=========================================="
echo "3/6 📥 从 GitHub 克隆/更新项目..."
echo "=========================================="
ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
    if [ -d "lianghua" ]; then
        echo "项目已存在，更新中..."
        cd lianghua && git pull
    else
        echo "克隆新项目..."
        git clone https://github.com/tangyujincheng/lianghua.git
    fi
EOF

echo ""
echo "=========================================="
echo "4/6 ⚙️  安装 Python 依赖..."
echo "=========================================="
ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
    cd ~/lianghua
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "安装依赖包..."
    pip install --upgrade pip
    pip install streamlit pandas numpy plotly requests
    echo "✅ 依赖安装完成"
EOF

echo ""
echo "=========================================="
echo "5/6 🔄 停止旧服务并启动新服务..."
echo "=========================================="
ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
    # 停止旧服务
    pkill -f "streamlit" 2>/dev/null
    sleep 2
    
    cd ~/lianghua
    source venv/bin/activate
    
    # 启动服务
    nohup python3 -m streamlit run src/dashboard/app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --browser.gatherUsageStats false > /tmp/streamlit.log 2>&1 &
    
    echo "服务已启动，PID: $!"
    sleep 10
    
    # 检查服务状态
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
        echo "✅ 服务启动成功！"
    else
        echo "⚠️  服务正在启动中，请稍后检查..."
    fi
EOF

echo ""
echo "=========================================="
echo "6/6 🌐 获取访问地址..."
echo "=========================================="
PUBLIC_IP=$(ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP "curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print \$1}'")
echo ""
echo "🎉 部署完成！"
echo ""
echo "=========================================="
echo "📊 访问地址："
echo "=========================================="
echo "   内网/公网: http://$PUBLIC_IP:8501"
echo "   本地访问:  http://localhost:8501"
echo ""
echo "📋 常用命令："
echo "   查看日志: ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP 'tail -50 /tmp/streamlit.log'"
echo "   重启服务: ssh -i $KEY_FILE -p $SERVER_PORT $SERVER_USER@$SERVER_IP 'pkill -f streamlit && cd ~/lianghua && source venv/bin/activate && nohup streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > /tmp/streamlit.log 2>&1 &'"
echo ""
echo "✅ 部署成功！请访问上面的地址查看效果！"
echo "=========================================="
