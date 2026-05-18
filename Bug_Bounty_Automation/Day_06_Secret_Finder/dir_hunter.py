import requests
import concurrent.futures
import sys
import urllib3

# Server ko tang na karne ke liye SSL warnings off kar dete hain
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_banner():
    print("""
    ==================================================
        THE SECRET FINDER - Fast Directory Fuzzer
    ==================================================
    """)

# Deep Dive: Hum ek global Session object bana rahe hain speed badhane ke liye
session = requests.Session()
# Headers set kar rahe hain taaki server hume block na kare (fake identity)
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BugHunter/1.0"})

def test_directory(base_url, word):
    # Word ke aage-peeche ke spaces hata do
    word = word.strip()
    if not word:
        return None
        
    # URL aur word ko jod kar full path banao (e.g., https://target.com/admin)
    target_url = f"{base_url}/{word}"
    
    try:
        # Deep Dive: session.get() use kar rahe hain for connection pooling
        # timeout=3 isliye taaki agar server atak jaye toh script na atke
        response = session.get(target_url, timeout=3, verify=False, allow_redirects=False)
        
        # Agar 200 (OK), 403 (Forbidden - hidden file), ya 301/302 (Redirect) aaye toh jackpot!
        if response.status_code in [200, 403, 301, 302]:
            return f"[+] [HTTP {response.status_code}] Found: {target_url}"
            
    except requests.exceptions.RequestException:
        # Agar connection error aaye toh silently pass kar do (terminal saaf rakhne ke liye)
        pass
        
    return None

def start_hunting(url, wordlist_file, threads=30):
    print_banner()
    print(f"[*] Target Locked: {url}")
    
    # 1. Wordlist file ko open karke read karte hain
    try:
        with open(wordlist_file, 'r') as f:
            words = f.readlines()
        print(f"[*] Loaded {len(words)} words from dictionary.")
    except FileNotFoundError:
        print(f"[-] ERROR: Wordlist file '{wordlist_file}' nahi mili!")
        sys.exit(1)

    print(f"[*] Igniting {threads} parallel threads. Fuzzing started...\n")
    print("-" * 60)

    found_secrets = []

    # Deep Dive: Multi-threading ka Engine start kar rahe hain
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        # executor.submit humare function ko alag alag threads mein bhejta hai
        # Dictionary comprehension use kar rahe hain taaki results track kar sakein
        future_to_url = {executor.submit(test_directory, url, word): word for word in words}
        
        # Jaise jaise threads apna kaam khatam karte hain, hum result print karte hain
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            if result:
                print(result)
                found_secrets.append(result)

    print("-" * 60)
    print(f"[+] Hunt Complete! Found {len(found_secrets)} hidden paths.")
    
    # Agar kuch mila, toh use file mein save kar lo
    if found_secrets:
        with open("loot_directories.txt", "w") as f:
            for secret in found_secrets:
                f.write(secret + "\n")
        print("[+] Loot saved to 'loot_directories.txt'")

# Deep Dive: Main execution block
if __name__ == "__main__":
    # Sys.argv command line arguments ko handle karta hai
    if len(sys.argv) != 3:
        print("Usage: python3 dir_hunter.py <Target_URL> <Wordlist.txt>")
        print("Example: python3 dir_hunter.py https://example.com common.txt")
        sys.exit(1)
        
    target_url = sys.argv[1].rstrip('/') # End mein se extra '/' hata do agar user ne lagaya hai
    wordlist = sys.argv[2]
    
    start_hunting(target_url, wordlist)
