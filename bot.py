from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, os, pytz, csv, random, json, logging

wib = pytz.timezone('Asia/Jakarta')

# 配置日志记录
logging.basicConfig(
    filename='account_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - Account: %(account)s - Proxy: %(proxy)s - Error: %(message)s'
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
        self.paused_accounts = self.load_paused_accounts()

    def load_paused_accounts(self):
        try:
            if os.path.exists(self.paused_accounts_file):
                with open(self.paused_accounts_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading paused accounts: {e}")
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
        self.log(
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
                    return choose
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
        version = "3.0.1" if ping_type == "extension" else "1.0.1"
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
                        return result['data']
            except ClientResponseError as e:
                if e.status == 401:
                    return "TOKEN_EXPIRED"
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
            # tasks.append(self.process_send_ping(token, browser_id, username, user_id, account, proxy, ping_type="webpage"))
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
            
            use_proxy_choice = self.print_question()
            use_proxy = use_proxy_choice == 1

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