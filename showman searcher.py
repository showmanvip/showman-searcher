# showman_searcher.py
# Created by: @Realshowman_7
# Requirements:
# - Python 3.x
# - Modules: tqdm, colorama
# Install them via: pip install tqdm colorama

import os
import re
from tqdm import tqdm
from colorama import init, Fore, Style

init(autoreset=True)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
SEEN_LINES_FILE = os.path.join("logs", "seen_lines.txt")

# Ask if user wants to reset seen lines history
if os.path.exists(SEEN_LINES_FILE):
    reset = input(Fore.YELLOW + "Do you want to reset the history? (y/n): ").strip().lower()
    if reset == 'y':
        os.remove(SEEN_LINES_FILE)
        print(Fore.GREEN + "History reset successfully!")

# Load previously seen lines
seen_lines = set()
if os.path.exists(SEEN_LINES_FILE):
    with open(SEEN_LINES_FILE, 'r', encoding='utf-8') as f:
        seen_lines = set(line.strip() for line in f if line.strip())

# Stylized banner
banner = f"""
{Fore.CYAN + Style.BRIGHT}
███████╗██╗  ██╗ ██████╗ ██╗    ██╗███╗   ███╗ █████╗ ███╗   ██╗
██╔════╝██║  ██║██╔═══██╗██║    ██║████╗ ████║██╔══██╗████╗  ██║
███████╗███████║██║   ██║██║ █╗ ██║██╔████╔██║███████║██╔██╗ ██║
╚════██║██╔══██║██║   ██║██║███╗██║██║╚██╔╝██║██╔══██║██║╚██╗██║
███████║██║  ██║╚██████╔╝╚███╔███╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║
╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
{Style.RESET_ALL}                                   by {Fore.YELLOW}@Realshowman_7
"""
print(banner)

# Ask for the keyword to search
keyword = input(Fore.CYAN + Style.BRIGHT + "What word would you like to search for? ").strip()
output_file = f"{keyword}.txt"

# Keywords to block
blocked_keywords = ["gmail", "yahoo", "facebook", "google", "www", "telegram", "android", "hotmail"]
blocked_pattern = re.compile(r"|".join(blocked_keywords), re.IGNORECASE)
non_ascii_pattern = re.compile(r"[^\x00-\x7F]")

# Get all .txt files excluding the logs folder and output file
all_txt_files = [f for f in os.listdir('.')
                 if f.endswith('.txt') and f != output_file and not f.startswith('logs') and os.path.isfile(f)]

all_results = []
total_files = len(all_txt_files)

for idx, file in enumerate(all_txt_files, 1):
    print(Fore.YELLOW + f"\n[{idx}/{total_files}] Searching in: {file}")
    matched = []
    try:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in tqdm(lines, desc=f"Processing {file}", unit="line"):
                line = line.strip()
                if keyword.lower() in line.lower() and line not in seen_lines:
                    matched.append(line)
                    seen_lines.add(line)
    except Exception as e:
        print(Fore.RED + f"Failed to read {file}: {e}")
        continue

    print(Fore.GREEN + f"Found {len(matched)} new lines in {file}")
    all_results.extend(matched)

# Post-processing results
filtered = []
for line in all_results:
    if blocked_pattern.search(line) or non_ascii_pattern.search(line):
        continue
    if not line.lower().startswith("http"):
        line = "https://" + line
    filtered.append(line)

# Remove duplicates
final_results = list(dict.fromkeys(filtered))

# Save results
with open(output_file, 'w', encoding='utf-8') as out:
    out.write("\n".join(final_results))

# Save to seen history
with open(SEEN_LINES_FILE, 'a', encoding='utf-8') as f:
    for line in final_results:
        f.write(line + '\n')

# Confirm deletion of processed files
if total_files > 0:
    print(Fore.CYAN + "\nDo you want to delete the processed files?")
    for i, f in enumerate(all_txt_files, 1):
        print(f"{i}. {f}")
    choice = input(Fore.YELLOW + "Delete all above files? (y/n): ").strip().lower()
    if choice == 'y':
        del_mode = input(Fore.YELLOW + "1- Permanent delete\n2- Send to Recycle Bin\nChoose delete mode (1/2): ").strip()
        for f in all_txt_files:
            try:
                if del_mode == '1':
                    os.remove(f)
                elif del_mode == '2':
                    import send2trash
                    send2trash.send2trash(f)
            except Exception as e:
                print(Fore.RED + f"Error deleting {f}: {e}")

print(Fore.GREEN + f"\nDone! Results saved to {output_file}")
