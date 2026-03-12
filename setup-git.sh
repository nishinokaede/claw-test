#!/bin/bash

# JWT Auth Project - 快速配置脚本
# 用途：一键配置 Git 远程仓库和 Webhook

set -e

echo "========================================="
echo "🚀 JWT Auth Project 快速配置"
echo "========================================="
echo ""

# 配置 Git 用户信息
echo "📝 配置 Git 用户信息..."
read -p "请输入你的 Git 用户名：" GIT_USERNAME
read -p "请输入你的 Git 邮箱：" GIT_EMAIL

git config --global user.name "$GIT_USERNAME"
git config --global user.email "$GIT_EMAIL"
echo "✅ Git 用户信息已配置"
echo ""

# 选择 Git 平台
echo "🌐 选择 Git 平台:"
echo "1. GitHub"
echo "2. Gitee (码云)"
echo "3. GitLab"
read -p "请选择 (1/2/3): " GIT_PLATFORM

case $GIT_PLATFORM in
    1)
        GIT_HOST="github.com"
        echo "你选择了 GitHub"
        ;;
    2)
        GIT_HOST="gitee.com"
        echo "你选择了 Gitee"
        ;;
    3)
        GIT_HOST="gitlab.com"
        echo "你选择了 GitLab"
        ;;
    *)
        echo "无效选择，使用 GitHub"
        GIT_HOST="github.com"
        ;;
esac

echo ""

# 配置远程仓库
echo "🔗 配置远程仓库..."
read -p "请输入仓库名 (默认：jwt-auth-project): " REPO_NAME
REPO_NAME=${REPO_NAME:-jwt-auth-project}

REMOTE_URL="https://${GIT_HOST}/${GIT_USERNAME}/${REPO_NAME}.git"
echo "远程仓库 URL: $REMOTE_URL"
echo ""

# 添加或更新 remote
if git remote | grep -q "^origin$"; then
    echo "更新已有的 origin remote..."
    git remote set-url origin "$REMOTE_URL"
else
    echo "添加 origin remote..."
    git remote add origin "$REMOTE_URL"
fi

echo "✅ Remote 配置完成"
echo ""

# 推送代码
echo "📤 推送代码到远程仓库..."
read -p "是否立即推送代码？(y/n): " PUSH_CODE

if [ "$PUSH_CODE" = "y" ]; then
    # 检查是否有 SSH key
    if [ ! -f ~/.ssh/id_rsa.pub ]; then
        echo "⚠️  未找到 SSH key，需要配置 SSH 访问"
        echo "请按照以下步骤操作："
        echo "1. 生成 SSH key: ssh-keygen -t rsa -b 4096 -C \"$GIT_EMAIL\""
        echo "2. 将 ~/.ssh/id_rsa.pub 的内容添加到 ${GIT_HOST} 的 SSH keys 设置"
        echo "3. 运行：git push -u origin master"
        exit 1
    fi
    
    # 尝试推送
    if git push -u origin master; then
        echo "✅ 代码推送成功！"
    else
        echo "⚠️  推送失败，可能需要配置 SSH 或 HTTPS 认证"
        echo ""
        echo "使用 HTTPS 推送（需要输入用户名和密码/Token）："
        echo "  git push -u origin master"
        echo ""
        echo "使用 SSH 推送（推荐）："
        echo "  1. 生成 SSH key: ssh-keygen -t rsa -b 4096 -C \"$GIT_EMAIL\""
        echo "  2. 将 ~/.ssh/id_rsa.pub 添加到 ${GIT_HOST}"
        echo "  3. 测试连接："
        if [ "$GIT_HOST" = "github.com" ]; then
            echo "     ssh -T git@github.com"
        elif [ "$GIT_HOST" = "gitee.com" ]; then
            echo "     ssh -T git@gitee.com"
        else
            echo "     ssh -T git@$GIT_HOST"
        fi
        exit 1
    fi
else
    echo "跳过推送，你可以稍后手动执行：git push -u origin master"
fi

echo ""

# Webhook 配置说明
echo "========================================="
echo "🔔 Webhook 配置说明"
echo "========================================="
echo ""
echo "请在 ${GIT_HOST} 上配置 Webhook："
echo ""
echo "1. 进入仓库页面 → Settings → Webhooks"
echo "2. 点击 'Add webhook' 或 '添加 WebHook'"
echo "3. 填写以下信息："
echo ""
echo "   Payload URL: http://122.51.223.247:9999/"
echo "   Content type: application/json"
echo "   Secret: your-webhook-secret-change-me"
echo "   Events: Push events"
echo ""
echo "⚠️  重要：请修改 Secret！"
echo "   编辑文件：/root/jwt-auth-project/webhook_server.py"
echo "   修改：WEBHOOK_SECRET = '你的强密码'"
echo ""
echo "========================================="
echo "✨ 配置完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 修改 Webhook Secret（重要！）"
echo "2. 在 ${GIT_HOST} 上配置 Webhook"
echo "3. 推送代码测试自动部署"
echo ""
echo "测试部署："
echo "  git commit -am '测试自动部署'"
echo "  git push origin master"
echo ""
echo "查看部署日志："
echo "  tail -f /tmp/webhook.log"
echo "  tail -f /tmp/backend.log"
echo "  tail -f /tmp/frontend.log"
echo ""
