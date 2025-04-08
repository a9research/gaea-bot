#!/bin/bash

# v1.1.4

# 定义变量
SCRIPT_DIR=$(dirname "$(realpath "$0")")
PROJECT_DIR="gaea-bot"
VENV_NAME="aigaea_venv"
PYTHON_CMD="python3"
MIN_VERSION="3.9"

# 检查 Python 版本
check_python_version() {
    echo "检查 Python 版本..."
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
    if [ -z "$PYTHON_VERSION" ]; then
        echo "错误：无法获取 Python 版本，请确保 $PYTHON_CMD 已正确安装"
        exit 1
    fi

    # 比较版本号
    if [ "$(printf '%s\n' "$PYTHON_VERSION" "$MIN_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
        echo "错误：Python 版本 $PYTHON_VERSION 不满足最低要求 $MIN_VERSION"
        exit 1
    fi
    echo "Python 版本 $PYTHON_VERSION 满足要求"
}

# 创建并激活虚拟环境
setup_venv() {
    echo "设置虚拟环境 $VENV_NAME..."

    # 检查虚拟环境是否已存在
    if [ ! -d "$VENV_NAME" ]; then
        echo "创建虚拟环境 $VENV_NAME..."
        $PYTHON_CMD -m venv "$VENV_NAME"
        if [ $? -ne 0 ]; then
            echo "错误：无法创建虚拟环境 $VENV_NAME"
            exit 1
        fi
    fi

    # 激活虚拟环境
    source "$VENV_NAME/bin/activate"
    if [ $? -ne 0 ]; then
        echo "错误：无法激活虚拟环境 $VENV_NAME"
        exit 1
    fi
    echo "虚拟环境 $VENV_NAME 已激活"
}

# 检查并创建 PROJECT_DIR
if [ ! -d "$PROJECT_DIR" ]; then
    echo "目录 $PROJECT_DIR 不存在，正在创建..."
    mkdir -p "$PROJECT_DIR"
    if [ $? -ne 0 ]; then
        echo "错误：无法创建目录 $PROJECT_DIR"
        exit 1
    fi
fi

# 切换到脚本所在目录
pushd "$SCRIPT_DIR" > /dev/null || {
    echo "错误：无法进入目录 $SCRIPT_DIR"
    exit 1
}

# 安装依赖的函数
install_requirements() {
    echo "正在安装依赖..."

    # 确保 pip 可用
    if ! command -v pip >/dev/null 2>&1; then
        echo "未找到 pip，正在安装..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y python3-pip
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y python3-pip
        else
            echo "错误：无法安装 pip，请手动安装"
            exit 1
        fi
    fi

    # 升级 pip 并安装依赖
    pip install --upgrade pip
    pip install aiohttp==3.9.* aiohttp-socks==0.8.* pyyaml==6.0.* async-timeout==4.0.* colorama==0.4.* attrs==23.2.* fake-useragent==1.5.* frozenlist==1.4.* multidict==6.0.* yarl==1.9.* aiohappyeyeballs==2.4.* aiosignal==1.3.* --force-reinstall
}

# 配置文件的函数
configure_files() {
    pushd "$PROJECT_DIR" > /dev/null || {
        echo "错误：无法进入目录 $PROJECT_DIR"
        popd > /dev/null
        exit 1
    }

    # 配置文件的逻辑
    echo "请输入要登录的账号/密码（输入完成后按 Enter 键继续）"
    declare -a names
    declare -a browser_ids
    declare -a tokens
    declare -a proxies
    declare -a index=1

    while true; do
        read -p "用户名（输入完成后按 Enter 键继续）: " name
        if [ -z "$name" ]; then
            break
        fi
        read -p "浏览器ID（输入完成后按 Enter 键继续）: " browser_id
        read -p "Token（输入完成后按 Enter 键继续）: " token
        read -p "代理（输入完成后按 Enter 键继续）: " proxy

        names+=("$name")
        browser_ids+=("$browser_id")
        tokens+=("$token")
        proxies+=("$proxy")
        index=$((index + 1))
    done

    if [ ${#names[@]} -eq 0 ]; then
        echo "错误：未输入任何账号信息"
        popd > /dev/null
        exit 1
    fi

    # 写入 accounts.csv
    echo "name,browser_id,token,proxy" > accounts.csv
    for ((i = 0; i < ${#names[@]}; i++)); do
        echo "${names[$i]},${browser_ids[$i]},${tokens[$i]},${proxies[$i]}" >> accounts.csv
    done

    popd > /dev/null
}

# 运行程序的函数
run_program() {
    pushd "$PROJECT_DIR" > /dev/null || {
        echo "错误：无法进入目录 $PROJECT_DIR"
        popd > /dev/null
        exit 1
    }

    # 检查 accounts.csv 是否存在
    if [ ! -f "accounts.csv" ]; then
        echo "错误：未找到 accounts.csv 文件"
        popd > /dev/null
        exit 1
    fi

    # 运行 Python 脚本
    python main.py

    popd > /dev/null
}

# 主逻辑
main() {
    check_python_version
    setup_venv
    install_requirements
    configure_files
    run_program
}

# 捕获中断信号
trap 'echo "程序被中断"; deactivate 2>/dev/null; popd > /dev/null; exit 1' SIGINT SIGTERM

# 运行主函数
main

# 清理：退出虚拟环境并恢复目录
deactivate 2>/dev/null
popd > /dev/null