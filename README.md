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
#### 步骤 1：
新建一个工作目录
```
mkdir gaea
cd gaea
```

#### 步骤 2：
从github上拉取安装脚本并执行
```
wget -O run_aigaea.sh https://raw.githubusercontent.com/a9research/gaea-bot/refs/heads/main/run_aigaea.sh && sed -i 's/\r$//' run_aigaea.sh && chmod +x run_aigaea.sh && ./run_aigaea.sh
```



保存脚本
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

在项目目录下执行以下命令：

```bash
# 创建虚拟环境
python -m venv aigaea_venv

# 在 Linux/MacOS 上激活虚拟环境
source aigaea_venv/bin/activate

# 在 Windows 上激活虚拟环境
.\aigaea_venv\Scripts\activate
```

激活成功后，命令行前面会出现 (aigaea_venv) 的标识。

安装项目依赖。

在激活的虚拟环境中执行以下命令安装所需依赖：

```bash
# 确保 pip 是最新版本
pip install --upgrade pip

# 安装项目依赖
pip install aiohttp
pip install -r requirements.txt
```

如果遇到权限问题，可以尝试：
```bash
pip install --user aiohttp
pip install --user -r requirements.txt
```

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



如果我获取了新的token后应该怎么处理？用中文回答

如果你获取了新的token后，想要继续使用之前被暂停的账号，可以按照以下步骤处理：
更新暂停账号的token：
打开 paused_accounts.json 文件，找到对应账号的记录（通过 UID 或 Name 识别）。

将其中的 "Token" 字段替换为新获取的token。

保存文件。

将账号移回活跃状态：
有两种方法可以选择：
方法一：手动编辑文件
从 paused_accounts.json 中删除该账号的记录。

确保 accounts.csv 中仍然包含该账号的信息（如果之前被移除，需要手动添加回去）。

方法二：程序自动处理
你可以修改代码，添加一个功能来检测 paused_accounts.json 中的账号是否有了新的token，然后自动将其移回活跃状态。不过当前代码没有这个功能，需要额外开发。

重新运行程序：
运行程序时，它会从 accounts.csv 加载账号，而不会加载 paused_accounts.json 中仍存在的账号。

如果你已经从 paused_accounts.json 中移除了该账号的记录，并且 accounts.csv 中有正确的token，程序会正常处理这个账号。

示例操作
假设 paused_accounts.json 中有以下内容：
json

{
    "UID123": {
        "Name": "user1",
        "Browser_ID": "browser123",
        "Token": "old_expired_token",
        "Proxy": "http://proxy.example.com",
        "UID": "UID123",
        "paused_at": "04/08/25 12:00:00 WIB",
        "reason": "Token Expired (401)"
    }
}

你获取了新token，比如 new_valid_token。

编辑 paused_accounts.json，将 "Token": "old_expired_token" 改为 "Token": "new_valid_token"。

然后删除整个 "UID123" 的记录。

确保 accounts.csv 中有这一行：

Name,Browser_ID,Token,Proxy,UID
user1,browser123,new_valid_token,http://proxy.example.com,UID123

重新运行程序，账号 user1 就会恢复正常运行。





