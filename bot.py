from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, uuid, time, json, os, pytz, csv, random

wib = pytz.timezone('Asia/Jakarta')

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
                if reader.fieldnames != ['Name', 'Browser_ID', 'Token', 'Proxy']:
                    self.log(f"{Fore.RED}Invalid CSV format. Required fields: Name,Browser_ID,Token,Proxy{Style.RESET_ALL}")
                    return
                self.accounts = list(reader)
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
        
    def generate_random_browser_id(self, browser_id: str):
        random_browser_id = str(uuid.uuid4())[8:]
        if len(browser_id) == 32:
            return browser_id
        return browser_id[:8] + random_browser_id

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

    async def user_data(self, token: str, proxy=None):
        url = "https://api.aigaea.net/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "0",
            "Content-Type": "application/json"
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return self.print_message(self.mask_account(token), proxy, Fore.RED, f"GET User ID Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def user_ip(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/network/ip"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET IP Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def user_earning(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def mission_lists(self, token: str, username: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/mission/list"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"GET Available Mission Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def complete_mission(self, token: str, username: str, mission_id: int, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/mission/complete-mission"
        data = json.dumps({"mission_id":mission_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                    continue
                return self.print_message(username, proxy, Fore.RED, f"Complete Available Mission Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def send_ping(self, token: str, random_browser_id: str, username: str, user_id: str, proxy=None, retries=5):
        url = "https://api.aigaea.net/api/network/ping"
        data = json.dumps({"browser_id":random_browser_id, "timestamp":int(time.time()), "uid":user_id, "version":"2.0.2"})
        headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://cpjicfogbgognnifjgmenmaldnmeeeib",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": FakeUserAgent().random
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(username, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            
    async def process_user_earning(self, token: str, username: str, proxy=None):
        while True:
            earning = await self.user_earning(token, username, proxy)
            if earning:
                today = earning['today_total']
                total = earning['total_total']
                uptime = earning['today_uptime']

                self.print_message(username, proxy, Fore.WHITE,
                    f"Earning Today {today} PTS "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Earning Total {total} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Uptime: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Today {uptime} Minutes{Style.RESET_ALL}"
                )

            await asyncio.sleep(15 * 60)

    async def process_user_missions(self, token: str, username: str, proxy=None):
        while True:
            missions = await self.mission_lists(token, username, proxy)
            if missions:
                completed = False
                for mission in missions:
                    mission_id = str(mission['id'])
                    title = mission['title']
                    reward = mission['points']
                    status = mission['status']

                    if mission and status == "AVAILABLE":
                        complete = await self.complete_mission(token, username, mission_id, proxy)
                        if complete:
                            self.print_message(username, proxy, Fore.WHITE,
                                f"Mission {title}"
                                f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                            )
                        else:
                            self.print_message(username, proxy, Fore.WHITE,
                                f"Mission {title} "
                                f"{Fore.RED + Style.BRIGHT}Isn't Completed{Style.RESET_ALL}"
                            )
                    else:
                        completed = True

                if completed:
                    self.print_message(username, proxy, Fore.GREEN,
                        "All Available Mission Is Completed"
                    )
                
            await asyncio.sleep(12 * 60 * 60)

    async def process_send_ping(self, token: str, browser_id: str, username: str, user_id: str, server_host: str, proxy=None):
        random_browser_id = self.generate_random_browser_id(browser_id)
        while True:
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            ping = await self.send_ping(token, random_browser_id, username, user_id, proxy)
            if ping:
                score = ping['score']

                self.print_message(username, proxy, Fore.GREEN,
                    "PING Success"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Network Score:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {score} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Server Host: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{server_host}{Style.RESET_ALL}"
                )

            wait_time = random.uniform(6 * 60, 12 * 60)  # Random wait between 12-18 minutes
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For {self.format_seconds(wait_time)} For Next Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(wait_time)

    async def get_user_data(self, token: str, proxy=None):
        user = None
        while user is None:
            user = await self.user_data(token, proxy)
            if not user:
                continue

            self.print_message(self.mask_account(token), proxy, Fore.GREEN, "GET User ID Success")

            server_host = "Unknown"
            ip_data = await self.user_ip(token, user['name'], proxy)
            if ip_data:
                server_host = ip_data['host']

            return user, server_host
        
    async def process_accounts(self, account: dict, use_proxy: bool):
        browser_id = account.get('Browser_ID')
        token = account.get('Token')
        proxy = self.check_proxy_schemes(account.get('Proxy')) if use_proxy else None
        
        if not (token and browser_id):
            self.log(f"{Fore.RED}Missing Token or Browser_ID for account {account.get('Name')}{Style.RESET_ALL}")
            return

        # Add random initial delay (0-200 seconds)
        initial_delay = random.uniform(0, 200)
        self.log(f"{Fore.YELLOW}Initial delay for {account.get('Name')}: {self.format_seconds(initial_delay)}{Style.RESET_ALL}")
        await asyncio.sleep(initial_delay)

        user, server_host = await self.get_user_data(token, proxy)
        if user and server_host:
            username = user['name']
            user_id = user['uid']

            tasks = []
            tasks.append(self.process_user_earning(token, username, proxy))
            tasks.append(self.process_user_missions(token, username, proxy))
            tasks.append(self.process_send_ping(token, browser_id, username, user_id, server_host, proxy))
            await asyncio.gather(*tasks)

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