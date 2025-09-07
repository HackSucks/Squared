import os
import subprocess
from pathlib import Path

OVERLAY_BASE = "/tmp/mapp_overlay"
UPPER_DIR = os.path.join(OVERLAY_BASE, "upper")
WORK_DIR = os.path.join(OVERLAY_BASE, "work")
MERGE_DIR = os.path.join(OVERLAY_BASE, "merged")

def setup_overlays(airootfs_rw: str):
    """
    Sets up overlayfs for chroot.
    All changes go to upper overlay.
    """
    os.makedirs(UPPER_DIR, exist_ok=True)
    os.makedirs(WORK_DIR, exist_ok=True)
    os.makedirs(MERGE_DIR, exist_ok=True)

    # Mount overlay
    subprocess.run([
        "sudo", "mount", "-t", "overlay",
        "overlay",
        "-o", f"lowerdir={airootfs_rw},upperdir={UPPER_DIR},workdir={WORK_DIR}",
        MERGE_DIR
    ], check=True)

def cleanup_overlays():
    """
    Unmounts overlay and cleans temporary dirs
    """
    if os.path.ismount(MERGE_DIR):
        subprocess.run(["sudo", "umount", "-l", MERGE_DIR], stderr=subprocess.DEVNULL)
    # Optional: keep upper/work for debugging or remove
    # subprocess.run(["sudo", "rm", "-rf", OVERLAY_BASE])

def commit_overlay_to_airootfs(upper_dir: str, lower_dir: str):
    """
    Merges the upper overlay into the writable airootfs_rw
    """
    # Use rsync to merge changes safely
    subprocess.run([
        "sudo", "rsync", "-aHAX", "--delete", f"{upper_dir}/", lower_dir
    ], check=True)
