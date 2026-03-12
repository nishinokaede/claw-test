#!/usr/bin/env python3
"""
Git Webhook 服务器
监听 GitHub/Gitee/GitLab 的 webhook 请求，自动触发部署脚本
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import hashlib
import hmac
import os
import json
import sys

# 配置
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret-change-me")
DEPLOY_SCRIPT = "/root/jwt-auth-project/deploy.sh"
PORT = 9999

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 获取请求内容
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # 验证签名（如果有的话）
        signature = self.headers.get('X-Hub-Signature-256', '')
        if signature:
            expected = 'sha256=' + hmac.new(
                WEBHOOK_SECRET.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                self.send_error(403, "Invalid signature")
                return
        
        # 解析 payload
        try:
            payload = json.loads(body)
            event = self.headers.get('X-Git-Event', 'push')
            
            print(f"收到 webhook 事件：{event}")
            print(f"仓库：{payload.get('repository', {}).get('full_name', 'unknown')}")
            print(f"分支：{payload.get('ref', 'unknown')}")
            
            # 只在推送到 master 分支时触发部署
            if payload.get('ref') == 'refs/heads/master':
                print("触发自动部署...")
                self.trigger_deploy()
            else:
                print("非 master 分支，跳过部署")
                
        except Exception as e:
            print(f"解析 payload 失败：{e}")
        
        # 返回响应
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")
    
    def trigger_deploy(self):
        """执行部署脚本"""
        try:
            result = subprocess.run(
                ['bash', DEPLOY_SCRIPT],
                capture_output=True,
                text=True,
                timeout=300
            )
            print("部署输出:")
            print(result.stdout)
            if result.stderr:
                print("部署错误:")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("部署超时!")
        except Exception as e:
            print(f"部署失败：{e}")
    
    def log_message(self, format, *args):
        print(f"[Webhook] {args[0]}")

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    print(f"🚀 Webhook 服务器启动在端口 {PORT}")
    print(f"📡 监听地址：http://0.0.0.0:{PORT}")
    print(f"🔐 Secret: {WEBHOOK_SECRET}")
    print("")
    print("配置 webhook 时，请将 URL 设置为:")
    print(f"  http://122.51.223.247:{PORT}/")
    print("")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
