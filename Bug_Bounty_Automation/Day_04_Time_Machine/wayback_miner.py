import requests
import sys
import urllib.parse

def print_banner():
    print("""
    ==================================================
        THE TIME MACHINE - Wayback URL Extractor
    ==================================================
    """)

def mine_wayback(domain):
    print_banner()
    print(f"[*] Firing up the Time Machine for: {domain}")
    print("[*] Fetching 10 years of historical URLs from the Internet Archive...")
    
    # The CDX API Endpoint for Wayback Machine
    url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey"
    
    try:
        # Taking a longer timeout because the archive database is HUGE
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            print("[-] API refused the connection. Try again later.")
            return

        # Response is a list of lists: [["original"], ["http://url1.com"], ["http://url2.com"]]
        data = response.json()
        
        if len(data) <= 1:
            print("[-] No historical data found for this domain.")
            return
            
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return

    print(f"[+] Downloaded {len(data) - 1} raw historical URLs.")
    print("[*] Filtering out garbage (Images, CSS, Fonts) to find juicy endpoints...\n")
    print("-" * 60)

    # Hacker's Filter: We don't care about these extensions
    garbage_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', 
        '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.mp3', '.ico'
    )
    
    juicy_urls = set()

    # Skip the first item because it's just the header ["original"]
    for item in data[1:]:
        url_string = item[0]
        
        # Parse the URL to check its path and extension
        parsed = urllib.parse.urlparse(url_string)
        path = parsed.path.lower()
        
        # If it doesn't end with garbage, we keep it!
        if not path.endswith(garbage_extensions):
            juicy_urls.add(url_string)

    # Print a sample of the Loot
    print(f"[!!!] JACKPOT 🎯 Filtered down to {len(juicy_urls)} High-Value Endpoints!")
    
    # Save the loot to a file
    output_file = f"archive_{domain}.txt"
    with open(output_file, 'w') as f:
        for u in sorted(juicy_urls):
            f.write(u + "\n")
            
    # Show a few lines as a teaser
    teaser = list(juicy_urls)[:10]
    for t in teaser:
        print(f"   --> {t}")
        
    if len(juicy_urls) > 10:
        print(f"   --> ... and {len(juicy_urls) - 10} more.")
        
    print("-" * 60)
    print(f"[+] All historical URLs saved to: {output_file}")
    print("[+] Next Step: Pass these URLs to your vulnerability scanner (like SSRF Hunter)!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 wayback_miner.py <target_domain>")
        print("Example: python3 wayback_miner.py uber.com")
        sys.exit(1)
        
    target = sys.argv[1].lower()
    mine_wayback(target)
