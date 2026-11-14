
def fcfs_scheduling(processes):
    """
    First Come First Serve CPU Scheduling.

    Each process must contain:
    pid, arrival_time, burst_time
    """

    if not processes:
        raise ValueError("Process list cannot be empty.")

    for process in processes:
        if process["arrival_time"] < 0:
            raise ValueError("Arrival time cannot be negative.")

        if process["burst_time"] <= 0:
            raise ValueError("Burst time must be greater than zero.")

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

    print("\n========== FCFS SCHEDULING ==========")

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
