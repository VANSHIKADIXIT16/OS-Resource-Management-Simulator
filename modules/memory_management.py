
def validate_memory_input(blocks, processes):
    """Validate memory blocks and process requests."""

    if not blocks:
        raise ValueError("Memory blocks cannot be empty.")

    if not processes:
        raise ValueError("Process list cannot be empty.")

    if any(
        not isinstance(size, int) or isinstance(size, bool) or size <= 0
        for size in blocks
    ):
        raise ValueError("Block sizes must be positive integers.")

    seen_pids = set()

    for process in processes:
        if not isinstance(process, dict):
            raise ValueError("Each process must be a dictionary.")

        if not {"pid", "size"}.issubset(process):
            raise ValueError("Each process needs pid and size.")

        pid = process["pid"]
        size = process["size"]

        if not isinstance(pid, str) or not pid.strip():
            raise ValueError("Process ID must be a non-empty string.")

        if pid in seen_pids:
            raise ValueError("Process IDs must be unique.")

        seen_pids.add(pid)

        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size <= 0
        ):
            raise ValueError("Process sizes must be positive integers.")


def memory_allocation(blocks, processes, algorithm):
    """
    Simulate fixed-partition memory allocation.

    Supported algorithms:
    First Fit, Best Fit, Worst Fit.
    """

    validate_memory_input(blocks, processes)

    if algorithm not in ("First Fit", "Best Fit", "Worst Fit"):
        raise ValueError("Invalid memory allocation algorithm.")

    # Each partition can hold only one process.
    free_blocks = list(blocks)

    results = []

    for process in processes:

        pid = process["pid"]
        required = process["size"]

        suitable_blocks = [
            index
            for index, size in enumerate(free_blocks)
            if size is not None and size >= required
        ]

        if not suitable_blocks:
            results.append({
                "pid": pid,
                "required_memory": required,
                "block": None,
                "allocated_memory": 0,
                "fragmentation": 0,
                "status": "Not Allocated"
            })
            continue

        if algorithm == "First Fit":
            selected = suitable_blocks[0]

        elif algorithm == "Best Fit":
            selected = min(
                suitable_blocks,
                key=lambda index: free_blocks[index]
            )

        else:
            selected = max(
                suitable_blocks,
                key=lambda index: free_blocks[index]
            )

        allocated_size = free_blocks[selected]

        internal_fragmentation = (
            allocated_size - required
        )

        results.append({
            "pid": pid,
            "required_memory": required,
            "block": f"B{selected + 1}",
            "allocated_memory": allocated_size,
            "fragmentation": internal_fragmentation,
            "status": "Allocated"
        })

        # Mark the partition as occupied.
        free_blocks[selected] = None

    successful = sum(
        1 for item in results
        if item["status"] == "Allocated"
    )

    failed = len(processes) - successful

    total_allocated = sum(
        item["allocated_memory"]
        for item in results
    )

    total_fragmentation = sum(
        item["fragmentation"]
        for item in results
    )

    remaining_free = sum(
        size for size in free_blocks
        if size is not None
    )

    total_memory = sum(blocks)

    memory_utilization = (
        total_allocated / total_memory * 100
        if total_memory else 0
    )

    return {
        "algorithm": algorithm,
        "results": results,
        "successful_allocations": successful,
        "failed_allocations": failed,
        "total_allocated_memory": total_allocated,
        "total_internal_fragmentation": total_fragmentation,
        "remaining_free_memory": remaining_free,
        "memory_utilization": memory_utilization
    }


def display_memory_result(result):

    print(f"\n========== {result['algorithm']} ==========")

    print(
        f"{'Process':<12}"
        f"{'Required':<12}"
        f"{'Block':<12}"
        f"{'Allocated':<12}"
        f"{'Fragmentation':<15}"
        f"{'Status':<15}"
    )

    print("-" * 78)

    for item in result["results"]:

        print(
            f"{item['pid']:<12}"
            f"{item['required_memory']:<12}"
            f"{item['block'] or '-':<12}"
            f"{item['allocated_memory']:<12}"
            f"{item['fragmentation']:<15}"
            f"{item['status']:<15}"
        )

    print("\nSuccessful allocations:",
          result["successful_allocations"])

    print("Failed allocations:",
          result["failed_allocations"])

    print("Total internal fragmentation:",
          result["total_internal_fragmentation"], "KB")

    print("Remaining free memory:",
          result["remaining_free_memory"], "KB")

    print("Memory utilization:",
          round(result["memory_utilization"], 2), "%")
