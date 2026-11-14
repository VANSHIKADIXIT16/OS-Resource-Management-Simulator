
from modules.memory_management import (
    memory_allocation,
    display_memory_result
)

blocks = [100, 500, 200, 300, 600]

processes = [
    {"pid": "P1", "size": 212},
    {"pid": "P2", "size": 417},
    {"pid": "P3", "size": 112},
    {"pid": "P4", "size": 426}
]

algorithms = [
    "First Fit",
    "Best Fit",
    "Worst Fit"
]

for algorithm in algorithms:

    result = memory_allocation(
        blocks,
        processes,
        algorithm
    )

    display_memory_result(result)
