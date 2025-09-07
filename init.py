# init.py
import os
import sys
import subprocess

def main():
    if os.geteuid() != 0:
        # Not root; re-run with sudo
        print("[INFO] Not running as root. Elevating privileges...")
        subprocess.run(["sudo", sys.executable, "mapp.py"] + sys.argv[1:])
    else:
        # Already root; run mapp.py directly
        subprocess.run([sys.executable, "mapp.py"] + sys.argv[1:])

if __name__ == "__main__":
    main()
