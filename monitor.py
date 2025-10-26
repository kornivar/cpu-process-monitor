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

def monitor_for_spikes(processes_dict, progs_baseline, duration=10, sample_interval=1, spike_delta=15, spike_absolute=25):

    samples = max(1, int(duration / sample_interval))
    current_pid = os.getpid()
    spikes = {} 

    baseline_map = {p.pid: p.cpu_use for p in progs_baseline}

    start_time = datetime.now()
    folder_path = ensure_logs_folder()
    filename = "spikes-" + start_time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    file_path = folder_path / filename
    file_path.touch(exist_ok=True)

    for _ in range(samples):
        time.sleep(sample_interval)
        for pid, p in list(processes_dict.items()):
            try:
                cur = p.cpu_percent(interval=None)
                base = baseline_map.get(pid, cur)

                if isinstance(p, psutil.Process):
                    name = p.info.get('name')
                else:
                    try:
                        name = p.name
                    except AttributeError:
                        name = str(pid)

                if name in EXCLUDED_PROCESSES or pid == current_pid:
                    continue

                delta = cur - base
                is_spike = False
                if delta >= spike_delta:
                    is_spike = True
                elif base < spike_absolute <= cur:
                    is_spike = True

                if is_spike:
                    rec = spikes.get(pid)
                    if not rec:
                        spikes[pid] = {'name': name, 'baseline': base, 'peak': cur}
                    else:
                        if cur > rec['peak']:
                            rec['peak'] = cur
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    results = []
    for pid, info in spikes.items():
        results.append((info['name'], pid, info['baseline'], info['peak']))

    if results:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("-"*30 + f" Start of monitoring window ({start_time.strftime('%Y-%m-%d %H:%M:%S')}) " + "-"*30 + "\n")
            for name, pid, baseline, peak in results:
                f.write(f"{name} (PID {pid}) baseline: {baseline:.1f}% -> spike: {peak:.1f}%\n")
            f.write("-"*30 + f" End of monitoring window " + "-"*54 + "\n")

    return results

def main():
    print("Process monitor starting...")
    print("Choose a mode:")
    print("  l - log processes with CPU usage below 3% (single pass)")
    print("  d - start spike diagnostic (continuous, 10-second window)")
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
            print("Spike diagnostics started (Ctrl+C to stop).")
            window_seconds = 10

            try:
                while True:
                    processes = build_processes_snapshot()
                    time.sleep(1.0)

                    progs = []
                    for pid, p in processes.items():
                        try:
                            cpu = p.cpu_percent(interval=None)
                            progs.append(My_Processes(pid, p.info['name'], cpu))
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass

                    progs.sort(key=lambda x: x.cpu_use)

                    spikes = monitor_for_spikes(processes, progs_baseline=progs, duration=window_seconds)

                    print(f"\n{window_seconds}-second monitoring window ended.")
                    if spikes:
                        print(f"Detected {len(spikes)} spike(s) in the last {window_seconds} seconds:")
                        for name, pid, baseline, peak in spikes:
                            print(f" - {name} (PID {pid}) baseline {baseline:.1f}% -> peak {peak:.1f}%")
                    else:
                        print("No spikes detected in this window.")

                    print("Results were logged. Waiting before next window...\n")
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\nDiagnostics stopped by user. Returning to menu.")

        else: 
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()

