# cpu-process-monitor
A Python tool to monitor system processes based on CPU usage.  
Currently, it logs processes with low CPU usage, ignoring system and popular applications  (e.g., Chrome, Teams, Python). 
The logs are stored in the “logs” folder in a file with the date of logging. 
Future updates will include monitoring processes with sudden spikes in CPU usage.

1. Clone the repository:
git clone https://github.com/kornivar/cpu-process-monitor.git
cd cpu-process-monitor

2. Install dependencies:
pip install psutil

Usage
Run the monitor script:
python monitor.py

The program will:
1. Continuously monitor running processes
2. Log processes below the CPU threshold
3. Skip system or predefined popular processes
4. Save logs in the logs folder

Configuration
You can adjust the CPU threshold by modifying the lower_limit argument in the log_below_limit function:
log_below_limit(progs, lower_limit=5) # logs processes using less than 5% CPU

You can also add to or reduce the list of ignored processes yourself by changing EXCLUDED_PROCESSES.

Logs
After the start of the program, every 7 seconds, processes with a CPU load below the specified threshold (3% by default) will be added to a text file in the logs folder.
Each log entry includes: process name, PID, and CPU usage
Example log snippet:
example_process.exe cpu use: 2.1%
another_process.exe cpu use: 0.5%
----------------------------------------

Future Plans
Detect and log processes with sudden spikes in CPU usage
