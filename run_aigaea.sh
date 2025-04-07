#!/bin/bash

# 定义项目目录和虚拟环境名称
PROJECT_DIR="AiGaea-BOT"
VENV_NAME="aigaea_venv"
PYTHON_CMD="python3"
MIN_VERSION="3.9"

# 函数：检查并安装前置组件
install_prerequisites() {
    echo "检查和安装前置组件..."

    # 检查是否为 root 用户（某些系统需要 sudo）
    if [ "$EUID" -ne 0 ]; then
        SUDO="sudo"
    else
        SUDO=""
    fi

    # 检查 Git
    if ! command -v git &> /dev/null; then
        echo "未找到 Git，正在安装..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y git
        if [ $? -ne 0 ]; then
            echo "错误：Git 安装失败，请手动安装后再运行脚本"
            exit 1
        fi
        echo "Git 安装成功"
    else
        echo "Git 已安装"
    fi

    # 检查 Python 3.9+
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo "未找到 Python，正在安装 Python 3.9..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3.9 python3-pip python3-venv
        if [ $? -ne 0 ]; then
            echo "错误：Python 安装失败，请手动安装 Python 3.9 或更高版本"
            exit 1
        fi
        PYTHON_CMD="python3.9"  # 更新 Python 命令为新安装的版本
        echo "Python 3.9 安装成功"
    else
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
            echo "当前 Python 版本 ($PYTHON_VERSION) 低于 3.9，正在安装 Python 3.9..."
            $SUDO apt-get update -y
            $SUDO apt-get install -y python3.9 python3-pip python3-venv
            if [ $? -ne 0 ]; then
                echo "错误：Python 3.9 安装失败，请手动安装"
                exit 1
            fi
            PYTHON_CMD="python3.9"
            echo "Python 3.9 安装成功"
        else
            echo "Python 已安装，版本为 $PYTHON_VERSION"
        fi
    fi
}

# 函数：克隆或更新项目
clone_or_update_project() {
    if [ -d "$PROJECT_DIR" ]; then
        echo "更新现有项目..."
        cd "$PROJECT_DIR"
        git pull origin main
        cd ..
    else
        echo "克隆项目..."
        git clone https://github.com/vonssy/AiGaea-BOT.git
    fi
}

# 函数：设置虚拟环境和依赖
setup_environment() {
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

    # 安装项目依赖
    echo "安装项目依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误：依赖安装失败，请检查网络或 requirements.txt 文件"
        exit 1
    fi
}

# 函数：检查和提示配置文件
check_config() {
    if [ ! -f "tokens.txt" ]; then
        echo "警告：未找到 tokens.txt 文件，请创建并填写您的 token 数据"
        echo "示例格式（每行一个 token）："
        echo "token1"
        echo "token2"
        echo "您可以在脚本运行后手动创建 tokens.txt 文件"
    fi
}

# 主流程
echo "开始运行 AiGaea-BOT 脚本..."

# 安装前置组件
install_prerequisites

# 克隆或更新项目
clone_or_update_project

# 设置虚拟环境和依赖
setup_environment

# 检查配置文件
check_config

# 运行项目
echo "启动 AiGaea-BOT..."
python bot.py

# 退出虚拟环境
deactivate

echo "脚本执行完成"