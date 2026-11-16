import pytest

from modules.deadlock import bankers_algorithm
from modules.disk_scheduling import (
    fcfs_disk_scheduling,
    scan_disk_scheduling,
    sstf_disk_scheduling,
)


SAFE_ALLOCATION = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2],
]
SAFE_MAXIMUM = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
]


def test_bankers_algorithm_safe_state_and_need_matrix():
    result = bankers_algorithm(SAFE_ALLOCATION, SAFE_MAXIMUM, [3, 3, 2])

    assert result["is_safe"] is True
    assert result["status"] == "Safe"
    assert result["need"] == [
        [7, 4, 3],
        [1, 2, 2],
        [6, 0, 0],
        [0, 1, 1],
        [4, 3, 1],
    ]
    assert result["safe_sequence"] == ["P1", "P3", "P0", "P2", "P4"]


def test_bankers_algorithm_unsafe_state_has_no_safe_sequence():
    result = bankers_algorithm([[1, 0], [0, 1]], [[2, 0], [0, 2]], [0, 0])

    assert result["is_safe"] is False
    assert result["status"] == "Unsafe"
    assert result["safe_sequence"] == []


@pytest.mark.parametrize(
    "allocation, maximum, available",
    [
        ([], [], []),
        ([[0, 0]], [[1]], [1]),
        ([[0], [0]], [[1]], [1]),
        ([[2]], [[1]], [0]),
        ([[-1]], [[1]], [0]),
        ([[0]], [[1]], [-1]),
        ([[0]], [[1]], [1, 2]),
        ([[0.5]], [[1]], [0]),
        ([[False]], [[1]], [0]),
        ([[0]], [[True]], [0]),
    ],
)
def test_bankers_algorithm_rejects_invalid_matrices(
    allocation, maximum, available
):
    with pytest.raises(ValueError):
        bankers_algorithm(allocation, maximum, available)


def test_bankers_algorithm_does_not_mutate_inputs():
    allocation = [[0, 1], [1, 0]]
    maximum = [[1, 1], [1, 1]]
    available = [1, 1]
    original = ([row[:] for row in allocation], [row[:] for row in maximum])

    bankers_algorithm(allocation, maximum, available)

    assert (allocation, maximum) == original
    assert available == [1, 1]


def test_disk_fcfs_preserves_duplicates_and_head_requests():
    result = fcfs_disk_scheduling([50, 90, 50], 50, 101)

    assert result["service_order"] == [50, 90, 50]
    assert result["movement_path"] == [50, 50, 90, 50]
    assert result["total_head_movement"] == 80
    assert result["average_head_movement"] == pytest.approx(80 / 3)


def test_disk_sstf_sample_and_tie_breaking():
    sample = [98, 183, 37, 122, 14, 124, 65, 67]
    result = sstf_disk_scheduling(sample, 53, 200)

    assert result["service_order"] == [65, 67, 37, 14, 98, 122, 124, 183]
    assert result["total_head_movement"] == 236
    assert result["average_head_movement"] == 29.5

    tied = sstf_disk_scheduling([40, 60], 50, 101)
    assert tied["service_order"] == [40, 60]


@pytest.mark.parametrize(
    "direction, expected_order, expected_movement",
    [
        ("right", [65, 67, 98, 122, 124, 183, 37, 14], 331),
        ("left", [37, 14, 65, 67, 98, 122, 124, 183], 236),
    ],
)
def test_disk_scan_sample_in_both_directions(
    direction, expected_order, expected_movement
):
    sample = [98, 183, 37, 122, 14, 124, 65, 67]
    result = scan_disk_scheduling(sample, 53, 200, direction)

    assert result["service_order"] == expected_order
    assert result["total_head_movement"] == expected_movement


def test_disk_scan_handles_duplicate_and_boundary_tracks():
    result = scan_disk_scheduling([0, 0, 10, 10], 0, 11, "right")

    assert result["service_order"] == [0, 0, 10, 10]
    assert result["total_head_movement"] == 10
    assert result["movement_path"] == [0, 0, 0, 10, 10, 10]


def test_disk_algorithms_accept_empty_requests():
    for algorithm in (
        fcfs_disk_scheduling([], 0, 1),
        sstf_disk_scheduling([], 0, 1),
        scan_disk_scheduling([], 0, 1, "left"),
    ):
        assert algorithm["service_order"] == []
        assert algorithm["total_head_movement"] == 0
        assert algorithm["average_head_movement"] == 0


@pytest.mark.parametrize(
    "requests, head, size, direction",
    [
        ([1], 0, 0, "right"),
        ([1], -1, 10, "right"),
        ([10], 0, 10, "right"),
        ([1.5], 0, 10, "right"),
        ([True], 0, 10, "right"),
        ([1], True, 10, "right"),
        ([1], 0, 10, "up"),
        (None, 0, 10, "right"),
    ],
)
def test_disk_algorithms_reject_invalid_inputs(requests, head, size, direction):
    with pytest.raises(ValueError):
        scan_disk_scheduling(requests, head, size, direction)


def test_disk_fcfs_and_sstf_validate_request_bounds():
    with pytest.raises(ValueError):
        fcfs_disk_scheduling([11], 0, 10)
    with pytest.raises(ValueError):
        sstf_disk_scheduling([-1], 0, 10)
