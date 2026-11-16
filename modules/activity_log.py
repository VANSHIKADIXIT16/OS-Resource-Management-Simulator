"""Shared configuration for the simulator's local activity log."""

import logging
from pathlib import Path


def configure_activity_logger(project_root: str | Path) -> logging.Logger:
    """Return the simulator logger, writing timestamped entries under logs/."""
    logger = logging.getLogger("simulator")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        log_path = Path(project_root) / "logs" / "activity.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
    logger.propagate = False
    return logger
