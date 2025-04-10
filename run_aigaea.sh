#!/bin/bash

# v1.1.15

# 定义项目目录和虚拟环境名称
SCRIPT_ROOT=$(dirname "$(realpath "$0")")  # 保存脚本的根目录（绝对路径）
PROJECT_DIR="gaea-bot"
VENV_NAME="aigaea_venv"
PYTHON_CMD="python3"  # 默认命令，稍后会动态调整
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
        echo "未找到 Python，正在尝试安装 Python 3.10..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3.10 python3.10-pip python3.10-venv
        if [ $? -ne 0 ]; then
            echo "错误：Python 3.10 安装失败，请手动安装 Python 3.9 或更高版本"
            exit 1
        fi
        PYTHON_CMD="python3.10"
        echo "Python 3.10 安装成功"
    else
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        echo "当前 Python 版本: $PYTHON_VERSION (通过 $PYTHON_CMD)"
        if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
            echo "当前 Python 版本 ($PYTHON_VERSION) 低于 3.9，正在安装 Python 3.10..."
            $SUDO apt-get update -y
            $SUDO apt-get install -y python3.10 python3.10-pip python3.10-venv
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

    # 动态获取 Python 主版本号
    PYTHON_MAJOR_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    echo "当前使用的 Python 主版本号: $PYTHON_MAJOR_VERSION"

    # 检查并安装 python3-venv
    if ! $PYTHON_CMD -m venv --help &> /dev/null; then
        echo "未找到 python3-venv 模块，正在安装 python3-${PYTHON_MAJOR_VERSION}-venv..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3-${PYTHON_MAJOR_VERSION}-venv
        if [ $? -ne 0 ]; then
            echo "错误：python3-venv 安装失败，请手动运行以下命令安装："
            echo "  $SUDO apt-get install python3-${PYTHON_MAJOR_VERSION}-venv"
            exit 1
        fi
        echo "python3-venv 安装成功，重新验证环境..."
        # 安装后重新检查
        if ! $PYTHON_CMD -m venv --help &> /dev/null; then
            echo "错误：即使安装了 python3-${PYTHON_MAJOR_VERSION}-venv，venv 模块仍然不可用"
            echo "请检查 $PYTHON_CMD 是否正确指向 Python $PYTHON_MAJOR_VERSION"
            exit 1
        fi
    else
        echo "python3-venv 已安装"
    fi

    # 调试信息：显示 Python 路径和版本
    PYTHON_PATH=$(which $PYTHON_CMD)
    echo "当前 Python 可执行文件路径: $PYTHON_PATH"
    echo "当前 Python 完整版本: $($PYTHON_CMD --version)"
}

# 函数：克隆或更新项目
clone_or_update_project() {
    pushd "$SCRIPT_ROOT" > /dev/null || {
        echo "错误：无法进入脚本根目录 $SCRIPT_ROOT"
        exit 1
    }

    if [ -d "$PROJECT_DIR" ]; then
        echo "更新现有项目..."
        pushd "$PROJECT_DIR" > /dev/null || {
            echo "错误：无法进入目录 $PROJECT_DIR"
            popd > /dev/null
            exit 1
        }
        git pull origin main
        popd > /dev/null
    else
        echo "克隆项目..."
        git clone https://github.com/a9research/gaea-bot.git
    fi

    popd > /dev/null
}

# 函数：设置虚拟环境和依赖
setup_environment() {
    pushd "$SCRIPT_ROOT" > /dev/null || {
        echo "错误：无法进入脚本根目录 $SCRIPT_ROOT"
        exit 1
    }

    pushd "$PROJECT_DIR" > /dev/null || {
        echo "错误：无法进入目录 $PROJECT_DIR"
        popd > /dev/null
        exit 1
    }

    if [ ! -d "$VENV_NAME" ]; then
        echo "创建虚拟环境..."
        $PYTHON_CMD -m venv "$VENV_NAME"
        if [ $? -ne 0 ]; then
            echo "错误：虚拟环境创建失败，请检查以下内容："
            echo "1. 是否正确安装 python3-${PYTHON_MAJOR_VERSION}-venv"
            echo "2. 当前 Python 命令 ($PYTHON_CMD) 是否支持 venv 模块"
            echo "尝试手动安装：$SUDO apt-get install python3-${PYTHON_MAJOR_VERSION}-venv"
            exit 1
        fi
        echo "虚拟环境创建成功"
    else
        echo "虚拟环境已存在"
    fi

    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        echo "虚拟环境已激活"
    else
        echo "错误：虚拟环境激活文件不存在，请检查虚拟环境是否创建成功"
        popd > /dev/null
        exit 1
    fi

    echo "升级 pip..."
    pip install --upgrade pip

    echo "安装项目依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误：依赖安装失败，请检查网络或 requirements.txt 文件"
        popd > /dev/null
        exit 1
    fi

    popd > /dev/null
    popd > /dev/null
}

# 函数：收集用户输入并生成 accounts.csv
configure_files() {
    pushd "$SCRIPT_ROOT" > /dev/null || {
        echo "错误：无法进入脚本根目录 $SCRIPT_ROOT"
        exit 1
    }

    pushd "$PROJECT_DIR" > /dev/null || {
        echo "错误：无法进入目录 $PROJECT_DIR"
        popd > /dev/null
        exit 1
    }

    echo "请配置您的账户信息（输入完成后按 Enter 继续）"
    declare -a names
    declare -a browser_ids
    declare -a tokens
    declare -a uids
    declare -a proxies
    account_index=1

    while true; do
        echo "请输入第 $account_index 个账户的名称（用于标记，直接按 Enter 结束输入）："
        read name
        if [ -z "$name" ]; then
            break
        fi
        names+=("$name")

        echo "请输入第 $account_index 个账户的 Browser_ID："
        read browser_id
        if [ -z "$browser_id" ]; then
            echo "错误：Browser_ID 不能为空，请重新输入"
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

        echo "请输入第 $account_index 个账户的 UID："
        read uid
        if [ -z "$uid" ]; then
            echo "错误：UID 不能为空，请重新输入"
            continue
        fi
        uids+=("$uid")

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

    if [ ${#tokens[@]} -eq 0 ]; then
        echo "错误：至少需要输入一个账户（Browser_ID、Token 和 UID）才能继续"
        popd > /dev/null
        exit 1
    fi

    echo "正在生成 accounts.csv 文件..."
    echo "Name,Browser_ID,Token,Proxy,UID" > accounts.csv
    for i in "${!tokens[@]}"; do
        name="${names[$i]//,/}"
        browser_id="${browser_ids[$i]//,/}"
        token="${tokens[$i]//,/}"
        proxy="${proxies[$i]:-""}"
        uid="${uids[$i]//,/}"
        echo "生成第 $((i+1)) 行: $name,$browser_id,$token,$proxy,$uid"
        echo "$name,$browser_id,$token,$proxy,$uid" >> accounts.csv
    done

    echo "生成的文件内容如下："
    cat accounts.csv
    echo "accounts.csv 已生成"

    popd > /dev/null
    popd > /dev/null
}

# 函数：运行项目
run_project() {
    pushd "$SCRIPT_ROOT" > /dev/null || {
        echo "错误：无法进入脚本根目录 $SCRIPT_ROOT"
        exit 1
    }

    pushd "$PROJECT_DIR" > /dev/null || {
        echo "错误：无法进入目录 $PROJECT_DIR"
        popd > /dev/null
        exit 1
    }

    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        echo "虚拟环境已激活"
    else
        echo "错误：虚拟环境未找到，请先运行安装流程"
        popd > /dev/null
        popd > /dev/null
        exit 1
    fi

    echo "启动 AiGaea-BOT..."
    $PYTHON_CMD bot.py

    deactivate

    popd > /dev/null
    popd > /dev/null
}

# 函数：安装 GaeaBot
install_gaeabot() {
    echo "开始安装 AiGaea-BOT..."

    install_prerequisites
    clone_or_update_project
    setup_environment
    configure_files

    echo "AiGaea-BOT 安装完成"
}

# 函数：显示菜单
show_menu() {
    while true; do
        echo ""
        echo "===== AiGaea-BOT 管理菜单 ====="
        echo "1. 安装 GaeaBot"
        echo "2. 运行 GaeaBot"
        echo "3. 退出"
        echo "=============================="
        echo -n "请选择一个选项 [1-3]: "
        read choice

        case $choice in
            1)
                install_gaeabot
                ;;
            2)
                run_project
                ;;
            3)
                echo "退出脚本..."
                exit 0
                ;;
            *)
                echo "无效选项，请输入 1、2 或 3"
                ;;
        esac
    done
}

# 主流程：显示菜单
echo "欢迎使用 AiGaea-BOT 脚本"
show_menu