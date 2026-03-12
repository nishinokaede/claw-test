#!/bin/bash

# 启动后端和前端服务

echo "=== 启动 JWT 认证系统 ==="
echo ""

# 启动后端
echo "正在启动后端服务 (端口 8000)..."
cd /root/jwt-auth-project/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 启动前端
echo "正在启动前端服务 (端口 10000)..."
cd /root/jwt-auth-project/frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=== 服务启动完成 ==="
echo "前端地址: http://localhost:10000"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "测试账号："
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待两个进程
wait $BACKEND_PID $FRONTEND_PID
