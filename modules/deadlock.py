"""Banker's Algorithm for resource-allocation safety checks."""

from typing import Sequence, TypedDict


class BankerResult(TypedDict):
    algorithm: str
    is_safe: bool
    status: str
    need: list[list[int]]
    safe_sequence: list[str]
    available: list[int]


def _validate_matrix(
    name: str, matrix: Sequence[Sequence[int]]
) -> tuple[list[list[int]], int]:
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise ValueError(f"{name} must be a non-empty matrix.")

    if any(not isinstance(row, (list, tuple)) or not row for row in matrix):
        raise ValueError(f"Every row in {name} must be non-empty.")

    resource_count = len(matrix[0])
    if any(len(row) != resource_count for row in matrix):
        raise ValueError(f"Rows in {name} must have equal length.")

    for row in matrix:
        if any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            for value in row
        ):
            raise ValueError(f"{name} values must be non-negative integers.")

    return [list(row) for row in matrix], resource_count


def bankers_algorithm(
    allocation: Sequence[Sequence[int]],
    maximum: Sequence[Sequence[int]],
    available: Sequence[int],
) -> BankerResult:
    """Return whether a resource state is safe and, if so, its safe sequence.

    ``allocation`` and ``maximum`` are process-by-resource matrices. ``available``
    contains one available-resource count for each resource type.
    """
    allocation_matrix, resource_count = _validate_matrix(
        "Allocation", allocation
    )
    maximum_matrix, maximum_resource_count = _validate_matrix("Max", maximum)

    if len(allocation_matrix) != len(maximum_matrix):
        raise ValueError("Allocation and Max must have the same process count.")
    if resource_count != maximum_resource_count:
        raise ValueError("Allocation and Max must have the same resource count.")
    if not isinstance(available, (list, tuple)) or len(available) != resource_count:
        raise ValueError("Available must contain one value per resource.")
    if any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        for value in available
    ):
        raise ValueError("Available values must be non-negative integers.")

    need = []
    for process_index, (allocated, maximum_row) in enumerate(
        zip(allocation_matrix, maximum_matrix)
    ):
        if any(used > claim for used, claim in zip(allocated, maximum_row)):
            raise ValueError(
                f"Allocation cannot exceed Max for process P{process_index}."
            )
        need.append(
            [claim - used for used, claim in zip(allocated, maximum_row)]
        )

    work = list(available)
    finished = [False] * len(allocation_matrix)
    safe_sequence = []

    while len(safe_sequence) < len(allocation_matrix):
        for process_index, process_need in enumerate(need):
            if finished[process_index] or any(
                required > free for required, free in zip(process_need, work)
            ):
                continue

            work = [
                free + allocated
                for free, allocated in zip(
                    work, allocation_matrix[process_index]
                )
            ]
            finished[process_index] = True
            safe_sequence.append(f"P{process_index}")
            break
        else:
            break

    is_safe = all(finished)
    return {
        "algorithm": "Banker's Algorithm",
        "is_safe": is_safe,
        "status": "Safe" if is_safe else "Unsafe",
        "need": need,
        "safe_sequence": safe_sequence if is_safe else [],
        "available": list(available),
    }