#!/bin/bash

# 定义项目目录和虚拟环境名称
PROJECT_DIR="AiGaea-BOT"
VENV_NAME="aigaea_venv"

# 检查是否已安装 Python 3.9 或更高版本
PYTHON_CMD="python3"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
MIN_VERSION="3.9"

if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
    echo "错误：需要 Python 3.9 或更高版本，当前版本为 $PYTHON_VERSION"
    exit 1
fi

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo "错误：未找到 git，请先安装 git"
    exit 1
fi

# 克隆或更新项目
if [ -d "$PROJECT_DIR" ]; then
    echo "更新现有项目..."
    cd "$PROJECT_DIR"
    git pull origin main
    cd ..
else
    echo "克隆项目..."
    git clone https://github.com/vonssy/AiGaea-BOT.git
fi

# 进入项目目录
cd "$PROJECT_DIR" || exit

# 创建虚拟环境
if [ ! -d "$VENV_NAME" ]; then
    echo "创建虚拟环境..."
    $PYTHON_CMD -m venv "$VENV_NAME"
fi

# 激活虚拟环境
source "$VENV_NAME/bin/activate"

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 检查 tokens.txt 文件是否存在
if [ ! -f "tokens.txt" ]; then
    echo "警告：未找到 tokens.txt 文件，请创建并填写您的 token 数据"
    echo "示例格式（每行一个 token）："
    echo "token1"
    echo "token2"
fi

# 运行项目
echo "启动 AiGaea-BOT..."
python bot.py

# 退出虚拟环境
deactivate