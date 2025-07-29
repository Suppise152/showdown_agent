import subprocess
import time
import os
import signal
import sys

# === New Virtual Environment Path ===
VENV_PYTHON = r"C:\Users\Timca\venv\pokemon\Scripts\python.exe"
SHOWDOWN_DIR = r"C:\Users\Timca\OneDrive\Documents\GitHub\showdown_agent\compsys726\pokemon-showdown"
AGENT_SCRIPT_DIR = r"C:\Users\Timca\OneDrive\Documents\GitHub\showdown_agent\compsys726\showdown_agent\showdown_agent\scripts"
AGENT_SCRIPT = "expert_main.py"

# === Validate All Paths ===
if not os.path.exists(VENV_PYTHON):
    print(f"[ERROR] Python executable not found: {VENV_PYTHON}")
    sys.exit(1)
if not os.path.exists(os.path.join(AGENT_SCRIPT_DIR, AGENT_SCRIPT)):
    print(
        f"[ERROR] Agent script not found: {os.path.join(AGENT_SCRIPT_DIR, AGENT_SCRIPT)}"
    )
    sys.exit(1)

# === Start Pokémon Showdown server ===
print("[INFO] Starting Pokémon Showdown server...")
showdown_process = subprocess.Popen(
    ["node", "pokemon-showdown", "start", "--no-security"],
    cwd=SHOWDOWN_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
)

# === Give the server time to start ===
time.sleep(5)

# === Run your agent script ===
print("[INFO] Running your agent script...")
try:
    subprocess.run([VENV_PYTHON, AGENT_SCRIPT], cwd=AGENT_SCRIPT_DIR, check=True)
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Agent script failed with exit code {e.returncode}")
    showdown_process.send_signal(signal.CTRL_BREAK_EVENT)
    showdown_process.wait()
    sys.exit(1)

# === Stop Pokémon Showdown server ===
print("[INFO] Stopping Pokémon Showdown server...")
showdown_process.send_signal(signal.CTRL_BREAK_EVENT)
showdown_process.wait()
print("[INFO] All done.")
