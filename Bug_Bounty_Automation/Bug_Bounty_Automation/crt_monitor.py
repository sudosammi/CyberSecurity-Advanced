import requests
import sys
import os

def print_banner():
    print("""
    ==================================================
      THE SLEEPY HUNTER - Automated Subdomain Monitor
    ==================================================
    """)

def fetch_subdomains(domain):
    print(f"[*] Fetching SSL Certificate logs for: {domain}...")
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print("[-] Error connecting to crt.sh API.")
            return set()
            
        data = response.json()
        subdomains = set()
        
        for item in data:
            name = item['name_value'].lower()
            # Certificate logs sometimes contain wildcards like *.target.com
            if '*' not in name:
                # Some entries have multiple domains separated by newline
                for sub in name.split('\n'):
                    subdomains.add(sub.strip())
                    
        return subdomains
        
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return set()

def monitor_domain(domain):
    print_banner()
    
    # Define where we store our history
    history_file = f"{domain}_history.txt"
    
    # Read old subdomains if the file exists
    old_subdomains = set()
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            for line in f:
                old_subdomains.add(line.strip())
        print(f"[*] Loaded {len(old_subdomains)} previously known subdomains from memory.")
    else:
        print(f"[*] No previous history found for {domain}. This is the first run!")

    # Fetch fresh subdomains from the internet
    current_subdomains = fetch_subdomains(domain)
    
    if not current_subdomains:
        print("[-] No subdomains found or API blocked us. Try again later.")
        return

    print(f"[*] Found {len(current_subdomains)} total subdomains live on crt.sh.")

    # The Magic Diffing (Find what's new!)
    new_subdomains = current_subdomains - old_subdomains

    if new_subdomains:
        print("\n[!!!] JACKPOT 🎯 NEW SUBDOMAINS DETECTED!")
        print("[!!!] These domains were not here last time. Hack them before anyone else does:\n")
        
        for sub in new_subdomains:
            print(f"   -> {sub}")
            
        # Update our history file with the new complete list
        with open(history_file, 'w') as f:
            for sub in sorted(current_subdomains):
                f.write(sub + "\n")
                
        print(f"\n[+] Updated {history_file} with new data.")
        print("[+] Next Step: Send these to your port scanner or vulnerability fuzzer!")
    else:
        print("\n[-] Zzz... No new subdomains found. The target hasn't deployed anything new.")
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 crt_monitor.py <target_domain>")
        print("Example: python3 crt_monitor.py uber.com")
        sys.exit(1)
        
    target = sys.argv[1].lower()
    monitor_domain(target)
