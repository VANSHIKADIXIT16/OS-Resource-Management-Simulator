
from modules.cpu_scheduling import (
    fcfs_scheduling,
    display_fcfs_result
)

processes = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8},
    {"pid": "P4", "arrival_time": 3, "burst_time": 2}
]

result = fcfs_scheduling(processes)

display_fcfs_result(result)

