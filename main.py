"""Menu-driven entry point for the OS resource management simulator."""

import json
import logging
from pathlib import Path

from analysis.performance import generate_reports
from modules.activity_log import configure_activity_logger
from modules.cpu_scheduling import (
    fcfs_scheduling,
    round_robin_scheduling,
    sjf_scheduling,
)
from modules.deadlock import bankers_algorithm
from modules.disk_scheduling import (
    fcfs_disk_scheduling,
    scan_disk_scheduling,
    sstf_disk_scheduling,
)
from modules.memory_management import memory_allocation

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_FILES = {
    "cpu": PROJECT_ROOT / "data" / "cpu_processes.json",
    "memory": PROJECT_ROOT / "data" / "memory_allocation.json",
    "deadlock": PROJECT_ROOT / "data" / "deadlock.json",
    "disk": PROJECT_ROOT / "data" / "disk_requests.json",
}


def configure_logging() -> logging.Logger:
    """Configure one file logger for application operations and outcomes."""
    return configure_activity_logger(PROJECT_ROOT)


def load_sample(name):
    """Load one of the bundled JSON samples by its fixed logical name."""
    if name not in SAMPLE_FILES:
        raise ValueError(f"Unknown sample dataset: {name}")
    with SAMPLE_FILES[name].open(encoding="utf-8") as sample_file:
        return json.load(sample_file)


def _read_integer(prompt):
    value = input(prompt).strip()
    try:
        return int(value)
    except ValueError as error:
        raise ValueError("Enter a whole number.") from error


def _read_choice(prompt, valid_choices):
    choice = input(prompt).strip()
    if choice not in valid_choices:
        logging.getLogger("simulator").warning("Invalid menu choice")
        print("Invalid choice. Please try again.")
        return None
    return choice


def _show_cpu_result(result):
    print(f"\n{result['algorithm']}")
    print("PID  Arrival  Burst  Start  Complete  Waiting  Turnaround")
    for process in result["results"]:
        print(
            f"{process['pid']:<4} {process['arrival_time']:<7} "
            f"{process['burst_time']:<6} {process['start_time']:<6} "
            f"{process['completion_time']:<9} "
            f"{process['waiting_time']:<8} {process['turnaround_time']}"
        )
    timeline = " | ".join(
        f"{item['pid']} [{item['start']}-{item['end']}]"
        for item in result["gantt_chart"]
    )
    print(f"Gantt timeline: {timeline}")
    print(f"Average waiting time: {result['average_waiting_time']:.2f}")
    print(f"Average turnaround time: {result['average_turnaround_time']:.2f}")
    print(f"CPU utilization: {result['cpu_utilization']:.2f}%")


def _show_memory_result(result):
    print(f"\n{result['algorithm']}")
    print("PID  Requested  Partition  Internal fragmentation  Status")
    for process in result["results"]:
        print(
            f"{process['pid']:<4} {process['required_memory']:<10} "
            f"{process['block'] or '-':<10} "
            f"{process['fragmentation']:<23} {process['status']}"
        )
    print(
        f"Allocated: {result['successful_allocations']}; "
        f"failed: {result['failed_allocations']}"
    )
    print(
        "Internal fragmentation: "
        f"{result['total_internal_fragmentation']} KB; "
        f"free partitions: {result['remaining_free_memory']} KB"
    )
    print(f"Occupied-partition utilization: {result['memory_utilization']:.2f}%")
    print(
        "Requested-memory utilization: "
        f"{result['requested_memory_utilization']:.2f}%"
    )


def _show_deadlock_result(result):
    print(f"\nSystem state: {result['status']}")
    print(f"Need matrix: {result['need']}")
    if result["is_safe"]:
        print(f"Safe sequence: {' -> '.join(result['safe_sequence'])}")
    else:
        print("No safe sequence exists for the current allocation.")


def _show_disk_result(result):
    print(f"\n{result['algorithm']}")
    print(f"Service order: {result['service_order']}")
    print(f"Movement path: {result['movement_path']}")
    print(f"Total head movement: {result['total_head_movement']} tracks")
    print(
        f"Average movement per request: "
        f"{result['average_head_movement']:.2f} tracks"
    )


def _run_cpu():
    choice = _read_choice(
        "\nCPU: 1 FCFS, 2 SJF, 3 Round Robin, 4 compare all, 0 Back: ",
        {"0", "1", "2", "3", "4"},
    )
    if choice in (None, "0"):
        return
    processes = load_sample("cpu")
    algorithms = {
        "1": lambda: [fcfs_scheduling(processes)],
        "2": lambda: [sjf_scheduling(processes)],
        "3": lambda: [
            round_robin_scheduling(
                processes, _read_integer("Time quantum (positive integer): ")
            )
        ],
        "4": lambda: [
            fcfs_scheduling(processes),
            sjf_scheduling(processes),
            round_robin_scheduling(processes, 2),
        ],
    }
    results = algorithms[choice]()
    for result in results:
        _show_cpu_result(result)
        logging.getLogger("simulator").info(
            "CPU result %s: average waiting %.2f, average turnaround %.2f, "
            "utilization %.2f%%",
            result["algorithm"],
            result["average_waiting_time"],
            result["average_turnaround_time"],
            result["cpu_utilization"],
        )


def _run_memory():
    choice = _read_choice(
        "\nMemory: 1 First Fit, 2 Best Fit, 3 Worst Fit, "
        "4 compare all, 0 Back: ",
        {"0", "1", "2", "3", "4"},
    )
    if choice in (None, "0"):
        return
    sample = load_sample("memory")
    names = {
        "1": ["First Fit"],
        "2": ["Best Fit"],
        "3": ["Worst Fit"],
        "4": ["First Fit", "Best Fit", "Worst Fit"],
    }[choice]
    results = [
        memory_allocation(sample["blocks"], sample["processes"], name)
        for name in names
    ]
    for result in results:
        _show_memory_result(result)
        logging.getLogger("simulator").info(
            "Memory result %s: %d allocated, %d failed, %d KB internal "
            "fragmentation, %d KB free",
            result["algorithm"],
            result["successful_allocations"],
            result["failed_allocations"],
            result["total_internal_fragmentation"],
            result["remaining_free_memory"],
        )


def _run_deadlock():
    sample = load_sample("deadlock")
    result = bankers_algorithm(
        sample["allocation"], sample["max"], sample["available"]
    )
    _show_deadlock_result(result)
    logging.getLogger("simulator").info(
        "Deadlock safety check completed: %s; safe sequence %s",
        result["status"],
        result["safe_sequence"],
    )


def _run_disk():
    choice = _read_choice(
        "\nDisk: 1 FCFS, 2 SSTF, 3 SCAN, 4 compare all, 0 Back: ",
        {"0", "1", "2", "3", "4"},
    )
    if choice in (None, "0"):
        return
    sample = load_sample("disk")
    requests = sample["requests"]
    head = sample["initial_head"]
    size = sample["disk_size"]
    direction = sample["direction"]
    algorithms = {
        "1": lambda: [fcfs_disk_scheduling(requests, head, size)],
        "2": lambda: [sstf_disk_scheduling(requests, head, size)],
        "3": lambda: [
            scan_disk_scheduling(requests, head, size, direction)
        ],
        "4": lambda: [
            fcfs_disk_scheduling(requests, head, size),
            sstf_disk_scheduling(requests, head, size),
            scan_disk_scheduling(requests, head, size, direction),
        ],
    }
    results = algorithms[choice]()
    for result in results:
        _show_disk_result(result)
        logging.getLogger("simulator").info(
            "Disk result %s: %d tracks total, %.2f tracks/request",
            result["algorithm"],
            result["total_head_movement"],
            result["average_head_movement"],
        )


def _run_analysis():
    generated = generate_reports()
    print("\nAnalysis reports generated:")
    for path in generated:
        print(f"  {path.relative_to(PROJECT_ROOT)}")
    logging.getLogger("simulator").info(
        "Performance analysis generated %d report artifacts", len(generated)
    )


def main():
    """Run the interactive simulator until the user selects Exit."""
    logger = configure_logging()
    actions = {
        "1": _run_cpu,
        "2": _run_memory,
        "3": _run_deadlock,
        "4": _run_disk,
        "5": _run_analysis,
    }
    print("OS Resource Management Simulator")
    while True:
        print(
            "\n1. CPU scheduling\n2. Memory allocation\n3. Deadlock safety\n"
            "4. Disk scheduling\n5. Generate analysis reports\n6. Exit"
        )
        choice = _read_choice("Select an option: ", set(actions) | {"6"})
        if choice == "6":
            logger.info("Application exited")
            print("Goodbye.")
            return
        if choice is None:
            continue
        try:
            actions[choice]()
        except (OSError, ValueError, KeyError, TypeError) as error:
            logger.exception(
                "Application operation failed (%s)", type(error).__name__
            )
            print(f"Unable to complete that operation: {error}")


if __name__ == "__main__":
    main()
