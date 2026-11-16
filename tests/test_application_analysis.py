import csv
from pathlib import Path

from analysis.performance import generate_reports
from main import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_application_menu_runs_samples_and_returns_to_exit(
    monkeypatch, capsys
):
    answers = iter(
        [
            "1", "4",  # Compare CPU algorithms.
            "2", "4",  # Compare memory algorithms.
            "3",  # Run the Banker's sample.
            "4", "4",  # Compare disk algorithms.
            "6",  # Exit.
        ]
    )

    def next_answer(prompt):
        if not prompt:
            raise AssertionError("Expected a visible input prompt.")
        return next(answers)

    monkeypatch.setattr("builtins.input", next_answer)

    main()

    output = capsys.readouterr().out
    assert "Average waiting time: 5.75" in output
    assert "Internal fragmentation: 559 KB" in output
    assert "System state: Safe" in output
    assert "Total head movement: 331 tracks" in output
    assert "Goodbye." in output


def test_invalid_menu_choice_recovers(monkeypatch, capsys):
    answers = iter(["invalid", "6"])

    def next_answer(prompt):
        if not prompt:
            raise AssertionError("Expected a visible input prompt.")
        return next(answers)

    monkeypatch.setattr("builtins.input", next_answer)

    main()

    output = capsys.readouterr().out
    assert "Invalid choice." in output
    assert "Goodbye." in output


def test_analysis_generates_csv_charts_and_trace():
    generated = generate_reports()

    assert len(generated) == 7
    assert all(path.is_file() for path in generated)
    assert all(path.stat().st_size > 0 for path in generated)

    with (PROJECT_ROOT / "reports" / "cpu_comparison.csv").open(
        newline="", encoding="utf-8"
    ) as report_file:
        rows = list(csv.DictReader(report_file))
    assert [row["average_waiting_time"] for row in rows] == [
        "5.75",
        "4.0",
        "7.25",
    ]

    trace = (PROJECT_ROOT / "reports" / "sample_outputs.txt").read_text(
        encoding="utf-8"
    )
    assert "Gantt: P1[0-5]" in trace
    assert "3 successful, 1 failed, 559 KB internal fragmentation" in trace
    assert '"block": "B2"' in trace
    assert "331 tracks total" in trace
    assert "movement path [53, 65, 67, 98, 122, 124, 183, 199, 37, 14]" in (
        trace
    )


def test_activity_logger_writes_timestamped_operation():
    from modules.activity_log import configure_activity_logger

    logger = configure_activity_logger(PROJECT_ROOT)
    logger.info("test operation completed")
    for handler in logger.handlers:
        handler.flush()

    log_path = PROJECT_ROOT / "logs" / "activity.log"
    content = log_path.read_text(encoding="utf-8")
    assert "INFO test operation completed" in content
    assert content[:4].isdigit()
