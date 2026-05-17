import requests
import sys
import json

def print_banner():
    print("""
    ==================================================
        THE ALERT SNIPER - Discord Webhook Notifier
    ==================================================
    """)

def send_alert(webhook_url, message):
    # The JSON payload that Discord expects
    data = {
        "content": f"🚨 **BUG BOUNTY ALERT** 🚨\n```yaml\n{message}\n
```",
        "username": "Fedora Sniper Bot",
        "avatar_url": "https://i.imgur.com/4M34hiw.png" # Cool hacker avatar
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers, timeout=5)
        
        if response.status_code == 204:
            print("[+] JACKPOT 🎯 Alert successfully sniped to your Discord!")
        else:
            print(f"[-] Failed to send alert. Discord returned status code: {response.status_code}")
            print(f"[-] Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[-] Network error while hitting the webhook: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_banner()
        print("Usage: python3 discord_sniper.py <WEBHOOK_URL> \"<YOUR_MESSAGE>\"")
        print("Example: python3 discord_sniper.py https://discord.com/api/webhooks/... \"Found new subdomain: api-dev.tesla.com\"")
        sys.exit(1)
        
    webhook = sys.argv[1]
    # Join all arguments after the webhook as the message (in case quotes were forgotten)
    msg = " ".join(sys.argv[2:])
    
    send_alert(webhook, msg)
