#!/bin/bash
# 虚拟教研社区 — 一键部署脚本（Ubuntu/Debian）
# 用法: chmod +x setup.sh && sudo bash setup.sh

set -e
echo "=== 虚拟教研社区 部署开始 ==="

# ---------- 1. 系统依赖 ----------
echo "[1/6] 安装系统依赖..."
apt update -qq
apt install -y python3 python3-venv python3-pip nginx supervisor mysql-server

# ---------- 2. 目录结构 ----------
echo "[2/6] 创建目录..."
mkdir -p /var/www/teaching-research
mkdir -p /var/log/teaching-research

# ---------- 3. 拉取代码 ----------
echo "[3/6] 部署代码..."
# 方式 A：从 GitHub 拉取
# git clone https://github.com/stowar/teaching-research-platform.git /var/www/teaching-research
# 方式 B：手动上传后解压
# tar -xzf teaching-research.tar.gz -C /var/www/teaching-research
echo "请手动将项目代码放到 /var/www/teaching-research 目录下"
echo "（git clone 或 手动上传）"

# ---------- 4. Python 虚拟环境 ----------
echo "[4/6] 创建 Python 虚拟环境..."
cd /var/www/teaching-research/backend
python3 -m venv /var/www/teaching-research/venv
source /var/www/teaching-research/venv/bin/activate
pip install --upgrade pip -q

# PyTorch CPU 版（国内用清华源加速）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu -q
# 其他依赖
pip install -r requirements.txt -q

# ---------- 5. Nginx ----------
echo "[5/6] 配置 Nginx..."
cp /var/www/teaching-research/deploy/nginx.conf /etc/nginx/conf.d/teaching-research.conf
# 前端静态文件
cd /var/www/teaching-research/frontend-vue
# 如有 Node.js，可以先构建
# npm install && npm run build
nginx -t && systemctl reload nginx

# ---------- 6. Supervisor ----------
echo "[6/6] 配置 Supervisor..."
cp /var/www/teaching-research/deploy/supervisor.ini /etc/supervisor/conf.d/teaching-research.conf
supervisorctl reread
supervisorctl update
supervisorctl start teaching-research-backend

# ---------- 7. MySQL 初始化 ----------
echo ""
echo "=== 初始化数据库 ==="
echo "请手动执行:"
echo "  mysql -u root -p < /var/www/teaching-research/docs/database/create_tables.sql"
echo ""

echo "=== 部署完成 ==="
echo "前端: http://你的服务器IP"
echo "后端: http://你的服务器IP/api/v1/"
echo "API文档: http://你的服务器IP/api/v1/docs (如保留开发模式)"
