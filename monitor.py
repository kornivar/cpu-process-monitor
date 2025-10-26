import os
import psutil
import time
from pathlib import Path
from datetime import datetime

class My_Processes:
    def __init__(self, pid, name, cpu_use):
        self.__pid = pid
        self.__name = name
        self.__cpu_use = cpu_use

    @property
    def pid(self):
        return self.__pid

    @property
    def name(self):
        return self.__name

    @property
    def cpu_use(self):
        return self.__cpu_use

EXCLUDED_PROCESSES = (
    # System processes
    "System Idle Process",  # Windows idle process
    "System",               # Windows kernel process
    "explorer.exe",         # Windows shell
    "svchost.exe",          # Windows service host
    "winlogon.exe",         # Windows login process
    "taskhostw.exe",        # Windows task host
    "Registry",             # Windows registry process
    
    # Popular applications
    "chrome.exe",           # Browser
    "firefox.exe",          # Browser
    "edge.exe",             # Browser
    "Teams.exe",            # Communication tool
    "python.exe",           # To avoid logging the monitor itself
    "devenv.exe",           # Visual Studio
    "node.exe",             # Node.js runtime
    "Microsoft.ServiceHub.Controller.exe"  # VS background service
)

def ensure_logs_folder():
    folder_path = Path(__file__).parent / "logs"
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

def log_below_limit(progs, lower_limit=3):
    now = datetime.now()
    folder_path = ensure_logs_folder()

    filename = datetime.now().strftime("%Y-%m-%d") + ".txt"
    file_path = folder_path / filename
    file_path.touch(exist_ok=True)
    current_pid = os.getpid()

    with open(file_path, 'a', encoding='utf-8') as f:
        for proc in progs:
            if 0 < proc.cpu_use < lower_limit:
                try:
                    if proc.pid == current_pid:
                        continue
                    elif proc.name in EXCLUDED_PROCESSES:
                        continue

                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    f.write(f"{now_str} | {proc.name} (PID {proc.pid}) CPU use: {proc.cpu_use:.1f}% < {lower_limit}%\n")
                    print(f"Logged {proc.name} (PID {proc.pid}) using {proc.cpu_use}% < {lower_limit}%")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"Could not access {proc.name} (PID {proc.pid})")
        f.write("-" * 60 + "\n")

def build_processes_snapshot():
    processes = {p.info['pid']: p for p in psutil.process_iter(['pid', 'name'])}
    for p in processes.values():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def main():
    print("Process monitor starting...")
    print("Choose a mode:")
    print("  l - log processes with CPU usage below 3% (single pass)")
    print("  d - start spike diagnostic (continuous, 10 seconds)")
    print("  q - quit")

    while True:
        choice = input("Enter (l/d/q): ").strip().lower()
        if choice == 'q':
            print("Exiting...")
            break
        elif choice == 'l':
            processes = build_processes_snapshot()

            time.sleep(1.5)

            progs = []
            for pid, p in processes.items():
                try:
                    cpu = p.cpu_percent(interval=None)
                    progs.append(My_Processes(pid, p.info['name'], cpu))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            progs.sort(key=lambda x: x.cpu_use)
            log_below_limit(progs)
            print("Logging complete!")

        elif choice == 'd':
            print("This feature is not available yet.")
            pass

        else: 
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()

