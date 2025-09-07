import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import chroot

ASCII_BANNER = r"""
 ____                                 _         
/ ___|  __ _ _   _  __ _ _ __ ___  __| |        
\___ \ / _` | | | |/ _` | '__/ _ \/ _` |  _____ 
 ___) | (_| | |_| | (_| | | |  __/ (_| | |_____|
|____/ \__, |\__,_|\__,_|_|  \___|\__,_|        
          |_|                                   
  ____ _                     _     ___       _             __                
 / ___| |__  _ __ ___   ___ | |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___ 
| |   | '_ \| '__/ _ \ / _ \| __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \
| |___| | | | | | (_) | (_) | |_   | || | | ||  __/ |  | _| (_| | (_|  __/
 \____|_| |_|_|  \___/ \___/ \__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___|
"""

class ChrootGUI(QMainWindow):
    def __init__(self, chroot_dir=None):
        super().__init__()
        self.setWindowTitle("Squared - Chroot GUI")
        self.setGeometry(300, 300, 800, 600)

        self.chroot_dir = chroot_dir
        self.chroot_name = "default"

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.console.setFont(font)
        self.console.setText(ASCII_BANNER)
        layout.addWidget(self.console)

        # Select chroot directory button
        self.select_button = QPushButton("Select Chroot Directory")
        self.select_button.clicked.connect(self.select_chroot_dir)
        layout.addWidget(self.select_button)

        # Enter chroot button
        self.enter_button = QPushButton("Enter Chroot")
        self.enter_button.clicked.connect(self.run_chroot)
        layout.addWidget(self.enter_button)

        # Unchroot button
        self.unchroot_button = QPushButton("Unchroot / Cleanup")
        self.unchroot_button.clicked.connect(self.run_unchroot)
        layout.addWidget(self.unchroot_button)

        if chroot_dir:
            self.console.append(f"\n[INFO] Loaded chroot directory: {chroot_dir}")

    def select_chroot_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Chroot Directory")
        if dir_path:
            self.chroot_dir = dir_path
            self.console.append(f"\n[INFO] Selected chroot directory: {dir_path}")

    def run_chroot(self):
        if not self.chroot_dir:
            self.console.append("\n[ERROR] No chroot directory selected.")
            return
        self.console.append(f"\n[INFO] Launching chroot for {self.chroot_dir}...")
        try:
            chroot.enter_chroot(self.chroot_dir, self.chroot_name)
            self.console.append(f"[INFO] Chroot launched successfully.")
        except Exception as e:
            self.console.append(f"[ERROR] Failed to launch chroot: {e}")

    def run_unchroot(self):
        if not self.chroot_dir:
            self.console.append("\n[ERROR] No chroot directory selected for cleanup.")
            QMessageBox.warning(self, "Chroot", "No chroot directory selected.")
            return
        try:
            chroot.unchroot(self.chroot_dir, self.chroot_name)
            self.console.append("[INFO] Chroot overlays unmounted and cleaned up.")
            QMessageBox.information(self, "Chroot", "Chroot unmounted and cleaned up.")
        except Exception as e:
            self.console.append(f"[ERROR] Failed to unchroot: {e}")
            QMessageBox.critical(self, "Chroot", f"Failed to unchroot: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ChrootGUI()
    gui.show()
    sys.exit(app.exec())
