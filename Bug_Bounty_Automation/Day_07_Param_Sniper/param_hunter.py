import requests
import concurrent.futures
import sys
import urllib3

# Clean terminal output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_banner():
    print("""
    ==================================================
       THE PARAMETER SNIPER - Hidden Param Fuzzer
    ==================================================
    """)

# Global session for speed
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ParamHunter/1.0"})

def get_baseline(url):
    print(f"[*] Fetching baseline for: {url}")
    try:
        res = session.get(url, timeout=5, verify=False)
        return len(res.text), res.status_code
    except Exception as e:
        print(f"[-] Failed to fetch baseline: {e}")
        sys.exit(1)

def test_param(url, param, baseline_length, baseline_status):
    param = param.strip()
    if not param:
        return None
        
    # Appending the parameter to the URL with a dummy value
    # Check if URL already has parameters (?) to use '&' instead
    separator = "&" if "?" in url else "?"
    target_url = f"{url}{separator}{param}=bugbountytest"
    
    try:
        res = session.get(target_url, timeout=3, verify=False)
        current_length = len(res.text)
        current_status = res.status_code
        
        # The Hacker's Logic: Anomaly Detection
        # If status code changes OR the page length changes by more than 50 bytes (to ignore dynamic time/ads)
        if current_status != baseline_status or abs(current_length - baseline_length) > 50:
            return f"[!!!] JACKPOT 🎯 Hidden Parameter Found: {param} | Status: {current_status} | Length Diff: {abs(current_length - baseline_length)}"
            
    except requests.exceptions.RequestException:
        pass
        
    return None

def start_sniping(url, wordlist_file, threads=30):
    print_banner()
    
    baseline_length, baseline_status = get_baseline(url)
    print(f"[*] Baseline Status: HTTP {baseline_status}")
    print(f"[*] Baseline Length: {baseline_length} bytes\n")
    
    try:
        with open(wordlist_file, 'r') as f:
            params = f.readlines()
        print(f"[*] Loaded {len(params)} parameters to test.")
    except FileNotFoundError:
        print(f"[-] ERROR: Wordlist '{wordlist_file}' not found!")
        return

    print(f"[*] Igniting {threads} parallel threads. Sniping started...\n")
    print("-" * 60)

    found_params = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_param = {executor.submit(test_param, url, p, baseline_length, baseline_status): p for p in params}
        
        for future in concurrent.futures.as_completed(future_to_param):
            result = future.result()
            if result:
                print(result)
                found_params.append(result)

    print("-" * 60)
    if found_params:
        print(f"[+] Hunt Complete! Found {len(found_params)} potential hidden parameters.")
        print("[+] Next Step: Test these parameters for XSS, SSRF, or LFI!")
    else:
        print("[-] Scan complete. No hidden parameters detected that alter the page.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 param_hunter.py <Target_URL> <Param_Wordlist.txt>")
        print("Example: python3 param_hunter.py https://example.com/api/users params.txt")
        sys.exit(1)
        
    target_url = sys.argv[1]
    wordlist = sys.argv[2]
    
    start_sniping(target_url, wordlist)
