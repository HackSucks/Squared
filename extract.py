import os
import subprocess
import sys

def is_mounted(path):
    with open("/proc/mounts", "r") as f:
        return any(path in line.split()[1] for line in f)

def force_umount(path):
    """Try normal unmount, then lazy, then detach loop devices if needed."""
    if is_mounted(path):
        print(f"[INFO] {path} already mounted. Trying to unmount...")
        try:
            subprocess.run(["sudo", "umount", path], check=True)
        except subprocess.CalledProcessError:
            print(f"[WARN] Normal unmount failed, trying lazy unmount...")
            subprocess.run(["sudo", "umount", "-l", path], check=True)

        # Check for associated loop device and detach
        result = subprocess.run(["mount"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if path in line:
                device = line.split()[0]
                if device.startswith("/dev/loop"):
                    print(f"[INFO] Detaching loop device {device}")
                    subprocess.run(["sudo", "losetup", "-d", device], check=False)

def extract_iso(iso_path, work_dir="workdir", mount_dir="mnt_iso"):
    try:
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(mount_dir, exist_ok=True)

        # Force unmount if ISO already mounted
        force_umount(mount_dir)

        # Mount ISO
        subprocess.run(["sudo", "mount", "-o", "loop", iso_path, mount_dir], check=True)

        # Copy airootfs.sfs
        sfs_path = os.path.join(mount_dir, "arch/x86_64/airootfs.sfs")
        if not os.path.exists(sfs_path):
            raise FileNotFoundError("airootfs.sfs not found in ISO")

        subprocess.run(["cp", sfs_path, work_dir], check=True)
        print(f"[INFO] Extracted airootfs.sfs to {work_dir}")

        # Mount airootfs.sfs
        sfs_mount = os.path.join(work_dir, "airootfs")
        os.makedirs(sfs_mount, exist_ok=True)
        force_umount(sfs_mount)
        subprocess.run(["sudo", "mount", "-t", "squashfs", "-o", "loop", os.path.join(work_dir, "airootfs.sfs"), sfs_mount], check=True)
        print(f"[INFO] Mounted airootfs.sfs at {sfs_mount}")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract.py <path-to-iso>")
        sys.exit(1)

    extract_iso(sys.argv[1])
