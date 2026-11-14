
import pytest

from modules.cpu_scheduling import (
    fcfs_scheduling,
    sjf_scheduling,
    round_robin_scheduling
)


# Common sample dataset
@pytest.fixture
def sample_processes():
    return [
        {"pid": "P1", "arrival_time": 0, "burst_time": 5},
        {"pid": "P2", "arrival_time": 1, "burst_time": 3},
        {"pid": "P3", "arrival_time": 2, "burst_time": 8},
        {"pid": "P4", "arrival_time": 3, "burst_time": 2}
    ]


# Test 1: FCFS correctness
def test_fcfs_scheduling(sample_processes):
    result = fcfs_scheduling(sample_processes)

    assert result["average_waiting_time"] == 5.75
    assert result["average_turnaround_time"] == 10.25
    assert result["cpu_utilization"] == 100.0


# Test 2: SJF correctness
def test_sjf_scheduling(sample_processes):
    result = sjf_scheduling(sample_processes)

    assert result["average_waiting_time"] == 4.0
    assert result["average_turnaround_time"] == 8.5
    assert result["cpu_utilization"] == 100.0


# Test 3: Round Robin correctness
def test_round_robin_scheduling(sample_processes):
    result = round_robin_scheduling(
        sample_processes,
        time_quantum=2
    )

    assert result["average_waiting_time"] == 7.25
    assert result["average_turnaround_time"] == 11.75
    assert result["cpu_utilization"] == 100.0


# Test 4: Empty process list
@pytest.mark.parametrize(
    "algorithm",
    [
        fcfs_scheduling,
        sjf_scheduling
    ]
)
def test_empty_process_list(algorithm):
    with pytest.raises(ValueError):
        algorithm([])


def test_empty_round_robin_processes():
    with pytest.raises(ValueError):
        round_robin_scheduling([], 2)


# Test 5: Invalid arrival time
@pytest.mark.parametrize(
    "algorithm",
    [
        fcfs_scheduling,
        sjf_scheduling
    ]
)
def test_negative_arrival_time(algorithm):
    processes = [
        {"pid": "P1", "arrival_time": -1, "burst_time": 5}
    ]

    with pytest.raises(ValueError):
        algorithm(processes)


# Test 6: Invalid burst time
@pytest.mark.parametrize(
    "algorithm",
    [
        fcfs_scheduling,
        sjf_scheduling
    ]
)
def test_zero_burst_time(algorithm):
    processes = [
        {"pid": "P1", "arrival_time": 0, "burst_time": 0}
    ]

    with pytest.raises(ValueError):
        algorithm(processes)


# Test 7: Invalid Round Robin quantum
@pytest.mark.parametrize("quantum", [0, -1, 1.5, True])
def test_invalid_time_quantum(sample_processes, quantum):
    with pytest.raises(ValueError):
        round_robin_scheduling(sample_processes, quantum)


# Test 8: CPU idle time handling
def test_cpu_idle_time():
    processes = [
        {"pid": "P1", "arrival_time": 3, "burst_time": 2}
    ]

    result = fcfs_scheduling(processes)

    assert result["gantt_chart"][0] == {
        "pid": "IDLE",
        "start": 0,
        "end": 3
    }

    assert result["results"][0]["completion_time"] == 5
    assert result["cpu_utilization"] == 40.0


# Test 9: Round Robin process completion
def test_round_robin_completion(sample_processes):
    result = round_robin_scheduling(sample_processes, 2)

    assert len(result["results"]) == 4

    for process in result["results"]:
        assert process["completion_time"] > 0
        assert process["waiting_time"] >= 0
        assert process["turnaround_time"] > 0


# Test 10: Duplicate process IDs rejected by Round Robin
def test_duplicate_process_ids():
    processes = [
        {"pid": "P1", "arrival_time": 0, "burst_time": 3},
        {"pid": "P1", "arrival_time": 1, "burst_time": 2}
    ]

    with pytest.raises(ValueError):
        round_robin_scheduling(processes, 2)
