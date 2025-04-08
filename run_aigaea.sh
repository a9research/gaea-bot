#!/bin/bash

# v1.1.3

# 定义项目目录和虚拟环境名称
PROJECT_DIR="gaea-bot"
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
        git clone https://github.com/a9research/gaea-bot.git
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

# 函数：收集用户输入并生成 accounts.csv
configure_files() {
    echo "PROJECT_DIR 的值是: $PROJECT_DIR"
    cd "$PROJECT_DIR" || {
        echo "错误：无法进入目录 $PROJECT_DIR"
        exit 1
    }

    echo "请配置您的账户信息（输入完成后按 Enter 继续）"
    declare -a names
    declare -a browser_ids
    declare -a tokens
    declare -a proxies
    account_index=1

    while true; do
        echo "请输入第 $account_index 个账户的名称（用于标记，直接按 Enter 结束输入）："
        read name
        if [ -z "$name" ]; then
            break
        fi
        names+=("$name")

        echo "请输入第 $account_index 个账户的 Browser_ID（前 8 位）："
        read browser_id
        if [ ${#browser_id} -ne 8 ]; then
            echo "错误：Browser_ID 必须为 8 位，请重新输入"
            continue
        fi
        browser_ids+=("$browser_id")

        echo "请输入第 $account_index 个账户的 Token："
        read token
        if [ -z "$token" ]; then
            echo "错误：Token 不能为空，请重新输入"
            continue
        fi
        tokens+=("$token")

        echo "请输入第 $account_index 个账户的代理地址（格式：protocol://user:pass@ip:port，直接按 Enter 跳过）："
        read proxy
        if [ -n "$proxy" ]; then
            if [[ ! "$proxy" =~ ^[a-z]+://[a-zA-Z0-9]+:[a-zA-Z0-9]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$ ]]; then
                echo "警告：代理地址 $proxy 格式可能不正确，应为 protocol://user:pass@ip:port"
            fi
        fi
        proxies+=("$proxy")

        account_index=$((account_index + 1))
    done

    # 检查是否至少输入了一个账户
    if [ ${#tokens[@]} -eq 0 ]; then
        echo "错误：至少需要输入一个账户（Browser_ID 和 Token）才能继续"
        exit 1
    fi

    # 生成 accounts.csv
    echo "正在生成 accounts.csv 文件..."
    echo "Name,Browser_ID,Token,Proxy" > accounts.csv
    for i in "${!tokens[@]}"; do
        name=${names[$i]}
        browser_id=${browser_ids[$i]}
        token=${tokens[$i]}
        proxy=${proxies[$i]:-""}  # 如果 proxy 为空，使用空字符串
        echo "$name,$browser_id,$token,$proxy" >> accounts.csv
    done
    echo "accounts.csv 已生成"
}

# 主流程
echo "开始运行 AiGaea-BOT 脚本..."

# 安装前置组件
install_prerequisites

# 克隆或更新项目
clone_or_update_project

# 设置虚拟环境和依赖
setup_environment

# 配置 accounts.csv
configure_files

# 运行项目
echo "启动 AiGaea-BOT..."
$PYTHON_CMD bot.py

# 退出虚拟环境
deactivate

echo "脚本执行完成"