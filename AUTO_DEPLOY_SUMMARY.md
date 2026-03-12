# 🎉 自动部署系统配置完成！

## ✅ 已完成配置

### 1. Git 仓库初始化
- ✅ Git 仓库已初始化 (`/root/jwt-auth-project/.git`)
- ✅ 首次提交已完成
- ✅ `.gitignore` 已配置

### 2. Systemd 服务
| 服务名 | 描述 | 状态 | 端口 |
|--------|------|------|------|
| **jwt-backend** | 后端 API 服务 | 🟢 运行中 | 8000 |
| **jwt-frontend** | 前端 Vite 服务 | 🟢 运行中 | 10000 |
| **jwt-webhook** | Git Webhook 服务器 | 🟢 运行中 | 9999 |

### 3. 自动部署脚本
- ✅ `/root/jwt-auth-project/deploy.sh` - 主部署脚本
- ✅ `/root/jwt-auth-project/webhook_server.py` - Webhook 服务器
- ✅ `/root/jwt-auth-project/setup-git.sh` - Git 快速配置脚本

---

## 🚀 使用指南

### 方式一：使用快速配置脚本（推荐）

```bash
cd /root/jwt-auth-project
./setup-git.sh
```

脚本会自动：
1. 配置 Git 用户信息
2. 选择 Git 平台（GitHub/Gitee/GitLab）
3. 配置远程仓库
4. 推送代码
5. 提供 Webhook 配置说明

### 方式二：手动配置

#### 1. 创建远程仓库

**GitHub:** https://github.com/new  
**Gitee:** https://gitee.com/new  
**GitLab:** https://gitlab.com/projects/new

创建名为 `jwt-auth-project` 的仓库

#### 2. 配置远程仓库

```bash
cd /root/jwt-auth-project

# GitHub
git remote add origin https://github.com/YOUR_USERNAME/jwt-auth-project.git

# Gitee
git remote add origin https://gitee.com/YOUR_USERNAME/jwt-auth-project.git

# GitLab
git remote add origin https://gitlab.com/YOUR_USERNAME/jwt-auth-project.git
```

#### 3. 推送代码

```bash
git push -u origin master
```

#### 4. 配置 Webhook

进入仓库设置页面，添加 Webhook：

| 配置项 | 值 |
|--------|-----|
| **Payload URL** | `http://122.51.223.247:9999/` |
| **Content type** | `application/json` |
| **Secret** | `your-webhook-secret-change-me` ⚠️ 需要修改 |
| **Events** | Push events |

---

## 🔐 重要：修改 Webhook Secret

```bash
# 编辑 webhook_server.py
nano /root/jwt-auth-project/webhook_server.py

# 修改这一行（第 14 行）：
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key-here")

# 改为强密码，例如：
WEBHOOK_SECRET = "MySuperSecret2024!@#$%^&*()"
```

然后重启服务：
```bash
systemctl restart jwt-webhook
```

同时在 Git 平台的 Webhook 设置中使用相同的 Secret。

---

## 📊 服务管理命令

### 查看服务状态
```bash
systemctl status jwt-backend jwt-frontend jwt-webhook
```

### 重启服务
```bash
systemctl restart jwt-backend
systemctl restart jwt-frontend
systemctl restart jwt-webhook
```

### 查看日志
```bash
# 后端日志
journalctl -u jwt-backend -f
tail -f /tmp/backend.log

# 前端日志
journalctl -u jwt-frontend -f
tail -f /tmp/frontend.log

# Webhook 日志
journalctl -u jwt-webhook -f
tail -f /tmp/webhook.log
```

### 开机自启
```bash
systemctl enable jwt-backend jwt-frontend jwt-webhook
```

---

## 🎯 完整工作流

### 日常开发部署

```bash
# 1. 在本地修改代码
# ... 编辑文件 ...

# 2. 提交更改
git add .
git commit -m "添加新功能"

# 3. 推送到远程仓库
git push origin master

# 4. 等待自动部署（约 1-2 分钟）
# 查看部署日志
tail -f /tmp/webhook.log

# 5. 验证部署
curl http://122.51.223.247:8000/
# 或访问浏览器 http://122.51.223.247:10000
```

### 手动部署

如果自动部署失败，可以手动执行：

```bash
bash /root/jwt-auth-project/deploy.sh
```

---

## 🔧 故障排查

### 1. 服务未运行

```bash
# 检查服务状态
systemctl status jwt-backend jwt-frontend jwt-webhook

# 重启服务
systemctl restart jwt-backend jwt-frontend jwt-webhook
```

### 2. Webhook 不触发

```bash
# 检查端口是否开放
netstat -tlnp | grep 9999

# 检查防火墙
ufw allow 9999/tcp

# 测试 Webhook
curl -X POST http://122.51.223.247:9999/ \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/master","repository":{"full_name":"test/test"}}'
```

### 3. 部署失败

```bash
# 查看日志
tail -f /tmp/webhook.log

# 手动执行部署
bash -x /root/jwt-auth-project/deploy.sh
```

---

## 📁 重要文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| **部署脚本** | `/root/jwt-auth-project/deploy.sh` | 自动部署主脚本 |
| **Webhook 服务** | `/root/jwt-auth-project/webhook_server.py` | 监听 Git 推送 |
| **快速配置** | `/root/jwt-auth-project/setup-git.sh` | 一键配置 Git |
| **配置文档** | `/root/jwt-auth-project/DEPLOYMENT.md` | 详细配置指南 |
| **Systemd 服务** | `/etc/systemd/system/jwt-*.service` | 服务配置 |

---

## 🎊 恭喜！

你现在拥有了一个完整的 **CI/CD 自动部署系统**！

### 功能特性

✅ **代码推送自动部署** - Push 到 master 分支自动触发  
✅ **服务自动重启** - 使用 systemd 保证服务稳定运行  
✅ **日志记录** - 完整的部署日志便于排查问题  
✅ **双 Token 认证** - Access Token (30 分钟) + Refresh Token (90 天)  
✅ **自动 Token 刷新** - 用户无感知续期  
✅ **密码显示切换** - 用户体验优化  

### 下一步

1. **修改 Webhook Secret**（必须！）
2. **在 Git 平台配置 Webhook**
3. **推送代码测试自动部署**
4. **配置 HTTPS（可选，生产环境推荐）**

---

**📞 需要帮助？**

查看详细文档：`/root/jwt-auth-project/DEPLOYMENT.md`

查看日志：`tail -f /tmp/webhook.log`

---

**祝你使用愉快！🚀**
