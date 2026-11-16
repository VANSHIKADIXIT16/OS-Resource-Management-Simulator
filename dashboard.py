"""Local Streamlit dashboard sharing the simulator's existing Python algorithms.

Run from the project root: ./dashboard.sh
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analysis.performance import generate_reports
from modules.activity_log import configure_activity_logger
from modules.cpu_scheduling import fcfs_scheduling, sjf_scheduling, round_robin_scheduling
from modules.deadlock import bankers_algorithm
from modules.disk_scheduling import fcfs_disk_scheduling, sstf_disk_scheduling, scan_disk_scheduling
from modules.memory_management import memory_allocation

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
LOG = configure_activity_logger(ROOT)

st.set_page_config(page_title="OS Resource Management", page_icon="🖥️", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background:rgba(128,128,128,.08); border:1px solid rgba(128,128,128,.18); padding:14px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)


def sample(name):
    with (DATA / name).open(encoding="utf-8") as f:
        return json.load(f)


def metrics(items):
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def gantt_chart(items):
    fig, ax = plt.subplots(figsize=(10, 2.6))
    names = list(dict.fromkeys(x["pid"] for x in items))
    cmap = plt.get_cmap("tab20")
    colors = {name: cmap(i % 20) for i, name in enumerate(names)}
    for item in items:
        start, end, pid = item["start"], item["end"], item["pid"]
        ax.barh(0, end-start, left=start, height=.48,
                color="#a7adb8" if pid == "IDLE" else colors[pid], edgecolor="white")
        ax.text((start+end)/2, 0, f"{pid}\n{start}–{end}", ha="center", va="center", fontsize=8)
    ax.set_yticks([])
    ax.set_xlabel("CPU time")
    ax.set_title("Gantt timeline")
    ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def cpu_page():
    st.title("CPU Scheduling")
    st.caption("Edit the workload and compare FCFS, non-preemptive SJF, and Round Robin.")
    initial = pd.DataFrame(sample("cpu_processes.json"))
    edited = st.data_editor(initial, num_rows="dynamic", use_container_width=True,
        column_config={
            "pid": st.column_config.TextColumn("Process ID", required=True),
            "arrival_time": st.column_config.NumberColumn("Arrival time", min_value=0, step=1),
            "burst_time": st.column_config.NumberColumn("Burst time", min_value=1, step=1),
        }, key="cpu_editor")
    quantum = st.number_input("Round Robin time quantum", min_value=1, value=2, step=1)
    if st.button("Run CPU simulations", type="primary"):
        try:
            processes = edited.to_dict("records")
            results = [fcfs_scheduling(processes), sjf_scheduling(processes),
                       round_robin_scheduling(processes, int(quantum))]
            LOG.info("Dashboard CPU run: %d processes", len(processes))
            frame = pd.DataFrame([{
                "Algorithm": r["algorithm"],
                "Average waiting": r["average_waiting_time"],
                "Average turnaround": r["average_turnaround_time"],
                "CPU utilization (%)": r["cpu_utilization"],
            } for r in results])
            st.subheader("Comparison")
            st.dataframe(frame, hide_index=True, use_container_width=True)
            st.bar_chart(frame.set_index("Algorithm")[["Average waiting", "Average turnaround"]])
            for result in results:
                with st.expander(f"{result['algorithm']} details", expanded=True):
                    metrics([
                        ("Avg. waiting", f"{result['average_waiting_time']:.2f}", "Time units"),
                        ("Avg. turnaround", f"{result['average_turnaround_time']:.2f}", "Time units"),
                        ("CPU utilization", f"{result['cpu_utilization']:.2f}%", "Busy time / elapsed time"),
                    ])
                    gantt_chart(result["gantt_chart"])
                    st.dataframe(pd.DataFrame(result["results"]), hide_index=True, use_container_width=True)
        except (ValueError, TypeError, KeyError) as exc:
            st.error(f"CPU input error: {exc}")


def memory_page():
    st.title("Memory Management")
    st.caption("Compare fixed-partition First Fit, Best Fit, and Worst Fit.")
    data = sample("memory_allocation.json")
    blocks = st.text_input("Partition sizes (KB, comma-separated)", ", ".join(map(str, data["blocks"])))
    edited = st.data_editor(pd.DataFrame(data["processes"]), num_rows="dynamic",
        use_container_width=True, key="memory_editor",
        column_config={
            "pid": st.column_config.TextColumn("Process ID", required=True),
            "size": st.column_config.NumberColumn("Requested memory (KB)", min_value=1, step=1),
        })
    if st.button("Run memory allocation", type="primary"):
        try:
            sizes = [int(x.strip()) for x in blocks.split(",") if x.strip()]
            requests = edited.to_dict("records")
            results = [memory_allocation(sizes, requests, a) for a in ("First Fit", "Best Fit", "Worst Fit")]
            LOG.info("Dashboard memory run: %d requests", len(requests))
            frame = pd.DataFrame([{
                "Algorithm": r["algorithm"], "Successful": r["successful_allocations"],
                "Failed": r["failed_allocations"], "Internal fragmentation (KB)": r["total_internal_fragmentation"],
                "Free partitions (KB)": r["remaining_free_memory"],
                "Occupied partition utilization (%)": r["memory_utilization"],
                "Requested memory utilization (%)": r["requested_memory_utilization"],
            } for r in results])
            st.dataframe(frame, hide_index=True, use_container_width=True)
            st.bar_chart(frame.set_index("Algorithm")[["Internal fragmentation (KB)", "Free partitions (KB)"]])
            for result in results:
                with st.expander(f"{result['algorithm']} allocation details"):
                    st.dataframe(pd.DataFrame(result["results"]), hide_index=True, use_container_width=True)
        except (ValueError, TypeError) as exc:
            st.error(f"Memory input error: {exc}")


def deadlock_page():
    st.title("Deadlock Safety — Banker's Algorithm")
    st.caption("Edit Allocation, Max, and Available values to check whether the state is safe.")
    data = sample("deadlock.json")
    columns = [f"R{i+1}" for i in range(len(data["available"]))]
    left, right = st.columns(2)
    with left:
        st.markdown("**Allocation matrix**")
        allocation = st.data_editor(pd.DataFrame(data["allocation"], columns=columns),
                                    use_container_width=True, key="allocation_editor")
    with right:
        st.markdown("**Maximum demand matrix**")
        maximum = st.data_editor(pd.DataFrame(data["max"], columns=columns),
                                 use_container_width=True, key="maximum_editor")
    available_text = st.text_input("Available resources (comma-separated)", ", ".join(map(str, data["available"])))
    if st.button("Check system safety", type="primary"):
        try:
            result = bankers_algorithm(
                allocation.astype(int).values.tolist(),
                maximum.astype(int).values.tolist(),
                [int(x.strip()) for x in available_text.split(",") if x.strip()],
            )
            LOG.info("Dashboard Banker's Algorithm result: %s", result["status"])
            if result["is_safe"]:
                st.success("The system is in a SAFE state.")
                st.markdown("**Safe sequence**")
                st.code("  →  ".join(result["safe_sequence"]))
            else:
                st.warning("The system is in an UNSAFE state. No safe sequence exists.")
            st.markdown("**Need matrix (Max − Allocation)**")
            st.dataframe(pd.DataFrame(result["need"], columns=maximum.columns),
                         hide_index=True, use_container_width=True)
            st.json({"status": result["status"], "available": result["available"],
                     "safe_sequence": result["safe_sequence"]})
        except (ValueError, TypeError, KeyError) as exc:
            st.error(f"Safety-check input error: {exc}")


def disk_page():
    st.title("Disk Scheduling")
    st.caption("Compare FCFS, SSTF, and SCAN. SCAN includes travel to the disk boundary.")
    data = sample("disk_requests.json")
    requests_text = st.text_input("Requests (track numbers, comma-separated)", ", ".join(map(str, data["requests"])))
    a, b, c = st.columns(3)
    head = a.number_input("Initial head", min_value=0, value=int(data["initial_head"]), step=1)
    size = b.number_input("Disk size (tracks)", min_value=1, value=int(data["disk_size"]), step=1)
    direction = c.selectbox("SCAN direction", ["right", "left"], index=0 if data["direction"] == "right" else 1)
    if st.button("Run disk simulations", type="primary"):
        try:
            requests = [int(x.strip()) for x in requests_text.split(",") if x.strip()]
            results = [
                fcfs_disk_scheduling(requests, int(head), int(size)),
                sstf_disk_scheduling(requests, int(head), int(size)),
                scan_disk_scheduling(requests, int(head), int(size), direction),
            ]
            LOG.info("Dashboard disk run: %d requests", len(requests))
            frame = pd.DataFrame([{
                "Algorithm": r["algorithm"], "Requests": r["request_count"],
                "Total movement (tracks)": r["total_head_movement"],
                "Average movement/request": r["average_head_movement"],
            } for r in results])
            st.dataframe(frame, hide_index=True, use_container_width=True)
            st.bar_chart(frame.set_index("Algorithm")[["Total movement (tracks)"]])
            for result in results:
                with st.expander(f"{result['algorithm']} movement path"):
                    st.write("Service order:", result["service_order"])
                    st.write("Movement path:", " → ".join(map(str, result["movement_path"])))
                    st.metric("Total head movement", f"{result['total_head_movement']} tracks")
                    st.metric("Average/request", f"{result['average_head_movement']:.2f} tracks")
        except (ValueError, TypeError) as exc:
            st.error(f"Disk input error: {exc}")


def overview_page():
    st.title("OS Resource Management")
    st.caption("Interactive control centre for the four simulator modules.")
    cpu, memory, deadlock, disk = (
        sample("cpu_processes.json"), sample("memory_allocation.json"),
        sample("deadlock.json"), sample("disk_requests.json")
    )
    metrics([
        ("CPU processes", str(len(cpu)), "Bundled sample"),
        ("Memory partitions", str(len(memory["blocks"])), "Fixed-size partitions"),
        ("Disk requests", str(len(disk["requests"])), "Bundled sample"),
        ("Resource types", str(len(deadlock["available"])), "Banker's Algorithm sample"),
    ])
    st.subheader("Modules")
    st.markdown("""
    - **CPU:** FCFS, non-preemptive SJF, Round Robin, Gantt timelines.
    - **Memory:** First Fit, Best Fit, Worst Fit, internal fragmentation.
    - **Deadlock:** Banker's Algorithm, Need matrix, safe sequence.
    - **Disk:** FCFS, SSTF, SCAN, head movement.
    """)
    st.info("This interface calls the existing Python modules. The terminal app remains available.")


def reports_page():
    st.title("Performance Reports")
    if st.button("Regenerate CSV reports and charts", type="primary"):
        try:
            generated = generate_reports()
            LOG.info("Dashboard regenerated %d report artifacts", len(generated))
            st.success(f"Generated {len(generated)} artifacts.")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            st.error(f"Report generation error: {exc}")
    for name in ("cpu_comparison", "memory_comparison", "disk_comparison"):
        path = REPORTS / f"{name}.csv"
        if path.exists():
            with st.expander(f"{name.replace('_', ' ').title()}", expanded=True):
                st.dataframe(pd.read_csv(path), hide_index=True, use_container_width=True)
                st.download_button(f"Download {path.name}", path.read_bytes(),
                                   file_name=path.name, mime="text/csv", key=f"dl_{name}")
    for name in ("cpu_comparison", "memory_comparison", "disk_comparison"):
        path = REPORTS / f"{name}.png"
        if path.exists():
            st.subheader(name.replace("_", " ").title())
            st.image(str(path), use_container_width=True)
    trace = REPORTS / "sample_outputs.txt"
    if trace.exists():
        with st.expander("Sample output trace"):
            st.code(trace.read_text(encoding="utf-8"))


def data_page():
    st.title("Sample Data")
    st.caption("Inspect/download the JSON samples or replace one with your own JSON file.")
    for name in ("cpu_processes.json", "memory_allocation.json", "deadlock.json", "disk_requests.json"):
        path = DATA / name
        with st.expander(name):
            st.code(path.read_text(encoding="utf-8"), language="json")
            st.download_button(f"Download {name}", path.read_bytes(), file_name=name,
                               mime="application/json", key=f"download_{name}")
            upload = st.file_uploader(f"Replacement JSON for {name}", type=["json"], key=f"upload_{name}")
            if upload is not None and st.button(f"Save replacement: {name}", key=f"save_{name}"):
                try:
                    payload = json.loads(upload.getvalue().decode("utf-8"))
                    if not isinstance(payload, (dict, list)):
                        raise ValueError("JSON root must be an object or array.")
                    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                    st.success(f"Saved {name} in data/.")
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                    st.error(f"Could not save JSON: {exc}")


with st.sidebar:
    st.title("🖥️ OS Simulator")
    st.caption("Resource management lab")
    selected = st.radio("Navigation", [
        "Overview", "CPU Scheduling", "Memory Management", "Deadlock Safety",
        "Disk Scheduling", "Performance Reports", "Sample Data"
    ])
    st.divider()
    st.caption("Local dashboard · Shared Python backend")

{
    "Overview": overview_page,
    "CPU Scheduling": cpu_page,
    "Memory Management": memory_page,
    "Deadlock Safety": deadlock_page,
    "Disk Scheduling": disk_page,
    "Performance Reports": reports_page,
    "Sample Data": data_page,
}[selected]()
