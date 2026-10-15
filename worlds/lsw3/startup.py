
import json
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import psutil

# pyrefly: ignore [missing-import]
from worlds.LauncherComponents import launch
from worlds.lsw3.LSW3Client.client import run_client

CONFIG_DIR = Path.home() / "AppData" / "Roaming" / "Archipelago" / "LSW3"
CONFIG_FILE = CONFIG_DIR / "config.json"

STEPS = [
    (
        "Step 1 of 3",
        "Open LEGO Star Wars III in Dolphin.",
    ),
    (
        "Step 2 of 3",
        "Load or create a save file.\n\n"
        "Do not start the game.",
    ),
    (
        "Step 3 of 3",
        "Launching Archipelago client. \nConnect to the archipelago room, then start your game.",

    ),
]


def get_dolphin_path():
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                config = json.load(f)

            path = Path(config.get("dolphin_path", ""))
            if path.is_file():
                return path
        except (OSError, json.JSONDecodeError):
            pass

    root = tk.Tk()
    root.withdraw()

    selected = filedialog.askopenfilename(
        title="Select Dolphin Emulator",
        filetypes=[
            ("Dolphin Emulator", "Dolphin.exe"),
            ("Executable files", "*.exe"),
            ("All files", "*.*"),
        ],
        parent=root,
    )

    root.destroy()

    if not selected:
        return None

    path = Path(selected)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump({"dolphin_path": str(path)}, f, indent=4)

    return path


def dolphin_is_running():
    for process in psutil.process_iter(["name"]):
        try:
            name = process.info["name"]
            if name and name.lower() == "dolphin.exe":
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False


def main():
    dolphin_path = get_dolphin_path()
    if dolphin_path is None:
        return

    if not dolphin_is_running():
        subprocess.Popen([str(dolphin_path)])

    root = tk.Tk()
    root.title("LEGO Star Wars III — Startup")
    root.geometry("480x220")
    root.minsize(420, 200)

    step_index = 0

    heading = tk.Label(
        root,
        text="LEGO Star Wars III: The Clone Wars",
        font=("Segoe UI", 14, "bold"),
        wraplength=440,
    )
    heading.pack(pady=(20, 10))

    step_label = tk.Label(
        root,
        font=("Segoe UI", 10),
    )
    step_label.pack(pady=5)

    instruction = tk.Label(
        root,
        font=("Segoe UI", 11),
        wraplength=440,
        justify="center",
    )
    instruction.pack(pady=10, expand=True)

    def update_step():
        title, text = STEPS[step_index]
        step_label.config(text=title)
        instruction.config(text=text)

        if step_index == len(STEPS) - 1:
            next_button.config(text="Launch Client")
        else:
            next_button.config(text="Next")

    def advance():
        nonlocal step_index

        if step_index < len(STEPS) - 1:
            step_index += 1
            update_step()
            return

        root.destroy()
        launch(
            run_client,
            name="LEGO Star Wars III: The Clone Wars Client",
        )

    next_button = tk.Button(
        root,
        text="Next",
        command=advance,
        width=18,
    )
    next_button.pack(pady=(0, 20))

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    update_step()
    root.mainloop()


if __name__ == "__main__":
    main()
