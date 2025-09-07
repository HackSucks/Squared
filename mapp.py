import subprocess
import os
import shutil
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QCheckBox
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Squared - Main App")
        self.setGeometry(200, 200, 900, 700)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Console window
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        font = QFont("Courier New", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.console.setFont(font)
        self.layout.addWidget(self.console)

        # ASCII art
        ascii_art = r"""
 ____                                 _  //\  ___         
/ ___|  __ _ _   _  __ _ _ __ ___  __| ||/_\||_  )        
\___ \ / _` | | | |/ _` | '__/ _ \/ _` | /_\  / /   _____ 
 ___) | (_| | | | | (_| | | |  __/ (_| |/ _ \/___| |_____|
|____/ \__, |\__,_|\__,_|_|  \___|\__,_/_/ \_\            
          |_|                                             
"""
        self.console.setText(ascii_art)

        # --- Buttons ---
        self.extract_button = QPushButton("Extract ISO")
        self.extract_button.clicked.connect(self.run_extract)
        self.layout.addWidget(self.extract_button)

        self.chroot_button = QPushButton("Enter Chroot")
        self.chroot_button.clicked.connect(self.enter_chroot)
        self.layout.addWidget(self.chroot_button)

        self.select_iso_button = QPushButton("Select Original ISO")
        self.select_iso_button.clicked.connect(self.select_original_iso)
        self.layout.addWidget(self.select_iso_button)

        self.select_sfs_button = QPushButton("Select New airootfs.sfs")
        self.select_sfs_button.clicked.connect(self.select_new_sfs)
        self.layout.addWidget(self.select_sfs_button)

        self.select_new_iso_button = QPushButton("Select Destination for New ISO")
        self.select_new_iso_button.clicked.connect(self.select_new_iso)
        self.layout.addWidget(self.select_new_iso_button)

        self.repack_button = QPushButton("Repack ISO (Hybrid)")
        self.repack_button.clicked.connect(self.repack_iso)
        self.layout.addWidget(self.repack_button)

        # NEW BUTTONS
        self.repack_bios_button = QPushButton("Repack ISO (BIOS Only)")
        self.repack_bios_button.clicked.connect(self.repack_bios_only_iso)
        self.layout.addWidget(self.repack_bios_button)

        self.repack_uefi_button = QPushButton("Repack ISO (UEFI Only)")
        self.repack_uefi_button.clicked.connect(self.repack_uefi_only_iso)
        self.layout.addWidget(self.repack_uefi_button)

        self.dark_mode_toggle = QCheckBox("Dark Mode")
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        self.layout.addWidget(self.dark_mode_toggle)

        # --- Paths ---
        self.original_iso = None
        self.new_sfs = None
        self.new_iso = None

    # --- Button Handlers ---
    def run_extract(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Arch ISO", "", "ISO Files (*.iso)")
        if file_name:
            try:
                result = subprocess.run(
                    ["python3", "extract.py", file_name],
                    capture_output=True,
                    text=True
                )
                self.console.append("\n[extract.py output]:\n" + result.stdout)
                if result.stderr:
                    self.console.append("\n[Error]:\n" + result.stderr)
            except Exception as e:
                self.console.append(f"\n[Exception running extract.py]: {e}")

    def enter_chroot(self):
        chroot_dir = QFileDialog.getExistingDirectory(self, "Select Chroot Directory")
        if not chroot_dir:
            return

        if not os.path.exists("prepare.py"):
            self.console.append("[ERROR] prepare.py not found.")
            return

        try:
            subprocess.Popen(["python3", "prepare.py", chroot_dir])
            self.console.append(f"[INFO] Launched chroot GUI for: {chroot_dir}")
        except Exception as e:
            self.console.append(f"[ERROR] Failed to launch chroot GUI: {e}")

    def select_original_iso(self):
        iso_path, _ = QFileDialog.getOpenFileName(self, "Select Original ISO", "", "ISO Files (*.iso)")
        if iso_path:
            self.original_iso = iso_path
            self.console.append(f"[INFO] Original ISO selected: {iso_path}")

    def select_new_sfs(self):
        sfs_path, _ = QFileDialog.getOpenFileName(self, "Select New airootfs.sfs", "", "SFS Files (*.sfs)")
        if sfs_path:
            self.new_sfs = sfs_path
            self.console.append(f"[INFO] New airootfs.sfs selected: {sfs_path}")

    def select_new_iso(self):
        iso_path, _ = QFileDialog.getSaveFileName(self, "Select Destination for New ISO", "", "ISO Files (*.iso)")
        if iso_path:
            self.new_iso = iso_path
            self.console.append(f"[INFO] New ISO destination: {iso_path}")

    def repack_iso(self):
        if not self.original_iso or not self.new_sfs or not self.new_iso:
            self.console.append("[ERROR] Please select original ISO, new SFS, and destination first.")
            return

        try:
            self.console.append(f"[INFO] Repacking ISO with new airootfs.sfs: {self.new_sfs}")
            self.pack_iso(self.original_iso, self.new_sfs, self.new_iso, mode="hybrid")
            self.console.append(f"[INFO] New ISO created: {self.new_iso}")
        except subprocess.CalledProcessError as e:
            self.console.append(f"[ERROR] Subprocess failed: {e}\nOutput: {e.output}")
        except Exception as e:
            self.console.append(f"[ERROR] Failed to repack ISO: {e}")

    def repack_bios_only_iso(self):
        if not self.original_iso or not self.new_sfs or not self.new_iso:
            self.console.append("[ERROR] Please select original ISO, new SFS, and destination first.")
            return

        try:
            self.console.append("[INFO] Repacking ISO (BIOS Only)...")
            self.pack_iso(self.original_iso, self.new_sfs, self.new_iso, mode="bios")
            self.console.append(f"[INFO] BIOS-only ISO created: {self.new_iso}")
        except Exception as e:
            self.console.append(f"[ERROR] Failed to build BIOS-only ISO: {e}")

    def repack_uefi_only_iso(self):
        if not self.original_iso or not self.new_sfs or not self.new_iso:
            self.console.append("[ERROR] Please select original ISO, new SFS, and destination first.")
            return

        try:
            self.console.append("[INFO] Repacking ISO (UEFI Only)...")
            self.pack_iso(self.original_iso, self.new_sfs, self.new_iso, mode="uefi")
            self.console.append(f"[INFO] UEFI-only ISO created: {self.new_iso}")
        except Exception as e:
            self.console.append(f"[ERROR] Failed to build UEFI-only ISO: {e}")

    # --- ISO Packing ---
    def pack_iso(self, original_iso, new_sfs, new_iso, mode="hybrid"):
        temp_mount = "/mnt/original_iso"
        temp_iso_dir = "/tmp/iso_temp"

        self.console.append("[INFO] Preparing temporary directories...")
        os.makedirs(temp_mount, exist_ok=True)
        shutil.rmtree(temp_iso_dir, ignore_errors=True)
        os.makedirs(temp_iso_dir, exist_ok=True)

        # Mount original ISO
        self.console.append("[INFO] Mounting original ISO...")
        if os.path.ismount(temp_mount):
            self.console.append("[INFO] Original ISO already mounted, unmounting first...")
            subprocess.run(["sudo", "umount", "-l", temp_mount], check=True)
        subprocess.run(["sudo", "mount", "-o", "loop", original_iso, temp_mount], check=True)

        # Copy ISO contents
        self.console.append("[INFO] Copying ISO contents ...")
        shutil.rmtree(temp_iso_dir)
        os.makedirs(temp_iso_dir, exist_ok=True)
        subprocess.run(["cp", "-rT", temp_mount, temp_iso_dir], check=True)

        # Replace airootfs.sfs
        self.console.append("[INFO] Replacing airootfs.sfs ...")
        orig_sfs_path = os.path.join(temp_iso_dir, "arch", "x86_64", "airootfs.sfs")
        os.makedirs(os.path.dirname(orig_sfs_path), exist_ok=True)
        shutil.copy(new_sfs, orig_sfs_path)

        # Ensure EFI path exists with correct case
        efi_boot_dir = os.path.join(temp_iso_dir, "EFI", "BOOT")
        if not os.path.isdir(efi_boot_dir):
            os.makedirs(efi_boot_dir, exist_ok=True)

        for f in os.listdir(efi_boot_dir):
            src = os.path.join(efi_boot_dir, f)
            dst = os.path.join(efi_boot_dir, f.upper())
            if src != dst:
                os.rename(src, dst)

        # Rebuild ISO
        if mode == "bios":
            self.console.append("[INFO] Building BIOS-only ISO ...")
            subprocess.run([
                "xorriso", "-as", "mkisofs",
                "-o", new_iso,
                "-b", "boot/syslinux/isolinux.bin",
                "-c", "boot/syslinux/boot.cat",
                "-no-emul-boot",
                "-boot-load-size", "4",
                "-boot-info-table",
                "-isohybrid-mbr", "/usr/lib/syslinux/bios/isohdpfx.bin",
                temp_iso_dir
            ], check=True)

        elif mode == "uefi":
            self.console.append("[INFO] Building UEFI-only ISO ...")
            
            # Use grub-mkstandalone to create a reliable EFI bootloader
            self.console.append("[INFO] Creating GRUB-based EFI bootloader...")
            grub_efi_boot_dir = os.path.join(temp_iso_dir, "EFI", "BOOT")
            grub_efi_file = os.path.join(grub_efi_boot_dir, "BOOTX64.EFI")
            
            # The grub.cfg must be present for grub-mkstandalone
            grub_cfg_dir = os.path.join(temp_iso_dir, "boot", "grub")
            if not os.path.isdir(grub_cfg_dir):
                self.console.append("[ERROR] GRUB configuration directory not found. Exiting.")
                return
            
            subprocess.run([
                "grub-mkstandalone",
                "-o", grub_efi_file,
                "-O", "x86_64-efi",
                "-d", "/usr/lib/grub/x86_64-efi",
                "--modules=part_gpt part_msdos normal squash4",
                f"{temp_iso_dir}/EFI/BOOT/grub.cfg={temp_iso_dir}/boot/grub/grub.cfg",
                f"--fonts=/usr/share/grub/unicode.pf2={temp_iso_dir}/usr/share/grub/unicode.pf2",
                f"{temp_iso_dir}/EFI/BOOT"
            ], check=True)

            # Build the ISO using the newly created EFI bootloader
            self.console.append("[INFO] Building ISO with new EFI bootloader...")
            subprocess.run([
                 "xorriso", "-as", "mkisofs",
                 "-iso-level", "3",
                 "-full-iso9660-filenames",
                 "-o", new_iso,
                 "-eltorito-alt-boot",
                 "-e", "EFI/BOOT/BOOTX64.EFI",
                 "-no-emul-boot",
                 "-isohybrid-gpt-basdat",
                 temp_iso_dir
            ], check=True)
            
        else:  # default hybrid
            self.console.append("[INFO] Building BIOS+UEFI hybrid ISO ...")
            subprocess.run([
                "xorriso", "-as", "mkisofs",
                "-o", new_iso,
                "-b", "boot/syslinux/isolinux.bin",
                "-c", "boot/syslinux/boot.cat",
                "-no-emul-boot",
                "-boot-load-size", "4",
                "-boot-info-table",
                "-isohybrid-mbr", "/usr/lib/syslinux/bios/isohdpfx.bin",
                "-eltorito-alt-boot",
                "-e", "EFI/BOOT/BOOTX64.EFI",
                "-no-emul-boot",
                "-isohybrid-gpt-basdat",
                temp_iso_dir
            ], check=True)

        # Unmount original ISO
        self.console.append("[INFO] Unmounting original ISO ...")
        subprocess.run(["sudo", "umount", temp_mount])

    # --- Dark Mode ---
    def toggle_dark_mode(self, state):
        if state == Qt.CheckState.Checked.value:
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            QApplication.instance().setPalette(dark_palette)
        else:
            QApplication.instance().setPalette(QApplication.instance().style().standardPalette())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
