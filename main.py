
from modules.cpu_scheduling import (
    fcfs_scheduling,
    sjf_scheduling,
    round_robin_scheduling,
    display_fcfs_result
)

# Common sample dataset
processes = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8},
    {"pid": "P4", "arrival_time": 3, "burst_time": 2}
]

# Run FCFS
fcfs_result = fcfs_scheduling(processes)
display_fcfs_result(fcfs_result)

# Run SJF
sjf_result = sjf_scheduling(processes)
display_fcfs_result(sjf_result)

# Run Round Robin with quantum = 2
rr_result = round_robin_scheduling(
    processes,
    time_quantum=2
)
display_fcfs_result(rr_result)

# Compare all three algorithms
print("\n========== CPU SCHEDULING COMPARISON ==========")

print(
    f"{'Algorithm':<25}"
    f"{'Avg Waiting':<18}"
    f"{'Avg Turnaround':<18}"
    f"{'CPU Utilization':<18}"
)

for result in [fcfs_result, sjf_result, rr_result]:
    print(
        f"{result['algorithm']:<25}"
        f"{result['average_waiting_time']:<18.2f}"
        f"{result['average_turnaround_time']:<18.2f}"
        f"{result['cpu_utilization']:<18.2f}"
    )
