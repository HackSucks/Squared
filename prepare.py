import os
import subprocess
import shutil

WORKDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "workdir"))
AIROOTFS_SFS = os.path.join(WORKDIR, "airootfs.sfs")
AIROOTFS = os.path.join(WORKDIR, "airootfs")
AIROOTFS_RW = os.path.join(WORKDIR, "airootfs_rw")

# --- Step 1: Extract airootfs if missing ---
if not os.path.exists(AIROOTFS):
    if not os.path.exists(AIROOTFS_SFS):
        raise FileNotFoundError(f"{AIROOTFS_SFS} not found!")
    print(f"[INFO] Extracting airootfs from {AIROOTFS_SFS} ...")
    subprocess.run(["sudo", "unsquashfs", "-d", AIROOTFS, AIROOTFS_SFS], check=True)
else:
    print(f"[INFO] airootfs already exists at {AIROOTFS}")

# --- Step 2: Create writable copy ---
if not os.path.exists(AIROOTFS_RW):
    print(f"[INFO] Creating writable copy at {AIROOTFS_RW} ...")
    shutil.copytree(AIROOTFS, AIROOTFS_RW, symlinks=True)
    subprocess.run(["sudo", "chmod", "-R", "u+rwX", AIROOTFS_RW], check=True)
else:
    print(f"[INFO] Writable copy already exists at {AIROOTFS_RW}")

# --- Step 3: Launch chroot GUI ---
CHGUI = os.path.join(os.path.dirname(__file__), "chgui.py")
if os.path.exists(CHGUI):
    print("[INFO] Launching chroot GUI ...")
    subprocess.Popen(["python3", CHGUI, AIROOTFS_RW])
else:
    print("[WARN] chgui.py not found, skipping GUI launch")
