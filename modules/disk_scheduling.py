"""Disk-head scheduling algorithms with explicit seek-distance metrics."""

from typing import Literal, Sequence, TypedDict


class DiskResult(TypedDict):
    algorithm: str
    initial_head: int
    service_order: list[int]
    movement_path: list[int]
    request_count: int
    total_head_movement: int
    average_head_movement: float


def _validate_disk_input(
    requests: Sequence[int], initial_head: int, disk_size: int
) -> None:
    if not isinstance(requests, (list, tuple)):
        raise ValueError("Requests must be a list or tuple of track numbers.")
    if (
        not isinstance(disk_size, int)
        or isinstance(disk_size, bool)
        or disk_size <= 0
    ):
        raise ValueError("Disk size must be a positive integer.")
    if (
        not isinstance(initial_head, int)
        or isinstance(initial_head, bool)
        or not 0 <= initial_head < disk_size
    ):
        raise ValueError("Initial head must be within the disk range.")
    if any(
        not isinstance(request, int)
        or isinstance(request, bool)
        or not 0 <= request < disk_size
        for request in requests
    ):
        raise ValueError("Every request must be within the disk range.")


def _result(
    algorithm: str,
    initial_head: int,
    service_order: Sequence[int],
    movement_path: Sequence[int],
) -> DiskResult:
    total_movement = sum(
        abs(destination - source)
        for source, destination in zip(movement_path, movement_path[1:])
    )
    request_count = len(service_order)
    return {
        "algorithm": algorithm,
        "initial_head": initial_head,
        "service_order": list(service_order),
        "movement_path": list(movement_path),
        "request_count": request_count,
        "total_head_movement": total_movement,
        "average_head_movement": (
            total_movement / request_count if request_count else 0.0
        ),
    }


def fcfs_disk_scheduling(
    requests: Sequence[int], initial_head: int, disk_size: int
) -> DiskResult:
    """Service requests in arrival order, preserving duplicates."""
    _validate_disk_input(requests, initial_head, disk_size)
    order = list(requests)
    return _result(
        "FCFS", initial_head, order, [initial_head, *order]
    )


def sstf_disk_scheduling(
    requests: Sequence[int], initial_head: int, disk_size: int
) -> DiskResult:
    """Service the closest pending request; ties follow input order."""
    _validate_disk_input(requests, initial_head, disk_size)
    pending = list(enumerate(requests))
    order = []
    current_head = initial_head

    while pending:
        selected_index = min(
            range(len(pending)),
            key=lambda index: (
                abs(pending[index][1] - current_head),
                pending[index][0],
            ),
        )
        _, track = pending[selected_index]
        order.append(track)
        current_head = track
        pending.pop(selected_index)

    return _result(
        "SSTF", initial_head, order, [initial_head, *order]
    )


def scan_disk_scheduling(
    requests: Sequence[int],
    initial_head: int,
    disk_size: int,
    direction: Literal["left", "right"] = "right",
) -> DiskResult:
    """Run SCAN to the selected disk boundary, then reverse direction."""
    _validate_disk_input(requests, initial_head, disk_size)
    if direction not in ("left", "right"):
        raise ValueError("Direction must be 'left' or 'right'.")

    if not requests:
        return _result("SCAN", initial_head, [], [initial_head])

    last_track = disk_size - 1
    if direction == "right":
        initial_side = sorted(
            (track for track in requests if track >= initial_head)
        )
        reverse_side = sorted(
            (track for track in requests if track < initial_head),
            reverse=True,
        )
        order = initial_side + reverse_side
        path = [initial_head, *initial_side, last_track, *reverse_side]
    else:
        initial_side = sorted(
            (track for track in requests if track <= initial_head),
            reverse=True,
        )
        reverse_side = sorted(
            track for track in requests if track > initial_head
        )
        order = initial_side + reverse_side
        path = [initial_head, *initial_side, 0, *reverse_side]

    return _result("SCAN", initial_head, order, path)