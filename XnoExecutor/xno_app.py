import json
import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from xno_engine import XnoEngine, STATE_DETACHED, STATE_DETECTED, STATE_ATTACHED
from xno_rainbow import Rainbow
from xno_theme import (BG_DARK, BG_PANEL, BG_CARD, FG_TEXT, FG_MUTED,
                       FONT_TITLE, FONT_HERO, FONT_SUB, FONT_NAV, FONT_BTN,
                       FONT_BODY, FONT_SMALL, FONT_CODE, FONT_TERM)

APP_DIR = os.path.dirname(os.path.abspath(__file__))

NAV_ITEMS = [("Home", 0), ("Script Hub", 1), ("Execute", 2), ("Settings", 3)]


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", APP_DIR)
    return os.path.join(base, rel)


def data_dir():
    if getattr(sys, "frozen", False):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "XnoExecutor")
    else:
        d = APP_DIR
    os.makedirs(d, exist_ok=True)
    return d


DATA_DIR = data_dir()
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
SCRIPTS_DIR = os.path.join(DATA_DIR, "scripts")


def ensure_scripts():
    src = resource_path("scripts")
    if not os.path.isdir(src):
        return
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    for name in os.listdir(src):
        dst = os.path.join(SCRIPTS_DIR, name)
        if not os.path.exists(dst):
            try:
                shutil.copy2(os.path.join(src, name), dst)
            except Exception:
                pass


class XnoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Xno Executor")
        self.geometry("1000x680")
        self.minsize(880, 580)
        self.configure(fg_color=BG_DARK)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.engine = XnoEngine(log=self._term_print)
        self.rainbow = Rainbow()
        self.config = self._load_config()
        self.engine.dll_path = self.config.get("dll_path", "")
        ensure_scripts()

        self._build_ui()
        self._bind_keys()

        self.attributes("-alpha", 0.0)
        for i in range(1, 21):
            self.after(i * 14, lambda a=i / 20: self.attributes("-alpha", a))

        self._term_print("[Xno] Welcome to Xno Executor.", "accent")
        self._term_print("[Xno] Start Roblox, join a game, then press Attach (F7).")
        self._term_print("[Xno] Paste a script and press Execute (F8).", "accent")
        self._rainbow_loop()
        self._watch_loop()

    def _load_config(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=74)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_propagate(False)

        self.title_logo = ctk.CTkLabel(self.header, text="XNO", font=FONT_TITLE,
                                       text_color="#7fd4ff")
        self.title_logo.grid(row=0, column=0, sticky="w", padx=(26, 0), pady=10)
        self.title_rest = ctk.CTkLabel(self.header, text="  EXECUTOR", font=FONT_TITLE,
                                       text_color=FG_TEXT)
        self.title_rest.grid(row=0, column=0, sticky="w", padx=(90, 0), pady=10)

        self.status_badge = ctk.CTkLabel(self.header, text="\u25cf  NOT ATTACHED",
                                         font=("Segoe UI", 11, "bold"), text_color="#ff5c5c")
        self.status_badge.grid(row=0, column=1, sticky="e", padx=26, pady=10)

        self.nav = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=52)
        self.nav.grid(row=1, column=0, sticky="ew")
        self.nav.grid_propagate(False)
        self.nav.grid_columnconfigure(0, weight=1)
        self.nav_buttons = []
        for i, (name, idx) in enumerate(NAV_ITEMS):
            b = ctk.CTkButton(self.nav, text=name, font=FONT_NAV, corner_radius=10,
                              fg_color=BG_DARK, hover_color="#1b2740",
                              text_color=FG_TEXT, height=34, width=110,
                              command=lambda n=idx: self._show_tab(n))
            b.grid(row=0, column=1 + i, padx=(0, 8), pady=9)
            self.nav_buttons.append(b)

        self.content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.home_tab = self._build_home()
        self.hub_tab = self._build_hub()
        self.exec_tab = self._build_exec()
        self.settings_tab = self._build_settings()

        for t in (self.home_tab, self.hub_tab, self.exec_tab, self.settings_tab):
            t.grid(row=0, column=0, sticky="nsew")

        self._show_tab(2)

    def _tab_frame(self):
        return ctk.CTkFrame(self.content, fg_color=BG_DARK, corner_radius=0)

    def _build_home(self):
        f = self._tab_frame()
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=16, border_width=1,
                            border_color="#1d2b4d")
        hero.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        hero.grid_columnconfigure(0, weight=1)

        self.hero_title = ctk.CTkLabel(hero, text="XNO EXECUTOR", font=FONT_HERO)
        self.hero_title.grid(row=0, column=0, padx=24, pady=(18, 0))
        ctk.CTkLabel(hero, text="Keyless Roblox executor - attach, script, execute.",
                     font=FONT_SUB, text_color=FG_MUTED).grid(row=1, column=0,
                                                              padx=24, pady=(2, 18))

        cards = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=0)
        cards.grid(row=1, column=0, sticky="new", padx=28, pady=(0, 8))
        for c in range(3):
            cards.grid_columnconfigure(c, weight=1)

        self.home_state = self._status_card(cards, "STATE", "Not attached")
        self.home_state.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._status_card(cards, "TARGET", "Roblox").grid(row=0, column=1,
                                                          sticky="ew", padx=8)
        self._status_card(cards, "VERSION", "v1.0").grid(row=0, column=2,
                                                         sticky="ew", padx=(8, 0))

        actions = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=0)
        actions.grid(row=2, column=0, sticky="ew", padx=28, pady=(8, 24))
        ctk.CTkButton(actions, text="Open Execute", font=FONT_BTN, corner_radius=10,
                      fg_color="#1e3a8a", hover_color="#2748b8", height=42, width=180,
                      command=lambda: self._show_tab(2)).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkButton(actions, text="Open Script Hub", font=FONT_BTN, corner_radius=10,
                      fg_color="#1e3a8a", hover_color="#2748b8", height=42, width=180,
                      command=lambda: self._show_tab(1)).grid(row=0, column=1, padx=10)
        return f

    def _status_card(self, parent, key, value):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12, border_width=1,
                            border_color="#1d2b4d")
        ctk.CTkLabel(card, text=key, font=FONT_SMALL, text_color=FG_MUTED).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        ctk.CTkLabel(card, text=value, font=("Segoe UI", 15, "bold"),
                     text_color=FG_TEXT).grid(row=1, column=0, sticky="w",
                                              padx=14, pady=(0, 12))
        return card

    def _build_hub(self):
        f = self._tab_frame()
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(f, fg_color=BG_DARK, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="SCRIPT HUB", font=("Segoe UI", 18, "bold"),
                     text_color=FG_TEXT).grid(row=0, column=0, sticky="w")
        self.hub_search = ctk.CTkEntry(top, placeholder_text="Search scripts...",
                                       height=36, fg_color=BG_CARD, text_color=FG_TEXT,
                                       corner_radius=10)
        self.hub_search.grid(row=0, column=1, sticky="e", padx=10)
        self.hub_search.bind("<KeyRelease>", lambda e: self._refresh_hub())

        self.hub_list = ctk.CTkScrollableFrame(f, fg_color=BG_DARK, corner_radius=0)
        self.hub_list.grid(row=1, column=0, sticky="nsew", padx=24, pady=(4, 20))
        self.hub_list.grid_columnconfigure(0, weight=1)
        self._refresh_hub()
        return f

    def _hub_scripts(self):
        try:
            return sorted(n for n in os.listdir(SCRIPTS_DIR) if n.lower().endswith(".lua"))
        except Exception:
            return []

    def _refresh_hub(self):
        for w in self.hub_list.winfo_children():
            w.destroy()
        query = self.hub_search.get().strip().lower()
        for name in self._hub_scripts():
            if query and query not in name.lower():
                continue
            card = ctk.CTkFrame(self.hub_list, fg_color=BG_CARD, corner_radius=12,
                                border_width=1, border_color="#1d2b4d")
            card.grid(row=len(self.hub_list.winfo_children()), column=0,
                      sticky="ew", pady=4)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=name.replace(".lua", ""), font=FONT_BTN,
                         text_color=FG_TEXT).grid(row=0, column=0, sticky="w",
                                                  padx=14, pady=(10, 2))
            ctk.CTkLabel(card, text="Xno script", font=FONT_SMALL,
                         text_color=FG_MUTED).grid(row=1, column=0, sticky="w",
                                                   padx=14, pady=(0, 4))
            ctk.CTkButton(card, text="Load", font=FONT_BTN, width=76, height=30,
                          corner_radius=8, fg_color="#1e3a8a", hover_color="#2748b8",
                          command=lambda n=name: self._load_script(n)).grid(
                row=0, column=1, rowspan=2, padx=14, pady=8)

    def _load_script(self, name):
        try:
            with open(os.path.join(SCRIPTS_DIR, name), "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as exc:
            self._term_print(f"[Xno] Failed to load script: {exc}", "err")
            return
        self.editor.delete("0.0", "end")
        self.editor.insert("0.0", content)
        self._show_tab(2)
        self._term_print(f"[Xno] Loaded script: {name}", "accent")

    def _build_exec(self):
        f = self._tab_frame()
        f.grid_rowconfigure(1, weight=3)
        f.grid_rowconfigure(3, weight=1)
        f.grid_columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(f, fg_color=BG_PANEL, corner_radius=12, border_width=1,
                               border_color="#1d2b4d")
        toolbar.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        toolbar.grid_columnconfigure(4, weight=1)

        self.attach_btn = ctk.CTkButton(toolbar, text="  ATTACH  ",
                                        font=("Segoe UI", 13, "bold"), corner_radius=10,
                                        fg_color=BG_DARK, hover_color="#1b2740",
                                        text_color="#7fd4ff", height=38, width=130,
                                        border_width=2, border_color="#3b82f6",
                                        command=self._on_attach)
        self.attach_btn.grid(row=0, column=0, padx=(12, 6), pady=10)

        self.exec_btn = ctk.CTkButton(toolbar, text="EXECUTE",
                                      font=("Segoe UI", 13, "bold"), corner_radius=10,
                                      fg_color="#16a34a", hover_color="#1fb85a",
                                      text_color="#ffffff", height=38, width=120,
                                      command=self._on_execute)
        self.exec_btn.grid(row=0, column=1, padx=6, pady=10)

        self.stop_btn = ctk.CTkButton(toolbar, text="STOP",
                                      font=("Segoe UI", 13, "bold"), corner_radius=10,
                                      fg_color="#b91c1c", hover_color="#dc2626",
                                      text_color="#ffffff", height=38, width=100,
                                      command=self._on_stop)
        self.stop_btn.grid(row=0, column=2, padx=6, pady=10)

        ctk.CTkButton(toolbar, text="Clear", font=FONT_BTN, corner_radius=8,
                      fg_color="#1f2937", hover_color="#374151", height=34, width=84,
                      command=self._clear_editor).grid(row=0, column=3, padx=6, pady=10)

        self.attach_status = ctk.CTkLabel(toolbar, text="\u25cf Not attached",
                                          font=("Segoe UI", 11, "bold"),
                                          text_color="#ff5c5c")
        self.attach_status.grid(row=0, column=5, sticky="e", padx=12, pady=10)

        ctk.CTkLabel(f, text="SCRIPT EDITOR", font=FONT_SMALL,
                     text_color=FG_MUTED).grid(row=1, column=0, sticky="sw",
                                               padx=24, pady=(0, 2))
        self.editor = ctk.CTkTextbox(f, font=FONT_CODE, fg_color="#0a0f1c",
                                     text_color="#e6eefc", wrap="none", corner_radius=12,
                                     border_width=1, border_color="#1d2b4d")
        self.editor.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 8))
        self.editor.insert("1.0", "print('Hello from Xno Executor!')")

        ctk.CTkLabel(f, text="TERMINAL", font=FONT_SMALL,
                     text_color=FG_MUTED).grid(row=3, column=0, sticky="sw",
                                               padx=24, pady=(0, 2))
        self.term = ctk.CTkTextbox(f, font=FONT_TERM, fg_color="#05070d",
                                   text_color="#9db4d6", wrap="word", corner_radius=12,
                                   border_width=1, border_color="#1d2b4d",
                                   state="disabled")
        self.term.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))
        f.grid_rowconfigure(4, weight=1)
        self._term_tags()
        return f

    def _term_tags(self):
        tb = self.term._textbox
        tb.tag_configure("info", foreground="#9db4d6")
        tb.tag_configure("ok", foreground="#4ade80")
        tb.tag_configure("err", foreground="#ff5c5c")
        tb.tag_configure("accent", foreground="#7fd4ff")

    def _term_print(self, text, color=None):
        def do():
            tag = color if color in ("info", "ok", "err", "accent") else "info"
            tb = self.term._textbox
            tb.configure(state="normal")
            tb.insert("end", text + "\n", (tag,))
            if int(tb.index("end-1c").split(".")[0]) > 400:
                tb.delete("1.0", "200.0")
            tb.see("end")
            tb.configure(state="disabled")
        self.after(0, do)

    def _clear_editor(self):
        self.editor.delete("0.0", "end")

    def _build_settings(self):
        f = self._tab_frame()
        f.grid_rowconfigure(8, weight=1)
        f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f, text="SETTINGS", font=("Segoe UI", 18, "bold"),
                     text_color=FG_TEXT).grid(row=0, column=0, sticky="w",
                                              padx=28, pady=(20, 8))

        box = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=14, border_width=1,
                           border_color="#1d2b4d")
        box.grid(row=1, column=0, sticky="ew", padx=28, pady=6)
        box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(box, text="Executor DLL path", font=FONT_BODY,
                     text_color=FG_TEXT).grid(row=0, column=0, sticky="w",
                                              padx=14, pady=12)
        self.dll_entry = ctk.CTkEntry(box, font=("Segoe UI", 11), fg_color="#0a0f1c",
                                      text_color=FG_TEXT, height=34)
        self.dll_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=12)
        self.dll_entry.insert(0, self.config.get("dll_path", ""))
        ctk.CTkButton(box, text="Browse", font=FONT_BTN, width=88, height=32,
                      corner_radius=8, fg_color="#1e3a8a", hover_color="#2748b8",
                      command=self._browse_dll).grid(row=0, column=2, padx=14, pady=12)

        self.auto_attach = tk.BooleanVar(value=bool(self.config.get("auto_attach", True)))
        ctk.CTkSwitch(box, text="Auto-attach to Roblox when it starts", font=FONT_BODY,
                      variable=self.auto_attach, progress_color="#3b82f6",
                      button_color="#0a0f1c",
                      command=self._save_config).grid(row=1, column=0, columnspan=3,
                                                      sticky="w", padx=14, pady=8)

        ctk.CTkLabel(box, text="Rainbow speed", font=FONT_BODY,
                     text_color=FG_TEXT).grid(row=2, column=0, sticky="w",
                                              padx=14, pady=(8, 14))
        self.speed_var = tk.DoubleVar(value=float(self.config.get("rainbow_speed", 0.006)))
        self.speed_slider = ctk.CTkSlider(box, from_=0.001, to=0.02, number_of_steps=190,
                                          variable=self.speed_var, progress_color="#3b82f6",
                                          button_color="#7fd4ff")
        self.speed_slider.grid(row=2, column=1, sticky="ew", padx=6, pady=(8, 14))
        ctk.CTkLabel(box, text="", font=FONT_BODY, text_color=FG_MUTED).grid(
            row=2, column=2, padx=14, pady=(8, 14))

        ctk.CTkLabel(f, text="Keybinds:  F7 Attach   |   F8 Execute   |   F9 Stop",
                     font=FONT_BODY, text_color=FG_MUTED).grid(row=2, column=0,
                                                               sticky="w",
                                                               padx=28, pady=6)
        return f

    def _browse_dll(self):
        path = filedialog.askopenfilename(title="Select executor DLL",
                                          filetypes=[("DLL files", "*.dll")])
        if path:
            self.dll_entry.delete(0, "end")
            self.dll_entry.insert(0, path)
            self.engine.dll_path = path
            self.config["dll_path"] = path
            self._save_config()

    def _show_tab(self, idx):
        tabs = (self.home_tab, self.hub_tab, self.exec_tab, self.settings_tab)
        for i, t in enumerate(tabs):
            if i == idx:
                t.tkraise()
            else:
                t.lower()
        for i, b in enumerate(self.nav_buttons):
            active = i == idx
            b.configure(fg_color="#1b2740" if active else BG_DARK,
                        text_color="#7fd4ff" if active else FG_TEXT)

    def _bind_keys(self):
        self.bind_all("<F7>", lambda e: self._on_attach())
        self.bind_all("<F8>", lambda e: self._on_execute())
        self.bind_all("<F9>", lambda e: self._on_stop())

    def _on_attach(self):
        self.attach_btn.configure(state="disabled")
        self._term_print("[Xno] Scanning for Roblox...", "accent")
        self.after(60, self._finish_attach)

    def _finish_attach(self):
        self.attach_btn.configure(state="normal")
        ok, msg = self.engine.attach()
        self._term_print(f"[Xno] {msg}", "ok" if ok else "err")
        self._update_status()

    def _on_execute(self):
        script = self.editor.get("0.0", "end").strip()
        if not script:
            self._term_print("[Xno] Nothing to execute - editor is empty.", "err")
            return
        ok, msg = self.engine.execute(script)
        self._term_print(f"[Xno] {msg}", "ok" if ok else "err")

    def _on_stop(self):
        ok, msg = self.engine.stop()
        self._term_print(f"[Xno] {msg}", "ok" if ok else "err")

    def _update_status(self):
        st = self.engine.state
        if st == STATE_ATTACHED:
            txt, col = f"\u25cf Attached (PID {self.engine.pid})", "#4ade80"
        elif st == STATE_DETECTED:
            txt, col = "\u25cf Detected (simulation)", "#fbbf24"
        else:
            txt, col = "\u25cf Not attached", "#ff5c5c"
        self.status_badge.configure(text=txt.upper(), text_color=col)
        self.attach_status.configure(text=txt, text_color=col)
        self.home_state.winfo_children()[1].configure(text="Attached" if st else "Not attached")

    def _watch_loop(self):
        try:
            pid = self.engine.find_roblox()
            if pid is None and self.engine.state != STATE_DETACHED:
                if self.engine.state == STATE_ATTACHED:
                    self._term_print("[Xno] Roblox closed - detached.", "err")
                    self.engine.detach()
                    self._update_status()
            elif pid is not None and self.auto_attach.get():
                if self.engine.state == STATE_DETACHED:
                    self._term_print("[Xno] Roblox detected - attaching...", "accent")
                    ok, msg = self.engine.attach()
                    self._term_print(f"[Xno] {msg}", "ok" if ok else "err")
                    self._update_status()
        except Exception:
            pass
        self.after(2000, self._watch_loop)

    def _rainbow_loop(self):
        self.rainbow.tick()
        self.rainbow.step = self.speed_var.get()
        c = self.rainbow.color()
        d = self.rainbow.dark()
        self.header.configure(fg_color=d)
        self.title_logo.configure(text_color=c)
        self.hero_title.configure(text_color=c)
        self.attach_btn.configure(border_color=c, text_color=c)
        for b in self.nav_buttons:
            if b.cget("text_color") == "#7fd4ff":
                b.configure(fg_color=d)
        self.after(50, self._rainbow_loop)

    def _on_close(self):
        self.config["dll_path"] = self.dll_entry.get()
        self.config["auto_attach"] = self.auto_attach.get()
        self.config["rainbow_speed"] = self.speed_var.get()
        self._save_config()
        self.destroy()
