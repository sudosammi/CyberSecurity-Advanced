#!/bin/bash

# ==================================================
# THE MASTER HUNTER - Bug Bounty Orchestration
# ==================================================

# Check if target is provided
if [ -z "$1" ]; then
    echo -e "[-] Usage: ./master_hunter.sh <target.com>"
    exit 1
fi

TARGET=$1
WEBHOOK="https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE" # Optional: Replace with yours

echo -e "\n[🚀] INITIATING MASTER HUNT FOR: $TARGET"
echo -e "==================================================\n"

# Step 1: Subdomain Recon (Day 1)
echo -e "[1/6] Running Sleepy Hunter (Subdomains)..."
python3 ../Day_01_Recon_Monitor/crt_monitor.py $TARGET

# Step 2: Live Host Probing (Day 2)
# File expected from Day 1: ${TARGET}_history.txt
echo -e "\n[2/6] Running Pulse Checker (Live Hosts)..."
if [ -f "../Day_01_Recon_Monitor/${TARGET}_history.txt" ]; then
    python3 ../Day_02_Live_Prober/alive_probe.py ../Day_01_Recon_Monitor/${TARGET}_history.txt
else
    echo -e "[-] No subdomains found to probe."
fi

# Step 3: JS Endpoint Extraction (Day 3)
# File expected from Day 2: alive_${TARGET}_history.txt
echo -e "\n[3/6] Running JS Miner..."
if [ -f "alive_${TARGET}_history.txt" ]; then
    python3 ../Day_03_JS_Miner/js_miner.py alive_${TARGET}_history.txt > js_loot_${TARGET}.txt
    echo -e "[+] JS Mining complete."
fi

# Step 4: Historical URLs (Day 4)
echo -e "\n[4/6] Running The Time Machine (Wayback)..."
python3 ../Day_04_Time_Machine/wayback_miner.py $TARGET

# Step 5: Report Generation (Day 9)
echo -e "\n[5/6] Generating Executive Report..."
python3 ../Day_09_Auto_Reporter/auto_reporter.py $TARGET
mv Final_Report_${TARGET}.md ../Day_09_Auto_Reporter/ 2>/dev/null

# Step 6: Discord Alert (Day 5)
echo -e "\n[6/6] Sending Discord Alert..."
python3 ../Day_05_Alert_Sniper/discord_sniper.py "$WEBHOOK" "Master Hunt Complete for $TARGET! Check the Markdown report for bounties! 💸"

echo -e "\n=================================================="
echo -e "[🎉] MISSION ACCOMPLISHED! ALL SYSTEMS RESTING."
echo -e "=================================================="
