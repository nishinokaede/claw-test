#!/bin/bash

# JWT Auth Project 自动部署脚本
# 用途：拉取最新代码并自动重启服务

set -e

PROJECT_DIR="/root/jwt-auth-project"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "========================================="
echo "🚀 JWT Auth Project 自动部署"
echo "========================================="
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 进入项目目录
cd "$PROJECT_DIR"

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master
echo "✅ 代码拉取完成"
echo ""

# 2. 安装后端依赖
echo "📦 安装后端依赖..."
cd "$BACKEND_DIR"
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    echo "✅ 后端依赖更新完成"
else
    echo "⚠️  未找到虚拟环境，请手动创建"
    exit 1
fi
echo ""

# 3. 安装前端依赖
echo "📦 安装前端依赖..."
cd "$FRONTEND_DIR"
if [ -d "node_modules" ]; then
    npm install --silent
    echo "✅ 前端依赖更新完成"
else
    echo "⚠️  未找到 node_modules，请手动运行 npm install"
    exit 1
fi
echo ""

# 4. 重启服务（使用 systemd）
echo "🔄 重启服务..."

# 检查是否使用 systemd
if command -v systemctl &> /dev/null; then
    echo "使用 systemd 重启服务..."
    systemctl daemon-reload
    systemctl restart jwt-backend
    systemctl restart jwt-frontend
    echo "✅ 服务已通过 systemd 重启"
else
    echo "使用传统方式重启服务..."
    pkill -f "python3 main.py" || true
    pkill -f "vite" || true
    sleep 2
    
    # 启动后端
    cd "$BACKEND_DIR"
    source venv/bin/activate
    nohup python3 main.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    
    # 等待后端启动
    sleep 3
    
    # 启动前端
    cd "$FRONTEND_DIR"
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
fi

echo ""
echo "========================================="
echo "✨ 部署完成！"
echo "========================================="
echo ""
echo "服务状态："
echo "  后端 API: http://122.51.223.247:8000"
echo "  前端页面：http://122.51.223.247:10000"
echo "  API 文档：http://122.51.223.247:8000/docs"
echo ""
echo "日志查看："
echo "  后端日志：tail -f /tmp/backend.log"
echo "  前端日志：tail -f /tmp/frontend.log"
echo ""
