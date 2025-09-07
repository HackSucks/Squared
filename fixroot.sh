#!/bin/bash
set -euo pipefail

# Define paths
WORKDIR="$(pwd)/workdir"
SQUASHDIR="$WORKDIR/squashfs-root"
AIROOTFS="$WORKDIR/airootfs.sfs"

echo "[*] Extracting original squashfs..."
cd "$WORKDIR"
unsquashfs "$AIROOTFS"

echo "[*] Fixing root filesystem overlays inside: $SQUASHDIR"
cd "$SQUASHDIR"

# Merge duplicate dirs like usr usr_1, etc etc_1, var var_1, root root_1...
for dir in bin boot etc home lib lib64 opt root run sbin srv sys tmp usr var; do
    if [[ -d "${dir}_1" ]]; then
        echo "[*] Found split directory: $dir / ${dir}_1"

        # Backup original if it exists
        if [[ -d "$dir" ]]; then
            mv "$dir" "${dir}_2"
        fi

        # Promote _1 → main
        mv "${dir}_1" "$dir"

        # Merge back with rsync
        if [[ -d "${dir}_2" ]]; then
            echo "[*] Merging ${dir}_2 → $dir"
            rsync -aHAX "${dir}_2"/ "$dir"/
            rm -rf "${dir}_2"
        fi
    fi
done

echo "[*] Cleaning up leftovers..."
find . -maxdepth 1 -type d -regex ".*_[12]" -exec rm -rf {} +

cd "$WORKDIR"

echo "[*] Repacking squashfs..."
mksquashfs "$SQUASHDIR" fixed_airootfs.sfs -comp xz -b 1M -Xdict-size 1M -noappend

echo "[*] Removing extracted squashfs-root..."
rm -rf "$SQUASHDIR"

echo "[*] Replacing old airootfs.sfs..."
rm -f "$AIROOTFS"
mv fixed_airootfs.sfs airootfs.sfs

echo
echo "[+] Done!"
echo "Your airootfs.sfs has been fixed and replaced automatically."
