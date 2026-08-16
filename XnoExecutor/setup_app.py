import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

APP_NAME = "Xno Executor"
DEFAULT_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                           "Programs", "XnoExecutor")


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def make_shortcut(lnk_path, target, workdir):
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$sc = $ws.CreateShortcut('{lnk_path}'); "
        f"$sc.TargetPath = '{target}'; "
        f"$sc.WorkingDirectory = '{workdir}'; "
        "$sc.Description = 'Xno Executor'; "
        "$sc.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=False)


class SetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Xno Executor - Setup")
        self.geometry("520x360")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f1a")

        ctk.CTkLabel(self, text="XNO EXECUTOR", font=("Segoe UI", 26, "bold"),
                     text_color="#7fd4ff").pack(pady=(28, 0))
        ctk.CTkLabel(self, text="Install to your PC", font=("Segoe UI", 12),
                     text_color="#8fa3c8").pack(pady=(2, 18))

        self.dir_var = tk.StringVar(value=DEFAULT_DIR)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=34)
        ctk.CTkEntry(row, textvariable=self.dir_var, height=36, fg_color="#0e1526",
                     text_color="#e5ecff").pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse", width=90, height=36, corner_radius=8,
                      fg_color="#1e3a8a", hover_color="#2748b8",
                      command=self._browse).pack(side="left", padx=(8, 0))

        self.status = ctk.CTkLabel(self, text="", font=("Segoe UI", 12),
                                   text_color="#9db4d6")
        self.status.pack(pady=(16, 4))

        self.progress = ctk.CTkProgressBar(self, height=10, corner_radius=5,
                                           progress_color="#3b82f6")
        self.progress.set(0)
        self.progress.pack(fill="x", padx=34)

        self.install_btn = ctk.CTkButton(self, text="Install", font=("Segoe UI", 14, "bold"),
                                         height=44, corner_radius=10, fg_color="#16a34a",
                                         hover_color="#1fb85a", command=self._install)
        self.install_btn.pack(pady=(20, 0))

        self.launch = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Launch Xno Executor after install", variable=self.launch,
                        font=("Segoe UI", 12), fg_color="#3b82f6", hover_color="#2748b8",
                        checkmark_color="#ffffff").pack(pady=(10, 20))

    def _browse(self):
        path = filedialog.askdirectory(initialdir=self.dir_var.get())
        if path:
            self.dir_var.set(path)

    def _install(self):
        dest_dir = self.dir_var.get().strip()
        if not dest_dir:
            self.status.configure(text="Choose an install folder.", text_color="#ff5c5c")
            return
        try:
            self.install_btn.configure(state="disabled")
            self.progress.set(0.15)
            self.status.configure(text="Copying files...", text_color="#9db4d6")
            self.update_idletasks()

            os.makedirs(dest_dir, exist_ok=True)
            exe_src = resource_path(os.path.join("app", "XnoExecutor.exe"))
            exe_dst = os.path.join(dest_dir, "XnoExecutor.exe")
            if not os.path.exists(exe_src):
                raise RuntimeError("XnoExecutor.exe not found in installer bundle.")
            shutil.copy2(exe_src, exe_dst)
            self.progress.set(0.6)

            self.status.configure(text="Creating shortcuts...", text_color="#9db4d6")
            self.update_idletasks()

            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            start_menu = os.path.join(os.environ.get("APPDATA", ""),
                                      "Microsoft", "Windows", "Start Menu",
                                      "Programs")
            for folder in (desktop, start_menu):
                if os.path.isdir(folder):
                    make_shortcut(os.path.join(folder, f"{APP_NAME}.lnk"),
                                  exe_dst, dest_dir)
            self.progress.set(0.9)

            self.status.configure(text="Install complete!", text_color="#4ade80")
            self.progress.set(1.0)
            self.install_btn.configure(text="Installed", state="disabled")
            if self.launch.get():
                self.after(600, lambda: subprocess.Popen([exe_dst],
                                                         cwd=dest_dir,
                                                         creationflags=subprocess.CREATE_NO_WINDOW))
        except Exception as exc:
            self.status.configure(text=f"Install failed: {exc}", text_color="#ff5c5c")
            self.install_btn.configure(state="normal")


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    SetupApp().mainloop()


if __name__ == "__main__":
    main()
