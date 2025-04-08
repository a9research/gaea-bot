import aiohttp
import asyncio
import aiohttp_socks
import random
import time
import sys
from colorama import Fore, init
from fake_useragent import UserAgent
import pandas as pd  # 用于读取 CSV 文件

init(autoreset=True)

class AiGaea:
    def __init__(self):
        self.ua = UserAgent()
        self.accounts = self.load_accounts()

    def load_accounts(self):
        """从 accounts.csv 加载账户信息（包含 Browser_ID、Token 和 Proxy）"""
        print(f"{Fore.CYAN}正在加载账户信息...")
        try:
            df = pd.read_csv('accounts.csv')
            required_columns = ['Browser_ID', 'Token', 'Proxy']
            if not all(col in df.columns for col in required_columns):
                print(f"{Fore.RED}错误：accounts.csv 文件必须包含 'Browser_ID'、'Token' 和 'Proxy' 列")
                sys.exit(1)
            # 替换 NaN 为空字符串（处理 Proxy 为空的情况）
            df['Proxy'] = df['Proxy'].fillna('')
            # 截取 Browser_ID 的前 8 位
            df['Browser_ID'] = df['Browser_ID'].apply(lambda x: x[:8])
            # 验证 Browser_ID 截取后是否为 8 位
            if not all(df['Browser_ID'].str.len() == 8):
                print(f"{Fore.RED}错误：accounts.csv 中的 Browser_ID 截取前 8 位后长度不正确")
                sys.exit(1)
            accounts = df[required_columns].to_dict('records')
            print(f"{Fore.GREEN}成功加载 {len(accounts)} 个账户")
            return accounts
        except FileNotFoundError:
            print(f"{Fore.RED}错误：未找到 accounts.csv 文件，请创建该文件")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}错误：加载 accounts.csv 文件失败 - {e}")
            sys.exit(1)

    async def get_account_info(self, session, account, proxy):
        """获取账户信息"""
        browser_id = account['Browser_ID']  # 已截取为前 8 位
        token = account['Token']
        headers = {
            'Authorization': f'Bearer {token}',
            'Origin': 'https://app.aigaea.io',
            'Referer': 'https://app.aigaea.io/',
            'User-Agent': self.ua.random,
            'X-Browser-Id': browser_id,
        }
        url = 'https://api.aigaea.io/api/user'
        try:
            async with session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"{Fore.GREEN}账户信息获取成功 - Browser_ID: {browser_id}")
                    return data
                else:
                    print(f"{Fore.RED}账户信息获取失败 - Browser_ID: {browser_id} - 状态码: {response.status}")
                    return None
        except Exception as e:
            print(f"{Fore.RED}账户信息获取失败 - Browser_ID: {browser_id} - 错误: {e}")
            return None

    async def run_with_private_proxy(self):
        """使用私有代理运行"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for account in self.accounts:
                proxy = account['Proxy'] if account['Proxy'] else None
                if proxy:
                    connector = aiohttp_socks.ProxyConnector.from_url(proxy)
                    session_with_proxy = aiohttp.ClientSession(connector=connector)
                    task = self.get_account_info(session_with_proxy, account, proxy)
                    tasks.append(task)
                else:
                    task = self.get_account_info(session, account, None)
                    tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

    async def run_without_proxy(self):
        """不使用代理运行"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for account in self.accounts:
                task = self.get_account_info(session, account, None)
                tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

    async def run(self, choice):
        """根据用户选择运行程序"""
        if choice == 1:
            print(f"{Fore.CYAN}使用私有代理运行...")
            return await self.run_with_private_proxy()
        elif choice == 2:
            print(f"{Fore.CYAN}不使用代理运行...")
            return await self.run_without_proxy()
        else:
            print(f"{Fore.RED}无效的选择")
            return []

def main():
    bot = AiGaea()
    print(f"{Fore.YELLOW}1. 使用私有代理运行")
    print(f"{Fore.YELLOW}2. 不使用代理运行")
    while True:
        try:
            choice = int(input(f"{Fore.CYAN}选择 [1/2] -> "))
            if choice in [1, 2]:
                break
            print(f"{Fore.RED}无效的选择，请输入 1 或 2")
        except ValueError:
            print(f"{Fore.RED}请输入数字 1 或 2")

    start_time = time.time()
    results = asyncio.run(bot.run(choice))
    end_time = time.time()
    print(f"{Fore.GREEN}任务完成，耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()