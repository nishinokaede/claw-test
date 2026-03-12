# JWT 认证系统

一个使用 FastAPI 后端和 React 前端的简单 JWT 认证系统。

## 项目结构

```
jwt-auth-project/
├── backend/          # FastAPI 后端
│   ├── main.py      # 主应用程序
│   ├── requirements.txt
│   └── .env
└── frontend/         # React 前端
    ├── src/
    │   ├── App.jsx
    │   ├── App.css
    │   └── main.jsx
    └── package.json
```

## 功能特性

- ✅ JWT 认证
- ✅ 用户登录
- ✅ 自动 token 管理
- ✅ 受保护的路由
- ✅ 响应式设计
- ✅ CORS 配置

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务器
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端将在 `http://localhost:8000` 运行

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（在 10000 端口）
npm run dev
```

前端将在 `http://localhost:10000` 运行

## 测试账号

默认测试账号：
- 用户名：`admin`
- 密码：`admin123`

## API 端点

- `POST /login` - 用户登录，返回 JWT token
- `GET /users/me` - 获取当前用户信息（需要认证）
- `GET /` - API 健康检查

## 安全提示

⚠️ **重要**：在生产环境中，请务必：
1. 修改 `.env` 文件中的 `SECRET_KEY` 为强密码
2. 使用真实数据库而非模拟数据库
3. 配置 HTTPS
4. 实施 rate limiting
5. 添加更完善的错误处理

## 技术栈

### 后端
- FastAPI
- Uvicorn
- python-jose (JWT)
- passlib (密码加密)
- bcrypt

### 前端
- React 19
- Vite
- Axios
- CSS3

## 访问地址

- 前端：http://localhost:10000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
