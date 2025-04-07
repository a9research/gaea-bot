# gaea-bot

项目简介
AiGaea-BOT 是一个自动化脚本项目，由 vonssy 开发，旨在通过 Python 脚本与 AiGaea 的 API 交互。它支持使用代理（包括 Monosans 代理、私有代理或无代理模式）运行多个账户，并提供自动获取账户信息和执行任务的功能。
前提条件
在开始之前，请确保您的系统满足以下要求：
操作系统：Linux、MacOS 或 Windows（推荐使用 Linux 或 MacOS，因为脚本是为 POSIX 系统设计的）。

Python 版本：3.9 或更高版本。

Git：用于克隆项目。

网络连接：用于下载依赖和访问 AiGaea 服务。

详细使用步骤
步骤 1：安装必要的工具
安装 Python 3.9+：
Ubuntu/Debian：
bash

sudo apt update
sudo apt install python3.9 python3-pip python3-venv

CentOS/RHEL：
bash

sudo yum install python39 python39-pip

Windows：从 Python 官网 下载并安装。

验证安装：
bash

python3 --version

安装 Git：
Ubuntu/Debian：
bash

sudo apt install git

CentOS/RHEL：
bash

sudo yum install git

Windows：下载并安装 Git for Windows。

验证安装：
bash

git --version

步骤 2：下载 AiGaea-BOT 项目
打开终端（Windows 用户可使用 Git Bash 或 CMD）。

克隆项目到本地：
bash

git clone https://github.com/vonssy/AiGaea-BOT.git

进入项目目录：
bash

cd AiGaea-BOT

步骤 3：设置虚拟环境
创建 Python 虚拟环境：
bash

python3 -m venv aigaea_venv

激活虚拟环境：
Linux/MacOS：
bash

source aigaea_venv/bin/activate

Windows：
bash

aigaea_venv\Scripts\activate

激活后，终端提示符前会出现 (aigaea_venv)。

步骤 4：安装依赖
在虚拟环境中安装项目所需的 Python 包：
bash

pip install -r requirements.txt

如果遇到权限或网络问题，可尝试：
bash

pip install -r requirements.txt --user

步骤 5：配置 tokens.txt
在项目目录下找到 tokens.txt 文件（若没有，请创建一个）。

编辑 tokens.txt，添加您的 AiGaea token，每行一个。例如：

token1
token2

保存文件。token 的获取方式需参考 AiGaea 官方文档或社区支持（通常在注册 AiGaea 服务后提供）。

步骤 6：配置代理（可选）
如果您计划使用代理，在项目目录下找到 proxy.txt 文件（若没有，请创建）。

编辑 proxy.txt，添加代理地址，每行一个。例如：

http://user:pass@proxy1:port
http://proxy2:port

如果不使用代理，可跳过此步骤，脚本将以无代理模式运行。

步骤 7：运行项目
在虚拟环境中运行脚本：
bash

python bot.py

脚本启动后，会提示选择代理模式（Monosans 代理、私有代理或无代理），根据需要输入对应选项。

步骤 8：验证和监控
运行后，脚本会自动获取账户信息并执行任务。

检查终端输出，确认是否正常运行。如果遇到错误，请检查：
tokens.txt 是否正确配置。

网络连接是否稳定。

依赖是否完整安装。

步骤 9：退出
按 Ctrl+C 停止脚本。

退出虚拟环境：
bash

deactivate

注意事项
多账户支持：确保 tokens.txt 中列出所有账户的 token，脚本会自动处理多账户任务。

代理问题：如果代理不可用，脚本可能报错，请确保代理有效或选择无代理模式。

更新项目：定期运行 git pull 获取最新代码：
bash

git pull origin main

故障排除
依赖安装失败：尝试升级 pip：
bash

pip install --upgrade pip

网络错误：检查防火墙或代理设置。

脚本未运行：确保 Python 版本正确，且 bot.py 文件存在。

获取帮助
查看项目 GitHub 页面 的 README。

加入 vonssy 的 Telegram 频道（通常在项目描述中提供链接）寻求社区支持。

