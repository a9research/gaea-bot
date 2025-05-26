from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime, timedelta
from colorama import *
import asyncio, time, os, pytz, csv, random, json, logging

wib = pytz.timezone('Asia/Jakarta')

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aigaea.log', encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

class AiGaea:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.aigaea.net",
            "Referer": "https://app.aigaea.net/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.accounts = []
        self.paused_accounts_file = "paused_accounts.json"
        self.training_records_file = "training_records.json"
        self.paused_accounts = self.load_paused_accounts()
        self.training_records = self.load_training_records()

    def load_paused_accounts(self):
        try:
            if os.path.exists(self.paused_accounts_file):
                with open(self.paused_accounts_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading paused accounts: {e}")
            return {}

    def load_training_records(self):
        try:
            if os.path.exists(self.training_records_file):
                with open(self.training_records_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading training records: {e}")
            return {}

    def save_paused_account(self, account_data):
        self.paused_accounts[account_data['UID']] = {
            'Name': account_data['Name'],
            'Browser_ID': account_data['Browser_ID'],
            'Token': account_data['Token'],
            'Proxy': account_data['Proxy'],
            'UID': account_data['UID'],
            'paused_at': datetime.now().astimezone(wib).strftime('%x %X %Z'),
            'reason': 'Token Expired (401)'
        }
        with open(self.paused_accounts_file, 'w') as f:
            json.dump(self.paused_accounts, f, indent=4)

    def save_training_record(self, account_data):
        uid = account_data['UID']
        current_date = datetime.now(pytz.UTC).strftime('%Y-%m-%d')
        
        if uid not in self.training_records:
            self.training_records[uid] = {}
            
        self.training_records[uid][current_date] = {
            'Name': account_data['Name'],
            'Browser_ID': account_data['Browser_ID'],
            'Token': account_data['Token'],
            'Proxy': account_data['Proxy'],
            'UID': uid,
            'trained_at': datetime.now().astimezone(wib).strftime('%x %X %Z')
        }
        
        with open(self.training_records_file, 'w') as f:
            json.dump(self.training_records, f, indent=4)

    def check_training_status(self, uid):
        current_date = datetime.now(pytz.UTC).strftime('%Y-%m-%d')
        return uid in self.training_records and current_date in self.training_records[uid]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}AI Gaea - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.csv"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                expected_fields = ['Name', 'Browser_ID', 'Token', 'Proxy', 'UID']
                if reader.fieldnames != expected_fields:
                    self.log(f"{Fore.RED}Invalid CSV format. Required fields: {', '.join(expected_fields)}{Style.RESET_ALL}")
                    return
                self.accounts = [acc for acc in reader if acc['UID'] not in self.paused_accounts]
        except Exception as e:
            self.log(f"{Fore.RED}Error loading accounts: {e}{Style.RESET_ALL}")
            return

    def check_proxy_schemes(self, proxy):
        if not proxy:
            return None
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxy.startswith(scheme) for scheme in schemes):
            return proxy
        return f"http://{proxy}"

    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    def print_message(self, account, proxy, color, message):
        proxy_display = proxy if proxy else "No Proxy"
        log_message = f"[ Account: {account} - Proxy: {proxy_display} - Status: {message} ]"
        self.log(log_message)
        # 同时记录到日志文件
        logging.info(log_message)
        # 打印彩色消息到控制台
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {account} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy_display}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Private Proxy")
                print("2. Run Without Proxy")
                choose = int(input("Choose [1/2] -> ").strip())

                if choose in [1, 2]:
                    proxy_type = (
                        "Run With Private Proxy" if choose == 1 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    
                    # 添加训练选项
                    while True:
                        try:
                            trained = input("Auto Complete Training? Will Burned 0-2500 PTS (y/n) ->").strip().lower()
                            if trained in ["y", "n"]:
                                trained = trained == "y"
                                break
                            else:
                                print(f"{Fore.RED + Style.BRIGHT}Enter 'y' to Yes or 'n' to Skip.{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' to Yes or 'n' to Skip.{Style.RESET_ALL}")
                    
                    return choose, trained
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

    async def user_earning(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/earn/info"
        headers = {
            **self.headers,
            "Accept-Language": "he",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Priority": "u=1, i"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("success") is not True:
                            raise ValueError(f"API returned unsuccessful response: {result.get('msg')}")
                        return result['data']
            except ClientResponseError as e:
                if e.status == 401:
                    return "TOKEN_EXPIRED"
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def process_user_earning(self, token: str, username: str, account_data: dict, proxy=None):
        while True:
            try:
                earning = await self.user_earning(token, username, proxy)
                if earning == "TOKEN_EXPIRED":
                    self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Pausing Account")
                    self.save_paused_account(account_data)
                    return
                if earning:
                    total_points = earning['total_total']  # Use total_total for Earning Total
                    today_points = earning['today_total']  # Use today_total for Today Total
                    uptime_minutes = earning['today_uptime']  # Uptime in minutes
                    uptime_hours = uptime_minutes / 60  # Convert to hours
                    self.print_message(username, proxy, Fore.WHITE,
                        f"Earning Total {total_points} PTS "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Today Total: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{today_points} PTS "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Uptime: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{uptime_hours:.2f} Hours{Style.RESET_ALL}"
                    )
            except Exception as e:
                logging.error("User Earning Failed", extra={"account": username, "proxy": proxy if proxy else "No Proxy", "message": str(e)})
                self.print_message(username, proxy, Fore.RED, f"User Earning Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

            await asyncio.sleep(15 * 60)

    async def send_ping(self, token: str, browser_id: str, username: str, user_id: str, proxy=None, retries=2, ping_type="extension"):
        url = "https://api.aigaea.net/api/network/ping"
        version = "3.0.19"
        data = json.dumps({
            "browser_id": browser_id,
            "timestamp": int(time.time()),  
            "uid": user_id,
            "version": version
        })
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://cpjicfogbgognnifjgmenmaldnmeeeib" if ping_type == "extension" else "https://app.aigaea.net",
            "Priority": "u=1, i",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none" if ping_type == "extension" else "same-site",
            "User-Agent": FakeUserAgent().random
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        content_type = response.headers.get('Content-Type', '')
                        text = await response.text(encoding=None)
                        self.log(f"{Fore.YELLOW}Raw response for {username} ({ping_type}): {text[:100]}{Style.RESET_ALL}")
                        if 'application/json' not in content_type.lower():
                            raise ValueError(f"Response is not JSON: {text[:100]}")
                        try:
                            result = json.loads(text)
                        except UnicodeDecodeError as e:
                            self.log(f"{Fore.YELLOW}UTF-8 decode failed, trying Latin-1 for {username} ({ping_type}){Style.RESET_ALL}")
                            text = await response.text(encoding='latin-1')
                            result = json.loads(text)
                        if result.get("code") == 401:  # 检查响应中的code是否为401
                            return "TOKEN_EXPIRED"
                        return result['data']
            except ClientResponseError as e:
                if e.status == 401:  # 检查HTTP状态码是否为401
                    return "TOKEN_EXPIRED"
                if e.status == 403:  # 检查HTTP状态码是否为403
                    return "ACCOUNT_FORBIDDEN"
                if attempt < retries - 1:
                    self.log(f"{Fore.YELLOW}Retrying {ping_type} ping for {username} (attempt {attempt + 1}/{retries})...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"{ping_type.upper()} PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            except Exception as e:
                if attempt < retries - 1:
                    self.log(f"{Fore.YELLOW}Retrying {ping_type} ping for {username} (attempt {attempt + 1}/{retries})...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"{ping_type.upper()} PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None

    async def process_send_ping(self, token: str, browser_id: str, username: str, user_id: str, account_data: dict, proxy=None, ping_type="extension"):
        while True:
            try:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try to Send {ping_type.capitalize()} Ping...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                ping = await self.send_ping(token, browser_id, username, user_id, proxy, ping_type=ping_type)
                if ping == "TOKEN_EXPIRED":
                    self.print_message(username, proxy, Fore.RED, f"Token Expired (401) - Pausing Account ({ping_type})")
                    self.save_paused_account(account_data)
                    return
                if ping == "ACCOUNT_FORBIDDEN":
                    self.print_message(username, proxy, Fore.RED, f"Account Forbidden (403) - Pausing Account ({ping_type})")
                    self.save_paused_account(account_data)
                    return
                if ping:
                    score = ping['score']
                    self.print_message(username, proxy, Fore.GREEN,
                        f"{ping_type.upper()} PING Success"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Network Score:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {score} {Style.RESET_ALL}"
                    )
            except Exception as e:
                logging.error(f"Send {ping_type.capitalize()} Ping Failed", extra={"account": username, "proxy": proxy if proxy else "No Proxy", "message": str(e)})
                self.print_message(username, proxy, Fore.RED, f"Send {ping_type.upper()} Ping Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

            wait_time = 10 * 60
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For {self.format_seconds(wait_time)} For Next {ping_type.capitalize()} Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(wait_time)

    async def complete_training(self, token: str, username: str, proxy=None, retries=2):
        url = "https://api.aigaea.net/api/ai/complete"
        data = json.dumps({"detail":"3_0_1"})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Content-Length": str(len(data))
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("success") is not True:
                            # 如果是训练已完成的情况，直接返回结果
                            if result.get("msg") == "Training already completed":
                                return result
                            raise ValueError(f"API returned unsuccessful response: {result.get('msg')}")
                        return result
            except ClientResponseError as e:
                if e.status == 401:
                    return "TOKEN_EXPIRED"
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Complete Training Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Complete Training Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None

    async def get_soul_balance(self, token: str, username: str, proxy=None, retries=2):
        url = "https://api.aigaea.net/api/ai/list"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Priority": "u=1, i"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("success") is not True:
                            raise ValueError(f"API returned unsuccessful response: {result.get('msg')}")
                        return result
            except ClientResponseError as e:
                if e.status == 401:
                    return "TOKEN_EXPIRED"
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Get Soul Balance Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Get Soul Balance Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None

    async def get_daily_rewards(self, token: str, username: str, proxy=None, retries=2):
        url = "https://api.aigaea.net/api/reward/daily-list"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Priority": "u=1, i"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("success") is not True:
                            raise ValueError(f"API returned unsuccessful response: {result.get('msg')}")
                        return result['data']
            except ClientResponseError as e:
                if e.status == 401:
                    return "TOKEN_EXPIRED"
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Get Daily Rewards Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Get Daily Rewards Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None

    async def claim_daily_reward(self, token: str, username: str, reward_id: int, proxy=None, retries=2):
        url = "https://api.aigaea.net/api/reward/daily-complete"
        data = json.dumps({"id": reward_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Content-Length": str(len(data))
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("success") is not True:
                            raise ValueError(f"API returned unsuccessful response: {result.get('msg')}")
                        return result['data']
            except ClientResponseError as e:
                if e.status == 401:
                    return "TOKEN_EXPIRED"
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Claim Daily Reward Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"Claim Daily Reward Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None

    async def process_daily_reward(self, token: str, username: str, account_data: dict, proxy=None):
        while True:
            try:
                # 获取当前UTC时间
                current_utc = datetime.now(pytz.UTC)
                # 计算今天的UTC 0:00
                today_utc = current_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                # 计算下一个UTC 0:00
                next_utc = today_utc + timedelta(days=1)
                
                # 生成今天的随机领取时间（UTC 0-24点之间）
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                today_reward_time = today_utc.replace(hour=random_hour, minute=random_minute, second=random_second)
                
                # 如果当前时间已经过了今天的随机时间，在当前时间和24点之间生成新的随机时间
                # 但是要排除当前时间是UTC 0:00的情况
                if current_utc >= today_reward_time and current_utc != today_utc:
                    # 计算当前时间到24点的秒数
                    remaining_seconds = (next_utc - current_utc).total_seconds()
                    # 生成一个0到剩余秒数之间的随机等待时间
                    random_wait_seconds = random.randint(0, int(remaining_seconds))
                    # 计算新的随机时间点
                    new_reward_time = current_utc + timedelta(seconds=random_wait_seconds)
                    self.print_message(username, proxy, Fore.BLUE, 
                        f"Original reward time ({today_reward_time.strftime('%H:%M:%S')} UTC) has passed, "
                        f"will try at {new_reward_time.strftime('%H:%M:%S')} UTC")
                    await asyncio.sleep(random_wait_seconds)
                else:
                    # 计算到随机领取时间的等待时间
                    wait_seconds = (today_reward_time - current_utc).total_seconds()
                    self.print_message(username, proxy, Fore.BLUE, 
                        f"Waiting for reward time: {today_reward_time.strftime('%H:%M:%S')} UTC")
                    await asyncio.sleep(wait_seconds)

                # 到达随机时间后，获取每日奖励列表
                self.print_message(username, proxy, Fore.BLUE, "Getting Daily Rewards...")
                daily_rewards = await self.get_daily_rewards(token, username, proxy)
                if daily_rewards == "TOKEN_EXPIRED":
                    self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Pausing Account")
                    self.save_paused_account(account_data)
                    return

                if daily_rewards:
                    # 检查今天是否已经领取过奖励
                    if daily_rewards.get('today') == 1:
                        self.print_message(username, proxy, Fore.YELLOW, "Daily reward already claimed today")
                        # 如果已经领取过奖励，等待到下一个UTC 0:00
                        wait_seconds = (next_utc - current_utc).total_seconds()
                        self.print_message(username, proxy, Fore.BLUE, 
                            f"Next daily reward check will be in {self.format_seconds(wait_seconds)}")
                        await asyncio.sleep(wait_seconds)
                        continue
                    else:
                        # 找到未领取的奖励
                        available_rewards = [reward for reward in daily_rewards['list'] if not reward['reward']]
                        if available_rewards:
                            # 随机选择一个未领取的奖励
                            selected_reward = random.choice(available_rewards)
                            reward_id = selected_reward['daily']
                            
                            self.print_message(username, proxy, Fore.BLUE, f"Claiming Daily Reward (ID: {reward_id})...")
                            reward_data = await self.claim_daily_reward(token, username, reward_id, proxy)
                            if reward_data == "TOKEN_EXPIRED":
                                self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Pausing Account")
                                self.save_paused_account(account_data)
                                return

                            if reward_data:
                                soul = reward_data.get('soul', 0)
                                core = reward_data.get('core', 0)
                                blindbox = reward_data.get('blindbox', 0)
                                self.print_message(username, proxy, Fore.GREEN,
                                    "Daily Reward Claimed "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{soul} Soul PTS{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{core} Core{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{blindbox} Blindbox{Style.RESET_ALL}"
                                )
                                # 领取奖励后等待到下一个UTC 0:00
                                wait_seconds = (next_utc - current_utc).total_seconds()
                                self.print_message(username, proxy, Fore.BLUE, 
                                    f"Next daily reward check will be in {self.format_seconds(wait_seconds)}")
                                await asyncio.sleep(wait_seconds)
                                continue
                        else:
                            self.print_message(username, proxy, Fore.YELLOW, "No Available Daily Rewards")
                            # 如果没有可用奖励，等待到下一个UTC 0:00
                            wait_seconds = (next_utc - current_utc).total_seconds()
                            self.print_message(username, proxy, Fore.BLUE, 
                                f"Next daily reward check will be in {self.format_seconds(wait_seconds)}")
                            await asyncio.sleep(wait_seconds)
                            continue

            except Exception as e:
                # 处理未预期的异常（如网络错误、连接超时等）
                logging.error("Daily Reward Failed", extra={"account": username, "proxy": proxy if proxy else "No Proxy", "message": str(e)})
                self.print_message(username, proxy, Fore.RED, f"Unexpected Error: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                await asyncio.sleep(60)  # 发生未预期错误时等待1分钟后重试

    async def process_complete_training(self, token: str, username: str, account_data: dict, proxy=None):
        while True:
            try:
                # 检查今天是否已经训练过
                if self.check_training_status(account_data['UID']):
                    current_utc = datetime.now(pytz.UTC)
                    today_utc = current_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                    next_utc = today_utc + timedelta(days=1)
                    wait_seconds = (next_utc - current_utc).total_seconds()
                    self.print_message(username, proxy, Fore.YELLOW, "Training Already Completed Today (Local Record)")
                    self.print_message(username, proxy, Fore.BLUE, 
                        f"Waiting for next day's training")
                    await asyncio.sleep(wait_seconds)
                    continue

                # 获取当前UTC时间
                current_utc = datetime.now(pytz.UTC)
                # 计算今天的UTC 0:00
                today_utc = current_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                # 计算下一个UTC 0:00
                next_utc = today_utc + timedelta(days=1)
                
                # 生成今天的随机训练时间（UTC 0-24点之间）
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                today_training_time = today_utc.replace(hour=random_hour, minute=random_minute, second=random_second)
                
                # 如果当前时间已经过了今天的训练时间，在当前时间到24点之间生成新的随机时间
                if current_utc >= today_training_time:
                    # 计算当前时间到24点的秒数
                    remaining_seconds = (next_utc - current_utc).total_seconds()
                    # 生成一个0到剩余秒数之间的随机等待时间
                    random_wait_seconds = random.randint(0, int(remaining_seconds))
                    # 计算新的随机时间点
                    new_training_time = current_utc + timedelta(seconds=random_wait_seconds)
                    self.print_message(username, proxy, Fore.BLUE, 
                        f"Original training time ({today_training_time.strftime('%H:%M:%S')} UTC) has passed, "
                        f"will try at {new_training_time.strftime('%H:%M:%S')} UTC")
                    await asyncio.sleep(random_wait_seconds)
                else:
                    # 计算到随机训练时间的等待时间
                    wait_seconds = (today_training_time - current_utc).total_seconds()
                    self.print_message(username, proxy, Fore.BLUE, 
                        f"Waiting for training time: {today_training_time.strftime('%H:%M:%S')} UTC")
                    await asyncio.sleep(wait_seconds)
                
                # 检查积分余额
                self.print_message(username, proxy, Fore.BLUE, "Checking Points Balance...")
                earning = await self.user_earning(token, username, proxy)
                if earning == "TOKEN_EXPIRED":
                    self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Pausing Account")
                    self.save_paused_account(account_data)
                    return
                
                if earning:
                    total_points = earning['total_total']
                    
                    self.print_message(username, proxy, Fore.WHITE,
                        f"Current Points Balance: {total_points} PTS"
                    )
                    
                    if total_points < 2500:
                        self.print_message(username, proxy, Fore.YELLOW, 
                            f"Points Balance ({total_points}) is less than 2500, skipping training today")
                    else:
                        # 执行训练
                        self.print_message(username, proxy, Fore.BLUE, "Starting Training...")
                        train = await self.complete_training(token, username, proxy)
                        if train == "TOKEN_EXPIRED":
                            self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Pausing Account")
                            self.save_paused_account(account_data)
                            return
                        
                        if train:
                            if train.get("code") == 200 and train.get("success") is True:
                                data = train.get("data", {})
                                burned_points = data.get('burned_points', 0)
                                soul = data.get('soul', 0)
                                blindbox = data.get('blindbox', 0)
                                self.print_message(username, proxy, Fore.GREEN,
                                    "Training Completed "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} Burned {burned_points} PTS {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{soul} Soul PTS{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{blindbox} Blindbox{Style.RESET_ALL}"
                                )
                                # 记录训练完成
                                self.save_training_record(account_data)
                                # 训练成功后等待到下一个UTC 0:00
                                wait_seconds = (next_utc - current_utc).total_seconds()
                                self.print_message(username, proxy, Fore.BLUE, 
                                    f"Training completed successfully, waiting for next day")
                                await asyncio.sleep(wait_seconds)
                                continue
                            elif train.get("msg") == "Training already completed":
                                self.print_message(username, proxy, Fore.YELLOW, "Training Already Completed Today")
                                # 记录训练完成
                                self.save_training_record(account_data)
                                # 训练已完成时等待到下一个UTC 0:00
                                wait_seconds = (next_utc - current_utc).total_seconds()
                                self.print_message(username, proxy, Fore.BLUE, 
                                    f"Waiting for next day's training")
                                await asyncio.sleep(wait_seconds)
                                continue
                            else:
                                # 处理其他API响应错误
                                error_msg = train.get('msg', 'Unknown error')
                                self.print_message(username, proxy, Fore.RED, f"Training API Error: {error_msg}")
                                # 生成新的随机训练时间（从当前时间到UTC 24:00）
                                remaining_seconds = (next_utc - current_utc).total_seconds()
                                new_wait_seconds = random.randint(0, int(remaining_seconds))
                                new_training_time = current_utc + timedelta(seconds=new_wait_seconds)
                                self.print_message(username, proxy, Fore.BLUE, 
                                    f"Training failed, will retry at {new_training_time.strftime('%H:%M:%S')} UTC")
                                await asyncio.sleep(new_wait_seconds)
                                continue
                        else:
                            # 如果没有响应，生成新的随机训练时间
                            remaining_seconds = (next_utc - current_utc).total_seconds()
                            new_wait_seconds = random.randint(0, int(remaining_seconds))
                            new_training_time = current_utc + timedelta(seconds=new_wait_seconds)
                            self.print_message(username, proxy, Fore.YELLOW, 
                                f"No response from training API, will retry at {new_training_time.strftime('%H:%M:%S')} UTC")
                            await asyncio.sleep(new_wait_seconds)
                            continue

            except Exception as e:
                # 处理未预期的异常（如网络错误、连接超时等）
                logging.error("Complete Training Failed", extra={"account": username, "proxy": proxy if proxy else "No Proxy", "message": str(e)})
                self.print_message(username, proxy, Fore.RED, f"Unexpected Error: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                # 发生错误时也生成新的随机训练时间
                remaining_seconds = (next_utc - current_utc).total_seconds()
                new_wait_seconds = random.randint(0, int(remaining_seconds))
                new_training_time = current_utc + timedelta(seconds=new_wait_seconds)
                self.print_message(username, proxy, Fore.BLUE, 
                    f"Error occurred, will retry at {new_training_time.strftime('%H:%M:%S')} UTC")
                await asyncio.sleep(new_wait_seconds)

    async def test_training(self, token: str, username: str, proxy=None):
        """测试训练功能的方法"""
        self.print_message(username, proxy, Fore.BLUE, "Starting Training Test...")
        
        # 1. 首先检查积分余额
        self.print_message(username, proxy, Fore.BLUE, "Checking Points Balance...")
        earning = await self.user_earning(token, username, proxy)
        if earning == "TOKEN_EXPIRED":
            self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Test Failed")
            return False
        
        if earning:
            total_points = earning['total_total']
            self.print_message(username, proxy, Fore.WHITE,
                f"Current Points Balance: {total_points} PTS"
            )
            
            if total_points < 2500:
                self.print_message(username, proxy, Fore.YELLOW, 
                    f"Points Balance ({total_points}) is less than 2500, cannot test training")
                return False
        
        # 2. 检查 Soul 余额
        self.print_message(username, proxy, Fore.BLUE, "Checking Soul Balance...")
        soul_balance = await self.get_soul_balance(token, username, proxy)
        if soul_balance == "TOKEN_EXPIRED":
            self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Test Failed")
            return False
            
        if soul_balance:
            self.print_message(username, proxy, Fore.WHITE,
                f"Current Soul Balance: {soul_balance.get('data', {}).get('soul', 0)} PTS"
            )
        
        # 3. 执行训练
        self.print_message(username, proxy, Fore.BLUE, "Testing Training...")
        train = await self.complete_training(token, username, proxy)
        if train == "TOKEN_EXPIRED":
            self.print_message(username, proxy, Fore.RED, "Token Expired (401) - Test Failed")
            return False
        
        if train:
            if train.get("code") == 200 and train.get("success") is True:
                data = train.get("data", {})
                burned_points = data.get('burned_points', 0)
                soul = data.get('soul', 0)
                blindbox = data.get('blindbox', 0)
                self.print_message(username, proxy, Fore.GREEN,
                    "Training Test Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Burned {burned_points} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{soul} Soul PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{blindbox} Blindbox{Style.RESET_ALL}"
                )
                return True
            elif train.get("code") == 400:
                self.print_message(username, proxy, Fore.YELLOW, "Training Already Completed - Test Skipped")
                return True
            else:
                error_msg = train.get('msg', 'Unknown error')
                self.print_message(username, proxy, Fore.RED, f"Training Test Failed: {error_msg}")
                return False
        else:
            self.print_message(username, proxy, Fore.RED, "Training Test Failed: No Response")
            return False

    async def test_account(self, account: dict, use_proxy: bool):
        """测试单个账户的所有功能"""
        browser_id = account.get('Browser_ID')
        token = account.get('Token')
        proxy = self.check_proxy_schemes(account.get('Proxy')) if use_proxy else None
        username = account.get('Name')
        user_id = account.get('UID')
        
        if not (token and browser_id and username and user_id):
            self.log(f"{Fore.RED}Missing required fields (Token, Browser_ID, Name, or UID) for account {username or 'unknown'}{Style.RESET_ALL}")
            return

        self.print_message(username, proxy, Fore.BLUE, "Starting Account Test...")
        
        # 测试训练功能
        training_result = await self.test_training(token, username, proxy)
        
        if training_result:
            self.print_message(username, proxy, Fore.GREEN, "Account Test Completed Successfully")
        else:
            self.print_message(username, proxy, Fore.RED, "Account Test Failed")

    async def process_accounts(self, account: dict, use_proxy: bool):
        browser_id = account.get('Browser_ID')
        token = account.get('Token')
        proxy = self.check_proxy_schemes(account.get('Proxy')) if use_proxy else None
        username = account.get('Name')
        user_id = account.get('UID')
        
        if not (token and browser_id and username and user_id):
            self.log(f"{Fore.RED}Missing required fields (Token, Browser_ID, Name, or UID) for account {username or 'unknown'}{Style.RESET_ALL}")
            return

        # Add random initial delay (0-100 seconds)
        initial_delay = random.uniform(0, 100)
        self.log(f"{Fore.YELLOW}Initial delay for {username}: {self.format_seconds(initial_delay)}{Style.RESET_ALL}")
        await asyncio.sleep(initial_delay)

        try:
            tasks = []
            tasks.append(self.process_user_earning(token, username, account, proxy))
            tasks.append(self.process_send_ping(token, browser_id, username, user_id, account, proxy, ping_type="extension"))
            # 添加训练任务
            if account.get('trained', False):  # 如果账户启用了训练
                tasks.append(self.process_complete_training(token, username, account, proxy))
            # 添加每日奖励任务
            tasks.append(self.process_daily_reward(token, username, account, proxy))
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error("Process Account Failed", extra={"account": username, "proxy": proxy if proxy else "No Proxy", "message": str(e)})
            self.log(f"{Fore.RED}Error processing account {username}: {e}{Style.RESET_ALL}")

    async def main(self):
        try:
            self.load_accounts()
            if not self.accounts:
                self.log(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice, trained = self.print_question()
            use_proxy = use_proxy_choice == 1

            # 更新账户的训练状态
            for account in self.accounts:
                account['trained'] = trained

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.accounts)}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.YELLOW + Style.BRIGHT}Paused Accounts: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.paused_accounts)}{Style.RESET_ALL}"
            )

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            # 询问是否要运行测试
            while True:
                try:
                    test_mode = input("Run in test mode? (y/n) -> ").strip().lower()
                    if test_mode in ["y", "n"]:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter 'y' for test mode or 'n' for normal mode.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Please enter 'y' or 'n'.{Style.RESET_ALL}")

            if test_mode == "y":
                # 测试模式：只测试第一个账户
                if self.accounts:
                    await self.test_account(self.accounts[0], use_proxy)
            else:
                # 正常模式：运行所有账户
                tasks = []
                for account in self.accounts:
                    tasks.append(self.process_accounts(account, use_proxy))
                await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = AiGaea()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] AI Gaea - BOT{Style.RESET_ALL}                                       "                              
        )