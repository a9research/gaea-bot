# gaea-bot

### 项目简介
AiGaea-BOT 是一个自动化脚本项目，由 vonssy 开发，旨在通过 Python 脚本与 AiGaea 的 API 交互。它支持使用代理（包括 Monosans 代理、私有代理或无代理模式）运行多个账户，并提供自动获取账户信息和执行任务的功能。
### 前提条件
在开始之前，请确保您的系统满足以下要求：
操作系统：Linux、MacOS 或 Windows（推荐使用 Linux 或 MacOS，因为脚本是为 POSIX 系统设计的）。

Python 版本：3.9 或更高版本。

Git：用于克隆项目。

网络连接：用于下载依赖和访问 AiGaea 服务。

### 详细使用步骤
步骤 1：保存脚本
将上述代码保存为 run_aigaea.sh 文件，例如保存到 ~/aigaea 目录。
bash

nano ~/aigaea/run_aigaea.sh

复制代码，保存并退出（Ctrl+O，Ctrl+X）。

步骤 2：赋予执行权限
进入保存脚本的目录：
bash

cd ~/aigaea

添加执行权限：
bash

chmod +x run_aigaea.sh

步骤 3：运行脚本
执行脚本：
bash

./run_aigaea.sh

脚本会自动执行以下操作：
检查并安装 Git 和 Python 3.9（如果缺失）。

下载或更新 AiGaea-BOT 项目。

创建并激活虚拟环境。

安装项目依赖。

检查 tokens.txt 文件并提示配置。

运行 bot.py。

步骤 4：配置 tokens.txt
如果脚本提示缺少 tokens.txt，在 AiGaea-BOT 目录下创建文件：
bash

nano AiGaea-BOT/tokens.txt

输入 token，每行一个，例如：

token1
token2

保存并退出。

步骤 5：监控和停止
脚本运行后，观察终端输出，确保没有错误。

按 Ctrl+C 停止程序，脚本会自动退出虚拟环境。

注意事项
系统兼容性：脚本中的安装命令适用于 Debian/Ubuntu 系统。如果您使用其他系统（如 CentOS 或 Windows），需要修改 install_prerequisites 函数中的安装命令：
CentOS：将 apt-get 替换为 yum 或 dnf。

Windows：需手动安装 Git 和 Python，脚本无法自动安装。

权限要求：脚本可能需要 sudo 权限来安装组件。如果提示权限不足，请以 root 用户运行：
bash

sudo ./run_aigaea.sh

网络要求：确保可以访问 GitHub 和 PyPI。

故障排除
安装失败：如果 Git 或 Python 安装失败，检查网络或手动安装。

依赖错误：如果 pip install 失败，尝试手动运行：
bash

source AiGaea-BOT/aigaea_venv/bin/activate
pip install -r AiGaea-BOT/requirements.txt

