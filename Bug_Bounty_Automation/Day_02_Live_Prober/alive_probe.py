import requests
import concurrent.futures
import sys
import urllib3
import time

# Disable insecure HTTPS warnings for clean terminal output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_banner():
    print("""
    ==================================================
      THE PULSE CHECKER - Multi-Threaded Live Host Prober
    ==================================================
    """)

def check_alive(subdomain):
    subdomain = subdomain.strip()
    if not subdomain:
        return None

    # We test HTTPS first, if it fails, we test HTTP
    protocols = ["https://", "http://"]
    
    for proto in protocols:
        url = f"{proto}{subdomain}"
        try:
            # We use a short timeout. If a server takes more than 3 seconds, it's too slow for automation.
            response = requests.get(url, timeout=3, verify=False, allow_redirects=False)
            
            # If we get ANY status code, the server is ALIVE!
            status = response.status_code
            
            # Format the output with colors/tags based on status
            if status == 200:
                return f"[+] [200 OK]      {url}"
            elif status in [301, 302, 307]:
                return f"[~] [{status} Redirect] {url} -> {response.headers.get('Location', '')}"
            elif status in [401, 403]:
                return f"[!] [{status} Denied]   {url} (Juicy! Might contain admin panels)"
            else:
                return f"[*] [{status} Found]    {url}"
                
        except requests.exceptions.RequestException:
            continue # Try the next protocol or fail silently

    return None # Dead host

def probe_list(filename, threads=50):
    print_banner()
    
    try:
        with open(filename, 'r') as f:
            subdomains = f.readlines()
    except FileNotFoundError:
        print(f"[-] Bhai, file '{filename}' nahi mili. Sahi path daalo!")
        return

    print(f"[*] Loaded {len(subdomains)} subdomains from {filename}.")
    print(f"[*] Igniting {threads} parallel threads. Launching probes...\n")
    print("-" * 60)
    
    start_time = time.time()
    alive_count = 0
    alive_hosts = []

    # The Hacker's Multi-Threading Engine
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        # Map the check_alive function to our list of subdomains
        results = executor.map(check_alive, subdomains)
        
        for result in results:
            if result:
                print(result)
                alive_hosts.append(result)
                alive_count += 1

    end_time = time.time()
    
    print("-" * 60)
    print(f"[+] Probing Complete in {round(end_time - start_time, 2)} seconds!")
    print(f"[+] Found {alive_count} ALIVE hosts out of {len(subdomains)}.")
    
    # Save the alive hosts to a new file for the next stage of our pipeline
    output_file = f"alive_{filename.split('/')[-1]}"
    with open(output_file, 'w') as f:
        for host in alive_hosts:
            # We just save the URL part for future tools
            clean_url = host.split()[-1] if "Redirect" not in host else host.split()[-3]
            f.write(clean_url + "\n")
            
    print(f"[+] Saved live targets to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 alive_probe.py <subdomains_file.txt>")
        print("Example: python3 alive_probe.py ../Day_01_Recon_Monitor/tesla.com_history.txt")
        sys.exit(1)
        
    target_file = sys.argv[1]
    probe_list(target_file)
