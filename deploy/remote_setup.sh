#!/bin/bash
set -e
echo "=== 虚拟教研社区 一键部署 ==="
echo ""

# 1. 系统更新
echo "[1/7] 系统更新..."
apt update -qq && apt upgrade -y -qq

# 2. 装依赖
echo "[2/7] 安装系统依赖..."
apt install -y -qq nginx mysql-server python3 python3-pip python3-venv supervisor git curl

# 3. 装 Node.js 18
echo "[3/7] 安装 Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y -qq nodejs

# 4. 拉代码
echo "[4/7] 拉取代码..."
mkdir -p /var/www
cd /var/www
git clone https://github.com/stowar/teaching-research-platform.git 2>/dev/null || (cd teaching-research-platform && git pull)
cd teaching-research-platform
git checkout dev-vue 2>/dev/null || true

# 5. 后端环境
echo "[5/7] 配置后端..."
cd /var/www/teaching-research-platform/backend
python3 -m venv /var/www/venv
source /var/www/venv/bin/activate
pip install --upgrade pip -q
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu -q
pip install -r requirements.txt -q

# 6. 前端构建
echo "[6/7] 构建前端..."
cd /var/www/teaching-research-platform/frontend-vue
npm install --silent
npm run build

# 7. 配置服务
echo "[7/7] 配置 Nginx + Supervisor..."
cp /var/www/teaching-research-platform/deploy/nginx.conf /etc/nginx/conf.d/teaching-research.conf
cp /var/www/teaching-research-platform/deploy/supervisor.ini /etc/supervisor/conf.d/teaching-research.conf
mkdir -p /var/log/teaching-research
nginx -t && systemctl reload nginx
supervisorctl reread
supervisorctl update
supervisorctl start teaching-research-backend

echo ""
echo "=== 部署完成 ==="
echo "前端: http://8.138.124.111"
echo ""
echo "下一步：初始化数据库"
echo "  mysql -u root -p < /var/www/teaching-research-platform/docs/database/create_tables.sql"
