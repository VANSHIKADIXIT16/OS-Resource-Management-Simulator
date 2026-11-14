
# OS Resource Management Simulator
## Phase 1: System Design and Planning

### 1. Project Overview

The OS Resource Management Simulator is an integrated Python and Bash application designed to simulate major operating system resource-management functions.

The application demonstrates CPU scheduling, memory allocation, deadlock detection and disk scheduling. It also analyses algorithm performance and generates reports.

### 2. Project Objectives

- Understand major operating system resource-management concepts.
- Implement multiple CPU scheduling algorithms.
- Simulate different memory allocation techniques.
- Detect safe and unsafe resource allocation states.
- Compare disk scheduling algorithms.
- Generate performance reports and visualizations.
- Integrate Python modules through a Bash launcher.

### 3. System Modules

| Module | Algorithms / Functions |
|---|---|
| CPU Scheduling | FCFS, SJF, Round Robin |
| Memory Management | First Fit, Best Fit, Worst Fit |
| Deadlock Management | Banker's Algorithm |
| Disk Scheduling | FCFS, SSTF, SCAN |
| Performance Analysis | Tables, graphs, comparisons |
| Logging | Activity and error logging |

### 4. System Architecture

The application follows a modular architecture.

The Bash launcher starts the Python application. The main application provides a menu and connects the individual resource-management modules.

Each module processes user input and returns results to the main application. The analysis module collects results and generates reports.

### 5. Input and Output Design

CPU Scheduling:
Input: Process ID, arrival time, burst time and time quantum.
Output: Execution sequence, waiting time and turnaround time.

Memory Management:
Input: Memory partition sizes and process sizes.
Output: Allocation results, unused space and allocation failures.

Deadlock Management:
Input: Allocation matrix, maximum demand matrix and available resources.
Output: Safe or unsafe state and safe sequence.

Disk Scheduling:
Input: Initial head position, disk requests and scan direction.
Output: Service sequence and total head movement.

Performance Analysis:
Input: Results from different algorithms.
Output: Comparison tables, charts and reports.

### 6. Data Structures

- Lists: Process queues and disk request queues.
- Dictionaries: Process information and algorithm results.
- Matrices: Resource allocation and maximum demand.
- Classes: Reusable process and memory representations.
- Pandas DataFrames: Performance comparison.

### 7. Performance Metrics

CPU scheduling:
- Average waiting time
- Average turnaround time
- CPU utilization

Memory management:
- Successful allocations
- Failed allocations
- Internal fragmentation
- Remaining free memory

Deadlock:
- Safe or unsafe state
- Safe execution sequence

Disk scheduling:
- Total head movement
- Average head movement per request

### 8. Technology Stack

- Python 3
- Bash scripting
- Visual Studio Code
- Matplotlib
- Pandas
- Pytest
- Git

### 9. Error Handling and Reliability

The system will validate user inputs, handle invalid menu selections, prevent invalid resource requests and record operations in activity logs.

Automated test cases will verify algorithm correctness and boundary conditions.

### 10. Expected Outcome

The final application will provide a unified menu-driven simulator capable of demonstrating and comparing important operating system resource-management techniques.

It will generate analytical results, visualizations and reports for academic demonstration and evaluation.
