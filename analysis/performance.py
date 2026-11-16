"""Generate comparable CSV summaries and charts from bundled datasets."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "reports"


def _read_sample(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as sample_file:
        return json.load(sample_file)


def _cpu_comparison(processes):
    results = [
        fcfs_scheduling(processes),
        sjf_scheduling(processes),
        round_robin_scheduling(processes, time_quantum=2),
    ]
    return pd.DataFrame(
        [
            {
                "algorithm": result["algorithm"],
                "average_waiting_time": result["average_waiting_time"],
                "average_turnaround_time": result["average_turnaround_time"],
                "cpu_utilization_percent": result["cpu_utilization"],
                "gantt_timeline": " | ".join(
                    f"{item['pid']}[{item['start']}-{item['end']}]"
                    for item in result["gantt_chart"]
                ),
            }
            for result in results
        ]
    )


def _memory_comparison(sample):
    rows = []
    for algorithm in ("First Fit", "Best Fit", "Worst Fit"):
        result = memory_allocation(
            sample["blocks"], sample["processes"], algorithm
        )
        rows.append(
            {
                "algorithm": algorithm,
                "successful_allocations": result["successful_allocations"],
                "failed_allocations": result["failed_allocations"],
                "allocation_results": json.dumps(result["results"]),
                "requested_memory_in_occupied_partitions_kb": sum(
                    item["required_memory"]
                    for item in result["results"]
                    if item["status"] == "Allocated"
                ),
                "total_internal_fragmentation_kb": (
                    result["total_internal_fragmentation"]
                ),
                "remaining_free_partition_memory_kb": (
                    result["remaining_free_memory"]
                ),
                "occupied_partition_utilization_percent": (
                    result["memory_utilization"]
                ),
                "requested_memory_utilization_percent": (
                    result["requested_memory_utilization"]
                ),
            }
        )
    return pd.DataFrame(rows)


def _disk_comparison(sample):
    requests = sample["requests"]
    head = sample["initial_head"]
    disk_size = sample["disk_size"]
    results = [
        fcfs_disk_scheduling(requests, head, disk_size),
        sstf_disk_scheduling(requests, head, disk_size),
        scan_disk_scheduling(
            requests, head, disk_size, sample["direction"]
        ),
    ]
    return pd.DataFrame(
        [
            {
                "algorithm": result["algorithm"],
                "initial_head": head,
                "disk_tracks": disk_size,
                "request_count": result["request_count"],
                "service_order": json.dumps(result["service_order"]),
                "movement_path": json.dumps(result["movement_path"]),
                "total_head_movement_tracks": result["total_head_movement"],
                "average_movement_per_request_tracks": (
                    result["average_head_movement"]
                ),
                "scan_direction": (
                    sample["direction"] if result["algorithm"] == "SCAN" else ""
                ),
            }
            for result in results
        ]
    )


def _save_cpu_chart(frame, path):
    figure, axis = plt.subplots(figsize=(8, 5))
    positions = range(len(frame))
    width = 0.36
    axis.bar(
        [position - width / 2 for position in positions],
        frame["average_waiting_time"],
        width,
        label="Average waiting time",
    )
    axis.bar(
        [position + width / 2 for position in positions],
        frame["average_turnaround_time"],
        width,
        label="Average turnaround time",
    )
    axis.set_xticks(list(positions), frame["algorithm"])
    axis.set_ylabel("Time units")
    axis.set_title("CPU Scheduling: Average Times (shared process workload)")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def _save_memory_chart(frame, path):
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.bar(
        frame["algorithm"],
        frame["requested_memory_in_occupied_partitions_kb"],
        label="Requested memory in successful allocations",
    )
    axis.bar(
        frame["algorithm"],
        frame["total_internal_fragmentation_kb"],
        bottom=frame["requested_memory_in_occupied_partitions_kb"],
        label="Internal fragmentation",
    )
    axis.set_ylabel("Occupied partition memory (KB)")
    axis.set_title("Fixed-Partition Allocation: Occupied Memory Breakdown")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def _save_disk_chart(frame, path):
    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(
        frame["algorithm"], frame["total_head_movement_tracks"]
    )
    axis.bar_label(bars)
    axis.set_ylabel("Total head movement (tracks)")
    axis.set_title(
        "Disk Scheduling: Total Movement "
        f"(head {frame.iloc[0]['initial_head']}, "
        f"{frame.iloc[0]['request_count']} requests)"
    )
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def _sample_trace(cpu, memory, disk, deadlock):
    lines = [
        "OS Resource Management Simulator — reproducible sample trace",
        "",
        "CPU sample: P1=(0,5), P2=(1,3), P3=(2,8), P4=(3,2); RR quantum=2.",
        "CPU metrics: waiting=turnaround minus burst; CPU utilization=busy time "
        "divided by elapsed time from time 0 to final completion.",
    ]
    for row in cpu.to_dict(orient="records"):
        lines.append(
            f"{row['algorithm']}: average waiting "
            f"{row['average_waiting_time']:.2f}, average turnaround "
            f"{row['average_turnaround_time']:.2f}, CPU utilization "
            f"{row['cpu_utilization_percent']:.2f}%; Gantt: "
            f"{row['gantt_timeline']}."
        )
    lines.extend(
        [
            "",
            "Memory sample: fixed blocks [100, 500, 200, 300, 600] KB; "
            "requests [212, 417, 112, 426] KB.",
            "Memory metrics: internal fragmentation is occupied partition "
            "space unused by its process; free memory is unallocated whole "
            "partitions. These are reported separately.",
        ]
    )
    for row in memory.to_dict(orient="records"):
        lines.append(
            f"{row['algorithm']}: {row['successful_allocations']} successful, "
            f"{row['failed_allocations']} failed, "
            f"{row['total_internal_fragmentation_kb']} KB internal "
            f"fragmentation, {row['remaining_free_partition_memory_kb']} KB "
            f"free, {row['occupied_partition_utilization_percent']:.2f}% "
            "occupied-partition utilization; allocations: "
            f"{row['allocation_results']}."
        )
    lines.extend(
        [
            "",
            "Deadlock sample: Banker’s safe-state check.",
            f"State: {deadlock['status']}; safe sequence: "
            f"{' -> '.join(deadlock['safe_sequence']) or '(none)'}.",
            "",
            "Disk sample: head 53, tracks 0–199, requests "
            "[98, 183, 37, 122, 14, 124, 65, 67], SCAN direction right.",
            "Disk metrics: total movement includes SCAN boundary travel; "
            "average movement divides by request count.",
        ]
    )
    for row in disk.to_dict(orient="records"):
        lines.append(
            f"{row['algorithm']}: service order {row['service_order']}, "
            f"movement path {row['movement_path']}, "
            f"{row['total_head_movement_tracks']} tracks total, "
            f"{row['average_movement_per_request_tracks']:.2f} tracks/request."
        )
    return "\n".join(lines) + "\n"


def generate_reports():
    """Create three comparison CSVs/charts and a text sample trace."""
    logger = configure_activity_logger(PROJECT_ROOT)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        cpu = _cpu_comparison(_read_sample("cpu_processes.json"))
        memory = _memory_comparison(_read_sample("memory_allocation.json"))
        disk_sample = _read_sample("disk_requests.json")
        disk = _disk_comparison(disk_sample)
        deadlock_sample = _read_sample("deadlock.json")
        deadlock = bankers_algorithm(
            deadlock_sample["allocation"],
            deadlock_sample["max"],
            deadlock_sample["available"],
        )

        frames = (
            ("cpu_comparison", cpu),
            ("memory_comparison", memory),
            ("disk_comparison", disk),
        )
        generated = []
        for name, frame in frames:
            csv_path = REPORT_DIR / f"{name}.csv"
            frame.to_csv(csv_path, index=False)
            generated.append(csv_path)

        chart_writers = (
            ("cpu_comparison.png", _save_cpu_chart, cpu),
            ("memory_comparison.png", _save_memory_chart, memory),
            ("disk_comparison.png", _save_disk_chart, disk),
        )
        for filename, writer, frame in chart_writers:
            chart_path = REPORT_DIR / filename
            writer(frame, chart_path)
            generated.append(chart_path)

        trace_path = REPORT_DIR / "sample_outputs.txt"
        trace_path.write_text(
            _sample_trace(cpu, memory, disk, deadlock), encoding="utf-8"
        )
        generated.append(trace_path)
        logger.info("Generated %d analysis artifacts", len(generated))
        return generated
    except (OSError, ValueError, KeyError, TypeError):
        logger.exception("Performance report generation failed")
        raise


if __name__ == "__main__":
    for report_path in generate_reports():
        print(report_path.relative_to(PROJECT_ROOT))
