# 🚀 JWT Auth Project - 自动部署配置指南

## 📋 目录

1. [系统架构](#系统架构)
2. [快速开始](#快速开始)
3. [配置 Git 仓库](#配置 git 仓库)
4. [配置 Webhook](#配置 webhook)
5. [手动部署](#手动部署)
6. [服务管理](#服务管理)
7. [故障排查](#故障排查)

---

## 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                    代码推送流程                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  本地开发 → Git Push → GitHub/Gitee                      │
│                      ↓                                    │
│              Webhook 通知                                 │
│                      ↓                                    │
│         webhook_server.py (端口 9999)                     │
│                      ↓                                    │
│              deploy.sh 部署脚本                           │
│                      ↓                                    │
│    ┌─────────────────┴─────────────────┐                 │
│    ↓                                   ↓                 │
│  后端服务                         前端服务                 │
│  (systemd: jwt-backend)          (systemd: jwt-frontend) │
│  端口：8000                      端口：10000             │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 1️⃣ 初始化 Git 仓库（已完成）

```bash
cd /root/jwt-auth-project
git init
git add .
git commit -m "Initial commit"
```

### 2️⃣ 启动 Webhook 服务器（已启动）

```bash
# Webhook 服务器已在端口 9999 运行
ps aux | grep webhook_server
```

### 3️⃣ 配置远程仓库

```bash
# GitHub
git remote add origin https://github.com/YOUR_USERNAME/jwt-auth-project.git

# 或 Gitee
git remote add origin https://gitee.com/YOUR_USERNAME/jwt-auth-project.git

# 推送代码
git push -u origin master
```

---

## 配置 Git 仓库

### GitHub 配置

1. **创建仓库**
   - 访问 https://github.com/new
   - 创建名为 `jwt-auth-project` 的仓库
   - 设为私有或公开（建议私有）

2. **推送代码**
   ```bash
   cd /root/jwt-auth-project
   git remote add origin https://github.com/YOUR_USERNAME/jwt-auth-project.git
   git push -u origin master
   ```

3. **配置 Webhook**
   - 进入仓库 → Settings → Webhooks
   - 点击 "Add webhook"
   - 填写：
     - **Payload URL**: `http://122.51.223.247:9999/`
     - **Content type**: `application/json`
     - **Secret**: `your-webhook-secret-change-me`（需要修改）
     - **Events**: 选择 "Just the push event"
   - 点击 "Add webhook"

### Gitee 配置

1. **创建仓库**
   - 访问 https://gitee.com/new
   - 创建名为 `jwt-auth-project` 的仓库

2. **推送代码**
   ```bash
   cd /root/jwt-auth-project
   git remote add origin https://gitee.com/YOUR_USERNAME/jwt-auth-project.git
   git push -u origin master
   ```

3. **配置 Webhook**
   - 进入仓库 → 管理 → WebHooks
   - 点击 "添加 WebHook"
   - 填写：
     - **WebHook URL**: `http://122.51.223.247:9999/`
     - **密码**: `your-webhook-secret-change-me`
     - **触发事件**: 勾选 "Push 事件"
   - 点击 "添加"

### GitLab 配置

1. **创建仓库**
   ```bash
   git remote add origin https://gitlab.com/YOUR_USERNAME/jwt-auth-project.git
   git push -u origin master
   ```

2. **配置 Webhook**
   - 进入仓库 → Settings → Webhooks
   - URL: `http://122.51.223.247:9999/`
   - Secret Token: `your-webhook-secret-change-me`
   - Trigger: 勾选 "Push events"
   - 点击 "Add webhook"

---

## 配置 Webhook

### 修改 Secret（重要！）

1. **编辑 webhook_server.py**
   ```bash
   nano /root/jwt-auth-project/webhook_server.py
   ```
   
   修改这一行：
   ```python
   WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret-change-me")
   ```
   
   改为强密码，例如：
   ```python
   WEBHOOK_SECRET = "MySuperSecret2024!@#$"
   ```

2. **重启 Webhook 服务器**
   ```bash
   pkill -f webhook_server.py
   cd /root/jwt-auth-project && source venv/bin/activate
   nohup python3 webhook_server.py > /tmp/webhook.log 2>&1 &
   ```

3. **更新 systemd 服务**
   ```bash
   nano /etc/systemd/system/jwt-webhook.service
   ```
   
   修改：
   ```ini
   Environment=WEBHOOK_SECRET=MySuperSecret2024!@#$
   ```
   
   重新加载：
   ```bash
   systemctl daemon-reload
   systemctl restart jwt-webhook
   ```

---

## 手动部署

如果自动部署失败，可以手动执行部署脚本：

```bash
# 执行部署脚本
bash /root/jwt-auth-project/deploy.sh

# 或进入项目目录执行
cd /root/jwt-auth-project
./deploy.sh
```

部署脚本会执行以下操作：
1. ✅ Git pull 拉取最新代码
2. ✅ 安装 Python 依赖
3. ✅ 安装 Node.js 依赖
4. ✅ 停止旧服务
5. ✅ 启动新服务

---

## 服务管理

### 使用 systemd 管理服务

**查看所有服务状态：**
```bash
systemctl status jwt-backend jwt-frontend jwt-webhook
```

**启动服务：**
```bash
systemctl start jwt-backend
systemctl start jwt-frontend
systemctl start jwt-webhook
```

**停止服务：**
```bash
systemctl stop jwt-backend
systemctl stop jwt-frontend
systemctl stop jwt-webhook
```

**重启服务：**
```bash
systemctl restart jwt-backend
systemctl restart jwt-frontend
systemctl restart jwt-webhook
```

**开机自启：**
```bash
systemctl enable jwt-backend
systemctl enable jwt-frontend
systemctl enable jwt-webhook
```

### 查看日志

**后端日志：**
```bash
journalctl -u jwt-backend -f
# 或
tail -f /tmp/backend.log
```

**前端日志：**
```bash
journalctl -u jwt-frontend -f
# 或
tail -f /tmp/frontend.log
```

**Webhook 日志：**
```bash
journalctl -u jwt-webhook -f
# 或
tail -f /tmp/webhook.log
```

---

## 故障排查

### 1. 服务无法启动

**检查端口占用：**
```bash
netstat -tlnp | grep -E "(8000|10000|9999)"
```

**查看错误日志：**
```bash
journalctl -u jwt-backend -n 50 --no-pager
```

### 2. Webhook 不触发

**检查防火墙：**
```bash
# 开放 9999 端口
ufw allow 9999/tcp
# 或
iptables -A INPUT -p tcp --dport 9999 -j ACCEPT
```

**测试 Webhook：**
```bash
# 发送测试请求
curl -X POST http://122.51.223.247:9999/ \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/master","repository":{"full_name":"test/test"}}'
```

**查看 Webhook 日志：**
```bash
tail -f /tmp/webhook.log
```

### 3. 部署失败

**检查部署脚本权限：**
```bash
chmod +x /root/jwt-auth-project/deploy.sh
```

**手动执行部署：**
```bash
bash -x /root/jwt-auth-project/deploy.sh
```

**检查依赖安装：**
```bash
# 后端
cd /root/jwt-auth-project/backend
source venv/bin/activate
pip install -r requirements.txt

# 前端
cd /root/jwt-auth-project/frontend
npm install
```

### 4. 代码更新但未自动部署

**检查 Git 分支：**
```bash
cd /root/jwt-auth-project
git branch  # 确保在 master 分支
git log     # 查看最新提交
```

**检查 Webhook 配置：**
- 确认 Payload URL 正确
- 确认 Secret 匹配
- 确认触发事件包含 Push

**手动触发部署：**
```bash
bash /root/jwt-auth-project/deploy.sh
```

---

## 安全建议

1. **修改默认 Secret**
   - 将 `your-webhook-secret-change-me` 改为强密码
   - 至少 16 位，包含大小写字母、数字、特殊字符

2. **配置防火墙**
   ```bash
   # 只允许必要的端口
   ufw allow 22/tcp      # SSH
   ufw allow 8000/tcp    # 后端 API
   ufw allow 10000/tcp   # 前端
   ufw allow 9999/tcp    # Webhook（可选，仅限 Git 服务器 IP）
   ```

3. **使用 HTTPS（可选）**
   - 配置 Nginx 反向代理
   - 使用 Let's Encrypt 免费证书

4. **限制 Webhook IP**
   - GitHub: 192.30.252.0/22
   - Gitee: 180.76.152.0/24

---

## 完整工作流

```bash
# 1. 本地开发
git checkout -b feature/new-feature
# ... 编写代码 ...
git add .
git commit -m "Add new feature"

# 2. 推送到远程
git checkout master
git merge feature/new-feature
git push origin master

# 3. 自动部署（Webhook 触发）
# 服务器自动执行 deploy.sh
# 等待 1-2 分钟

# 4. 验证部署
curl http://122.51.223.247:8000/
# 或访问浏览器
# http://122.51.223.247:10000
```

---

## 联系支持

如果遇到问题：
1. 查看日志文件
2. 检查服务状态
3. 手动执行部署脚本
4. 重启相关服务

---

**🎉 恭喜！你现在拥有了一个完整的 CI/CD 自动部署系统！**
