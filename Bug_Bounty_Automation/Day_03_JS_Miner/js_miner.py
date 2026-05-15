import requests
import re
import sys
import urllib3
from urllib.parse import urljoin

# Clean terminal output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_banner():
    print("""
    ==================================================
        THE JS MINER - Secret Endpoint Extractor
    ==================================================
    """)

def mine_endpoints(url):
    print(f"[*] Target locked: {url}")
    print("[*] Fetching HTML and searching for JavaScript files...")
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        html_content = response.text
    except Exception as e:
        print(f"[-] Failed to connect to {url}\n")
        return

    # Regex 1: Find all .js files in the HTML
    # Looks for src="something.js" or src='something.js'
    js_files = set(re.findall(r'src=["\'](.*?\.js)["\']', html_content))
    
    if not js_files:
        print("[-] No JavaScript files found on the main page.\n")
        return

    print(f"[+] Found {len(js_files)} JS files. Digging for hidden endpoints...\n")
    print("-" * 60)

    # Regex 2: Find hidden API endpoints inside the JS files
    # Looks for strings like "/api/v1/user" or "/dashboard"
    endpoint_regex = re.compile(r'["\'](/[a-zA-Z0-9_/?&=-]+)["\']')

    found_endpoints = set()

    for js_path in js_files:
        # Convert relative JS paths (like /js/app.js) to absolute URLs
        full_js_url = urljoin(url, js_path)
        
        try:
            js_response = requests.get(full_js_url, headers=headers, timeout=5, verify=False)
            js_content = js_response.text
            
            # Extract endpoints using our Regex
            endpoints = endpoint_regex.findall(js_content)
            for ep in endpoints:
                # Filter out garbage (too short, or generic CSS/PNG paths)
                if len(ep) > 3 and not ep.endswith(('.png', '.svg', '.css', '.jpg')):
                    found_endpoints.add(ep)
                    
        except Exception:
            pass # Skip this JS file if it fails

    # Print the Loot!
    if found_endpoints:
        print(f"[!!!] JACKPOT 🎯 Found {len(found_endpoints)} Hidden Endpoints!")
        for ep in sorted(found_endpoints):
            print(f"   --> {ep}")
    else:
        print("[-] Mined the JS files but found no juicy endpoints.")
        
    print("=" * 60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage (Single): python3 js_miner.py <url>")
        print("Usage (List):   python3 js_miner.py <alive_hosts.txt>")
        sys.exit(1)
        
    target = sys.argv[1]
    print_banner()
    
    # Check if the user provided a file or a single URL
    if target.endswith('.txt'):
        try:
            with open(target, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            print(f"[*] Loaded {len(urls)} URLs from list. Starting mass mining...\n")
            for u in urls:
                mine_endpoints(u)
        except FileNotFoundError:
            print(f"[-] File {target} not found.")
    else:
        mine_endpoints(target)
