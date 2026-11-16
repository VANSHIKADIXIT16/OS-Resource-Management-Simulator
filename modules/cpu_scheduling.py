from collections import deque


def _validate_processes(processes):
    """Validate CPU process records shared by all scheduling algorithms."""
    if not isinstance(processes, (list, tuple)) or not processes:
        raise ValueError("Process list cannot be empty.")

    required_fields = {"pid", "arrival_time", "burst_time"}
    seen_pids = set()

    for process in processes:
        if not isinstance(process, dict) or not required_fields.issubset(process):
            raise ValueError(
                "Each process needs pid, arrival_time and burst_time."
            )

        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]
        if not isinstance(pid, str) or not pid.strip():
            raise ValueError("Process ID must be a non-empty string.")
        if pid in seen_pids:
            raise ValueError("Process IDs must be unique.")
        seen_pids.add(pid)

        if (
            not isinstance(arrival, int)
            or isinstance(arrival, bool)
            or arrival < 0
        ):
            raise ValueError("Arrival time must be a non-negative integer.")
        if (
            not isinstance(burst, int)
            or isinstance(burst, bool)
            or burst <= 0
        ):
            raise ValueError("Burst time must be a positive integer.")


def fcfs_scheduling(processes):
    """
    First Come First Serve CPU Scheduling.

    Each process must contain:
    pid, arrival_time, burst_time
    """

    _validate_processes(processes)

    # Sort processes by arrival time.
    # Original order is preserved for equal arrival times.
    ordered_processes = sorted(
        processes,
        key=lambda p: p["arrival_time"]
    )

    current_time = 0
    results = []
    gantt_chart = []

    for process in ordered_processes:
        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

        # Handle CPU idle time.
        if current_time < arrival:
            gantt_chart.append({
                "pid": "IDLE",
                "start": current_time,
                "end": arrival
            })
            current_time = arrival

        start_time = current_time
        completion_time = start_time + burst

        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst

        results.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "start_time": start_time,
            "completion_time": completion_time,
            "turnaround_time": turnaround_time,
            "waiting_time": waiting_time
        })

        gantt_chart.append({
            "pid": pid,
            "start": start_time,
            "end": completion_time
        })

        current_time = completion_time

    process_count = len(results)

    average_waiting_time = (
        sum(p["waiting_time"] for p in results) / process_count
    )

    average_turnaround_time = (
        sum(p["turnaround_time"] for p in results) / process_count
    )

    total_busy_time = sum(p["burst_time"] for p in results)
    total_elapsed_time = current_time - gantt_chart[0]["start"]

    cpu_utilization = (
        total_busy_time / total_elapsed_time * 100
        if total_elapsed_time > 0 else 0
    )

    return {
        "algorithm": "FCFS",
        "results": results,
        "gantt_chart": gantt_chart,
        "average_waiting_time": average_waiting_time,
        "average_turnaround_time": average_turnaround_time,
        "cpu_utilization": cpu_utilization
    }


def display_fcfs_result(result):
    """Display FCFS scheduling results."""

    print(f"\n========== {result['algorithm']} ==========")

    print("\nProcess Execution Table")
    print("-" * 80)

    print(
        f"{'PID':<10}{'Arrival':<10}{'Burst':<10}"
        f"{'Completion':<12}{'Waiting':<10}{'Turnaround':<12}"
    )

    for p in result["results"]:
        print(
            f"{p['pid']:<10}"
            f"{p['arrival_time']:<10}"
            f"{p['burst_time']:<10}"
            f"{p['completion_time']:<12}"
            f"{p['waiting_time']:<10}"
            f"{p['turnaround_time']:<12}"
        )

    print("\nGantt Chart")

    for item in result["gantt_chart"]:
        print(
            f"| {item['pid']} "
            f"({item['start']}-{item['end']}) ",
            end=""
        )

    print("|")

    print("\nAverage Waiting Time:",
          round(result["average_waiting_time"], 2))

    print("Average Turnaround Time:",
          round(result["average_turnaround_time"], 2))

    print("CPU Utilization:",
          round(result["cpu_utilization"], 2), "%")

# SJF ALGORITHM


def sjf_scheduling(processes):
    """
    Non-preemptive Shortest Job First CPU Scheduling.
    Selects the shortest available process.
    """

    _validate_processes(processes)

    # Keep original order as a tie-breaker.
    remaining = [
        (index, process)
        for index, process in enumerate(processes)
    ]

    current_time = 0
    results = []
    gantt_chart = []

    while remaining:

        # Find processes that have already arrived.
        available = [
            item for item in remaining
            if item[1]["arrival_time"] <= current_time
        ]

        # If no process is available, move to next arrival.
        if not available:
            next_arrival = min(
                item[1]["arrival_time"] for item in remaining
            )

            gantt_chart.append({
                "pid": "IDLE",
                "start": current_time,
                "end": next_arrival
            })

            current_time = next_arrival
            continue

        # Select shortest burst time.
        selected = min(
            available,
            key=lambda item: (
                item[1]["burst_time"],
                item[1]["arrival_time"],
                item[0]
            )
        )

        _, process = selected

        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

        start_time = current_time
        completion_time = start_time + burst

        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst

        results.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "start_time": start_time,
            "completion_time": completion_time,
            "turnaround_time": turnaround_time,
            "waiting_time": waiting_time
        })

        gantt_chart.append({
            "pid": pid,
            "start": start_time,
            "end": completion_time
        })

        current_time = completion_time

        # Remove completed process.
        remaining.remove(selected)

    process_count = len(results)

    average_waiting_time = (
        sum(p["waiting_time"] for p in results) / process_count
    )

    average_turnaround_time = (
        sum(p["turnaround_time"] for p in results) / process_count
    )

    total_busy_time = sum(p["burst_time"] for p in results)
    total_elapsed_time = current_time - gantt_chart[0]["start"]

    cpu_utilization = (
        total_busy_time / total_elapsed_time * 100
        if total_elapsed_time > 0 else 0
    )

    return {
        "algorithm": "SJF (Non-preemptive)",
        "results": results,
        "gantt_chart": gantt_chart,
        "average_waiting_time": average_waiting_time,
        "average_turnaround_time": average_turnaround_time,
        "cpu_utilization": cpu_utilization
    }


#round robin scheduling


def round_robin_scheduling(processes, time_quantum):
    """
    Preemptive Round Robin CPU Scheduling.
    Processes execute for a fixed time quantum.
    """

    _validate_processes(processes)

    if not isinstance(time_quantum, int) or isinstance(time_quantum, bool) or time_quantum <= 0:
        raise ValueError("Time quantum must be a positive integer.")

    # Sort processes by arrival time.
    ordered = sorted(
        enumerate(processes),
        key=lambda item: (item[1]["arrival_time"], item[0])
    )

    remaining = {
        process["pid"]: process["burst_time"]
        for process in processes
    }

    ready_queue = deque()
    current_time = 0
    next_process = 0

    gantt_chart = []
    completion_times = {}
    first_start_times = {}

    while next_process < len(ordered) or ready_queue:

        # Add newly arrived processes.
        while (
            next_process < len(ordered)
            and ordered[next_process][1]["arrival_time"] <= current_time
        ):
            ready_queue.append(ordered[next_process][1]["pid"])
            next_process += 1

        # If queue is empty, CPU remains idle.
        if not ready_queue:
            next_arrival = ordered[next_process][1]["arrival_time"]

            gantt_chart.append({
                "pid": "IDLE",
                "start": current_time,
                "end": next_arrival
            })

            current_time = next_arrival
            continue

        pid = ready_queue.popleft()

        if pid not in first_start_times:
            first_start_times[pid] = current_time

        execution_time = min(
            time_quantum,
            remaining[pid]
        )

        start_time = current_time
        current_time += execution_time

        remaining[pid] -= execution_time

        gantt_chart.append({
            "pid": pid,
            "start": start_time,
            "end": current_time
        })

        # Add processes that arrived during this time slice.
        while (
            next_process < len(ordered)
            and ordered[next_process][1]["arrival_time"] <= current_time
        ):
            ready_queue.append(ordered[next_process][1]["pid"])
            next_process += 1

        # Reinsert unfinished process at the end.
        if remaining[pid] > 0:
            ready_queue.append(pid)
        else:
            completion_times[pid] = current_time

    # Calculate individual process metrics.
    results = []

    for process in processes:
        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

        completion = completion_times[pid]
        turnaround = completion - arrival
        waiting = turnaround - burst

        results.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "start_time": first_start_times[pid],
            "completion_time": completion,
            "turnaround_time": turnaround,
            "waiting_time": waiting
        })

    count = len(results)

    average_waiting_time = (
        sum(p["waiting_time"] for p in results) / count
    )

    average_turnaround_time = (
        sum(p["turnaround_time"] for p in results) / count
    )

    total_busy_time = sum(p["burst_time"] for p in results)

    total_elapsed_time = (
        current_time - gantt_chart[0]["start"]
    )

    cpu_utilization = (
        total_busy_time / total_elapsed_time * 100
        if total_elapsed_time > 0 else 0
    )

    return {
        "algorithm": "Round Robin",
        "time_quantum": time_quantum,
        "results": results,
        "gantt_chart": gantt_chart,
        "average_waiting_time": average_waiting_time,
        "average_turnaround_time": average_turnaround_time,
        "cpu_utilization": cpu_utilization
    }
