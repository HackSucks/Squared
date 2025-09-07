import os
import subprocess
import shutil
from shutil import copytree, which
import space

_active_chroot = None

ASCII_BANNER = r"""
 ____                                 _         
/ ___|  __ _ _   _  __ _ _ __ ___  __| |        
\___ \ / _` | | | |/ _` | '__/ _ \/ _` |  _____ 
 ___) | (_| | |_| | (_| | | |  __/ (_| | |_____|
|____/ \__, |\__,_|\__,_|_|  \___|\__,_|        
          |_|                                   
"""

def _ensure_mounts(chroot_dir: str):
    """Bind mounts required for chroot"""
    for fs in ["proc", "sys", "dev", "run"]:
        target = os.path.join(chroot_dir, fs)
        os.makedirs(target, exist_ok=True)
        subprocess.run(["sudo", "mount", "--bind", f"/{fs}", target], stderr=subprocess.DEVNULL)
    # DNS
    resolv_target = os.path.join(chroot_dir, "etc/resolv.conf")
    os.makedirs(os.path.dirname(resolv_target), exist_ok=True)
    subprocess.run(["sudo", "mount", "--bind", "/etc/resolv.conf", resolv_target], stderr=subprocess.DEVNULL)

def enter_chroot(chroot_dir: str, *args):
    global _active_chroot

    _active_chroot = os.path.abspath(chroot_dir)
    workdir = os.path.dirname(_active_chroot)
    airootfs = os.path.join(workdir, "airootfs")
    airootfs_rw = _active_chroot

    # --- Cleanup stale mounts ---
    for mnt in ["/tmp/mapp_overlay/merged", airootfs_rw]:
        subprocess.run(["sudo", "umount", "-l", mnt], stderr=subprocess.DEVNULL)
    shutil.rmtree("/tmp/mapp_overlay", ignore_errors=True)

    # --- Ensure airootfs exists ---
    if not os.path.exists(airootfs):
        if not hasattr(space, "ISO_PATH") or not os.path.exists(space.ISO_PATH):
            raise FileNotFoundError("ISO path not set or does not exist in space.ISO_PATH")
        print(f"[INFO] airootfs not found, extracting from ISO {space.ISO_PATH} ...")
        subprocess.run(["python3", "extract.py", space.ISO_PATH], check=True)
        if not os.path.exists(airootfs):
            raise RuntimeError("Extraction failed: airootfs still missing.")

    # --- Create writable copy if missing ---
    if not os.path.exists(airootfs_rw):
        print(f"[INFO] Creating writable copy at {airootfs_rw}...")
        copytree(airootfs, airootfs_rw, symlinks=True)
        subprocess.run(["sudo", "chmod", "-R", "u+rwX", airootfs_rw], check=True)
    else:
        print(f"[INFO] Writable copy already exists at {airootfs_rw}")

    # Setup overlay for upper layer
    space.setup_overlays(airootfs_rw)

    # Bind mounts into the merged overlay root
    _ensure_mounts(space.MERGE_DIR)

    # Init script
    init_script = os.path.join(space.MERGE_DIR, "root/.mapp_chroot_init.sh")
    os.makedirs(os.path.dirname(init_script), exist_ok=True)
    with open(init_script, "w") as f:
        f.write(f"""#!/bin/bash
set -u
cat << 'EOF'
{ASCII_BANNER}
EOF

echo "[CHROOT] Initializing pacman keyring..."
pacman-key --init || true
pacman-key --populate archlinux || true
echo "[CHROOT] Keyring ready. You can now use pacman."
exec /bin/bash
""")
    os.chmod(init_script, 0o755)

    # Launch in terminal
    arch_chroot = which("arch-chroot")
    term = which("konsole") or which("xterm") or which("gnome-terminal")
    if not arch_chroot or not term:
        raise RuntimeError("Missing arch-chroot or terminal emulator.")
    
    subprocess.Popen(
        ["setsid", term, "--hold", "-e", "sudo", arch_chroot, space.MERGE_DIR, "/bin/bash", "/root/.mapp_chroot_init.sh"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
    )

def _promote_dir(squash_root: str, name: str):
    """
    Ensure the final layout does this swap:
        name       -> name_2   (backup original if it exists)
        name_1     -> name     (promote modified)
    Handles files/dirs/symlinks using sudo mv/rm so ownership isn't an issue.
    """
    d   = os.path.join(squash_root, name)
    d1  = os.path.join(squash_root, f"{name}_1")
    d2  = os.path.join(squash_root, f"{name}_2")

    # If we have a modified dir (name_1), promote it to name
    if os.path.lexists(d1):
        # Move original out of the way to name_2
        if os.path.lexists(d):
            # Remove any stale name_2
            if os.path.lexists(d2):
                subprocess.run(["sudo", "rm", "-rf", d2], check=True)
            subprocess.run(["sudo", "mv", d, d2], check=True)
        # Promote name_1 -> name
        subprocess.run(["sudo", "mv", d1, d], check=True)
    else:
        # If there is no name_1 but there's a leftover name_2 and no name, restore it to name
        if os.path.lexists(d2) and not os.path.lexists(d):
            subprocess.run(["sudo", "mv", d2, d], check=True)

def unchroot(commit=True, *args):
    global _active_chroot
    if not _active_chroot:
        return

    workdir = os.path.dirname(_active_chroot)
    sfs_out = os.path.join(workdir, "airootfs.sfs")

    if commit:
        # Merge overlay upper into writable airootfs
        space.commit_overlay_to_airootfs(space.UPPER_DIR, _active_chroot)

        # Step 1: Rebuild temporary SFS from current chroot
        temp_sfs = os.path.join(workdir, "airootfs_tmp.sfs")
        print("[INFO] Rebuilding temporary airootfs.sfs from writable copy...")
        subprocess.run(["sudo", "mksquashfs", _active_chroot, temp_sfs, "-comp", "xz"], check=True)

        # Step 2: Unsquash the SFS to a temp dir
        squash_dir = os.path.join(workdir, "squashfs_root")
        subprocess.run(["sudo", "unsquashfs", "-d", squash_dir, temp_sfs], check=True)

        # Step 3: Perform the rename/swap:
        #   <d> -> <d>_2   and   <d>_1 -> <d>
        for d in ["usr", "bin", "sbin", "lib", "lib64", "opt", "etc"]:
            _promote_dir(squash_dir, d)

        # Step 4: Resquash final rootfs
        print("[INFO] Rebuilding final merged airootfs.sfs...")
        subprocess.run(["sudo", "mksquashfs", squash_dir, sfs_out, "-comp", "xz"], check=True)
        print(f"[INFO] New merged airootfs.sfs at {sfs_out}")

        # Clean up temp directories
        shutil.rmtree(squash_dir, ignore_errors=True)
        os.remove(temp_sfs)

    # Unmount overlay and binds
    for fs in ["proc", "sys", "dev", "run", "etc/resolv.conf"]:
        target = os.path.join(space.MERGE_DIR, fs)
        subprocess.run(["sudo", "umount", "-l", target], stderr=subprocess.DEVNULL)

    space.cleanup_overlays()
    _active_chroot = None
    subprocess.run(["chmod", "+x", "fixroot.sh"], check=True)
subprocess.run(["sudo", "./fixroot.sh"], check=True)

