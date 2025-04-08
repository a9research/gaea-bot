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
        echo "未找到 Python，正在安装 Python 3.10..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3.10 python3-pip python3.10-venv
        if [ $? -ne 0 ]; then
            echo "错误：Python 安装失败，请手动安装 Python 3.9 或更高版本"
            exit 1
        fi
        PYTHON_CMD="python3.10"
        echo "Python 3.10 安装成功"
    else
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
            echo "当前 Python 版本 ($PYTHON_VERSION) 低于 3.9，正在安装 Python 3.10..."
            $SUDO apt-get update -y
            $SUDO apt-get install -y python3.10 python3-pip python3.10-venv
            if [ $? -ne 0 ]; then
                echo "错误：Python 3.10 安装失败，请手动安装"
                exit 1
            fi
            PYTHON_CMD="python3.10"
            echo "Python 3.10 安装成功"
        else
            echo "Python 已安装，版本为 $PYTHON_VERSION"
        fi
    fi

    # 检查并安装 python3-venv
    if ! $PYTHON_CMD -m venv --help &> /dev/null; then
        echo "未找到 python3-venv 模块，正在安装 python3.${PYTHON_VERSION}-venv..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3.${PYTHON_VERSION}-venv
        if [ $? -ne 0 ]; then
            echo "错误：python3-venv 安装失败，请手动运行以下命令安装："
            echo "  $SUDO apt-get install python3.${PYTHON_VERSION}-venv"
            exit 1
        fi
        echo "python3-venv 安装成功"
    else
        echo "python3-venv 已安装"
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
        if [ $? -ne 0 ]; then
            echo "错误：虚拟环境创建失败，请检查 python3-venv 是否正确安装"
            echo "尝试手动安装：$SUDO apt-get install python3.${PYTHON_VERSION}-venv"
            exit 1
        fi
    fi

    # 激活虚拟环境
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        echo "虚拟环境已激活"
    else
        echo "错误：虚拟环境激活文件不存在，请检查虚拟环境是否创建成功"
        exit 1
    fi

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

# 函数：检查和初始化配置文件
check_config() {
    # 检查 tokens.txt
    if [ ! -f "tokens.txt" ]; then
        echo "未找到 tokens.txt 文件，正在创建默认文件..."
        cat << EOF > tokens.txt
# 请在此填入您的 token，每行一个
# 示例：
# token1
# token2
EOF
        echo "已创建 tokens.txt 文件，请编辑文件并填入您的 token 数据"
    else
        echo "tokens.txt 文件已存在，请确保已填入正确的 token 数据"
    fi

    # 检查 accounts.json
    if [ ! -f "accounts.json" ]; then
        echo "未找到 accounts.json 文件，正在创建默认文件..."
        cat << EOF > accounts.json
{
  "accounts": [
    {
      "token": "token1",
      "proxy": "http://user:pass@proxy1:port"
    },
    {
      "token": "token2",
      "proxy": "http://user:pass@proxy2:port"
    }
  ]
}
EOF
        echo "已创建 accounts.json 文件，请编辑文件并填入您的账户和代理信息"
    else
        echo "accounts.json 文件已存在，请确保已填入正确的账户信息"
    fi

    # 检查 proxy.txt
    if [ ! -f "proxy.txt" ]; then
        echo "未找到 proxy.txt 文件，正在创建默认文件..."
        cat << EOF > proxy.txt
# 请在此填入您的代理地址，每行一个
# 示例：
# http://user:pass@proxy1:port
# http://proxy2:port
EOF
        echo "已创建 proxy.txt 文件，请编辑文件并填入您的代理地址（如果需要）"
    else
        echo "proxy.txt 文件已存在，请确保已填入正确的代理地址（如果需要）"
    fi

    # 提示用户检查配置文件
    echo "请在运行程序前检查以下文件并填入必要信息："
    echo "  - tokens.txt：填入您的 token 数据"
    echo "  - accounts.json：填入账户和代理信息"
    echo "  - proxy.txt：填入代理地址（可选）"
    echo "您可以使用以下命令编辑文件："
    echo "  nano $PROJECT_DIR/tokens.txt"
    echo "  nano $PROJECT_DIR/accounts.json"
    echo "  nano $PROJECT_DIR/proxy.txt"
    echo "编辑完成后，重新运行脚本以启动程序。"
    exit 0
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
$PYTHON_CMD bot.py

# 退出虚拟环境
deactivate

echo "脚本执行完成"