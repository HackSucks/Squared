import subprocess
import os

CHROOT_DIR = "/root/archiso_work/squashfs-root"
OVERLAY_UPPER = "/tmp/overlay_upper"
OVERLAY_WORK = "/tmp/overlay_work"

# Lazy unmount all overlays
for path in [
    f"{CHROOT_DIR}/var/cache/pacman",
    f"{CHROOT_DIR}/var/lib/pacman",
    f"{CHROOT_DIR}/tmp",
    f"{CHROOT_DIR}"
]:
    subprocess.run(["sudo", "umount", "-l", path], stderr=subprocess.DEVNULL)

# Remove overlay workspace
for path in [OVERLAY_UPPER, OVERLAY_WORK]:
    subprocess.run(["sudo", "rm", "-rf", os.path.join(path, "*")])
