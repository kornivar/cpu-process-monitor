# cpu-process-monitor
A Python tool for monitoring system processes based on CPU usage.  
It logs processes with low CPU usage, ignoring system and popular applications  (e.g., Chrome, Teams, Python). It also has the ability to log spikes in CPU load.
Logs are stored in the “logs” folder.

1. Clone the repository:
git clone https://github.com/kornivar/cpu-process-monitor.git
cd cpu-process-monitor

2. Install dependencies:
pip install psutil

Usage
Run the monitor script:
python monitor.py

Configuration
You can adjust the CPU threshold by modifying the lower_limit argument in the log_below_limit function:
log_below_limit(progs, lower_limit=5) # logs processes using less than 5% CPU

You can also add to or reduce the list of ignored processes yourself by changing EXCLUDED_PROCESSES.

After launching the program, you can choose one of two options. 
First: the program logs processes with CPU load below the specified threshold (3% by default) and adds them to a text file in the log folder.
Second: the program launches a “monitoring window” (lasting 10 seconds) during which it attempts to detect processes with spikes in CPU load and adds them to a text file named “spikes” in the log folder.

