import ctypes
import csv
import io
import os
import subprocess
from ctypes import wintypes

ROBLOX_PROCESS = "RobloxPlayerBeta.exe"
ALTERNATE_PROCESSES = ["RobloxStudioBeta.exe", "Player"]

PAGE_READWRITE = 0x04
MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_CREATE_THREAD = 0x0002
PROCESS_QUERY_INFORMATION = 0x0400

GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3

STATE_DETACHED = 0
STATE_DETECTED = 1
STATE_ATTACHED = 2

PIPE_PATH = r"\\.\pipe\XnoExec"


class XnoEngine:
    def __init__(self, log=None):
        self.log = log or print
        self.state = STATE_DETACHED
        self.pid = None
        self.dll_path = ""
        self.injected = False

    def find_roblox(self):
        try:
            out = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {ROBLOX_PROCESS}",
                 "/FO", "CSV", "/NH"],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
            )
            rows = list(csv.reader(io.StringIO(out.stdout)))
            for row in rows:
                if row and row[0].strip().lower() == ROBLOX_PROCESS.lower():
                    try:
                        return int(row[1].strip())
                    except ValueError:
                        continue
        except Exception:
            pass
        return None

    def attach(self):
        self.pid = self.find_roblox()
        if self.pid is None:
            self.state = STATE_DETACHED
            return False, "Roblox is not running. Start Roblox, join a game, then press Attach."

        if self.dll_path and os.path.isfile(self.dll_path):
            try:
                self._inject_dll(self.pid, self.dll_path)
                self.injected = True
                self.state = STATE_ATTACHED
                return True, f"Attached to Roblox (PID {self.pid}) via {os.path.basename(self.dll_path)}. In-game execution ready."
            except Exception as exc:
                self.state = STATE_DETECTED
                return False, f"Injection failed: {exc}. Running in simulation mode."
        else:
            self.state = STATE_DETECTED
            return True, f"Roblox detected (PID {self.pid}). No executor DLL set \u2014 running in simulation mode. Set the DLL path in Settings for real execution."

    def detach(self):
        self.injected = False
        self.state = STATE_DETACHED
        self.pid = None

    def execute(self, script):
        if not script.strip():
            return False, "Nothing to execute."
        if self.state == STATE_DETACHED:
            return False, "Not attached to Roblox. Press Attach first."
        if self.state == STATE_DETECTED:
            return False, "Simulation mode \u2014 no executor DLL loaded. Set the DLL path in Settings."
        ok, msg = self._write_pipe(script.encode("utf-8"))
        return ok, msg

    def stop(self):
        if self.state == STATE_DETACHED:
            return False, "Not attached to Roblox."
        if self.state == STATE_DETECTED:
            return True, "Stopped (simulation mode)."
        ok, msg = self._write_pipe(b"\x01STOP")
        return ok, msg

    def _write_pipe(self, payload):
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateFileW(
            PIPE_PATH, GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)
        if handle in (0, None, -1, ctypes.c_void_p(-1).value):
            return False, "Executor DLL is not responding (pipe closed). Re-attach or restart Roblox."
        try:
            buf = ctypes.create_string_buffer(payload + b"\x00")
            written = ctypes.c_ulong(0)
            ok = kernel32.WriteFile(handle, buf, len(buf), ctypes.byref(written), None)
            if not ok:
                return False, f"Write failed ({ctypes.get_last_error()})."
            return True, "Executed in Roblox."
        finally:
            kernel32.CloseHandle(handle)

    def _inject_dll(self, pid, dll_path):
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        access = (PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ |
                  PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION)
        handle = kernel32.OpenProcess(access, False, pid)
        if not handle:
            raise OSError(f"OpenProcess failed ({ctypes.get_last_error()})")
        try:
            path_buf = ctypes.create_unicode_buffer(os.path.abspath(dll_path), 512)
            size = (len(os.path.abspath(dll_path)) + 1) * 2
            remote = kernel32.VirtualAllocEx(handle, None, size, MEM_COMMIT, PAGE_READWRITE)
            if not remote:
                raise OSError(f"VirtualAllocEx failed ({ctypes.get_last_error()})")
            if not kernel32.WriteProcessMemory(handle, remote, path_buf, size, None):
                raise OSError(f"WriteProcessMemory failed ({ctypes.get_last_error()})")

            kernel32.GetModuleHandleW.restype = wintypes.HMODULE
            kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
            kernel32.GetProcAddress.restype = ctypes.c_void_p
            kernel32.GetProcAddress.argtypes = [wintypes.HMODULE, ctypes.c_char_p]
            k32 = kernel32.GetModuleHandleW("kernel32.dll")
            load_lib = ctypes.c_void_p(kernel32.GetProcAddress(k32, b"LoadLibraryW"))
            if not load_lib.value:
                raise OSError("LoadLibraryW address not found.")

            thread_id = ctypes.c_ulong(0)
            thread = kernel32.CreateRemoteThread(handle, None, 0, load_lib, remote, 0, ctypes.byref(thread_id))
            if not thread:
                kernel32.VirtualFreeEx(handle, remote, 0, MEM_RELEASE)
                raise OSError(f"CreateRemoteThread failed ({ctypes.get_last_error()})")
            kernel32.WaitForSingleObject(thread, 5000)
            kernel32.CloseHandle(thread)
        finally:
            kernel32.CloseHandle(handle)
