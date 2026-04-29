#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================="
echo "Word Report Backend 启动脚本"
echo "========================================="

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

echo ""
echo "启动服务..."
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "========================================="

python main.py