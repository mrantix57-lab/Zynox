# Xno Executor

Keyless Roblox executor GUI built with Python + CustomTkinter.

## Features

- **Tabs**: Home, Script Hub, Execute, Settings
- **Execute tab**: Attach / Execute / Stop / Clear buttons, script editor and a live terminal
- **Attach**: scans for `RobloxPlayerBeta.exe` (attaches to the game process)
- **Script Hub**: offline scripts, searchable, one-click load into the editor
- **Blue-rainbow theme**: smooth color cycle (speed adjustable in Settings)
- **Keybinds**: F7 Attach, F8 Execute, F9 Stop
- **Simulation mode**: works without a DLL so the GUI is testable; set a real executor DLL in Settings for actual in-game execution

## Run

```powershell
py -m pip install customtkinter
py D:\Zynox\XnoExecutor\main.py
```

## How execution works

1. `Attach` finds the Roblox process.
2. If an executor DLL is set in Settings, it is injected via `LoadLibrary` (CreateRemoteThread).
3. `Execute` writes the script to the `\\.\pipe\XnoExec` named pipe that the DLL must expose.
4. Without a DLL, the app runs in simulation mode (GUI + terminal only).
