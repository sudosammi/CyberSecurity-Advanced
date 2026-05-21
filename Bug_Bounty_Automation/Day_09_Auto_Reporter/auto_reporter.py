import os
import datetime
import sys

def print_banner():
    print("""
    ==================================================
      THE BOUNTY CLAIMER - Auto-Report Generator
    ==================================================
    """)

def read_loot_file(filepath):
    """Safely reads a file and returns its lines as a list."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"[-] Error reading {filepath}: {e}")
        return []

def generate_report(target_name):
    print_banner()
    print(f"[*] Compiling all loot files for target: {target_name}...")
    
    # Define expected files from our previous pipeline tools
    files_to_check = {
        "Subdomains": f"../Day_01_Recon_Monitor/{target_name}_history.txt",
        "Live Hosts": f"../Day_02_Live_Prober/alive_{target_name}_history.txt",
        "Historical URLs": f"../Day_04_Time_Machine/archive_{target_name}.txt",
        "Hidden Directories": "../Day_06_Secret_Finder/loot_directories.txt"
    }

    report_content = f"# 🚀 Automated Bug Bounty Recon Report\n"
    report_content += f"**Target:** `{target_name}`\n"
    report_content += f"**Generated On:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
    report_content += "---\n\n"

    total_findings = 0

    # Aggregate data from all tools
    for section, filepath in files_to_check.items():
        data = read_loot_file(filepath)
        report_content += f"## 📂 {section} (Total: {len(data)})\n"
        
        if data:
            report_content += "```text\n"
            # Limit to top 50 lines per section to avoid massive reports
            for item in data[:50]:
                report_content += f"{item}\n"
            if len(data) > 50:
                report_content += f"... and {len(data) - 50} more items.\n"
            report_content += "```\n\n"
            total_findings += len(data)
        else:
            report_content += "*No data found or scan not run yet.*\n\n"

    # Save the Markdown Report
    report_filename = f"Final_Report_{target_name}.md"
    
    try:
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print("-" * 60)
        print(f"[+] JACKPOT 🎯 Report Successfully Generated!")
        print(f"[+] Compiled {total_findings} data points into a clean Markdown document.")
        print(f"[+] Report saved to: {report_filename}")
        print("[+] Next Step: Open the .md file, review the findings, and claim your bounties! 💸")
    except Exception as e:
        print(f"[-] Failed to generate report: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 auto_reporter.py <target_name>")
        print("Example: python3 auto_reporter.py tesla.com")
        sys.exit(1)
        
    target = sys.argv[1].lower()
    generate_report(target)
