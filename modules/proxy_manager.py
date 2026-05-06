# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #



import os
import random

class ProxyManager:
    def __init__(self, proxy_file="live_proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies = []
        self.load_proxies()

    def load_proxies(self):
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, "r") as f:
                 self.proxies = [line.strip() for line in f if line.strip()]
            print(f"[+] Loaded {len(self.proxies)} proxies from {self.proxy_file}")
        else:
            print(f"[!] {self.proxy_file} not found. Please scrape proxies first.")
            self.proxies = []
            
    def get_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)
