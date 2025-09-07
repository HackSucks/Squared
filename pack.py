#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys

def pack_iso(original_iso, chroot_dir, new_iso):
    temp_mount = "/mnt/original_iso"
    temp_iso_dir = "/tmp/iso_temp"

    os.makedirs(temp_mount, exist_ok=True)
    os.makedirs(temp_iso_dir, exist_ok=True)

    print("[*] Rebuilding airootfs.sfs...")
    new_sfs = os.path.join("/tmp", "airootfs.sfs")
    subprocess.run(["sudo", "mksquashfs", chroot_dir, new_sfs, "-comp", "xz", "-e", "boot"], check=True)

    print("[*] Mounting original ISO...")
    subprocess.run(["sudo", "mount", "-o", "loop", original_iso, temp_mount], check=True)

    print("[*] Copying ISO contents...")
    subprocess.run(["rm", "-rf", temp_iso_dir])
    os.makedirs(temp_iso_dir, exist_ok=True)
    subprocess.run(["cp", "-rT", temp_mount, temp_iso_dir], check=True)

    print("[*] Replacing airootfs.sfs...")
    shutil.copy(new_sfs, os.path.join(temp_iso_dir, "airootfs.sfs"))

    print("[*] Rebuilding new ISO...")
    subprocess.run([
        "xorriso", "-as", "mkisofs",
        "-o", new_iso,
        "-b", "isolinux/isolinux.bin",
        "-c", "isolinux/boot.cat",
        "-no-emul-boot",
        "-boot-load-size", "4",
        "-boot-info-table",
        "-isohybrid-mbr", "/usr/lib/ISOLINUX/isohdpfx.bin",
        temp_iso_dir
    ], check=True)

    subprocess.run(["sudo", "umount", temp_mount])
    print(f"[*] New ISO created: {new_iso}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 pack.py <original_iso> <chroot_dir> <new_iso>")
        sys.exit(1)

    orig_iso = sys
