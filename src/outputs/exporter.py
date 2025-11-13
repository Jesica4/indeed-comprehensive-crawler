import json
import logging
from pathlib import Path
from typing import Any, Iterable, List, Dict

logger = logging.getLogger("exporter")

def export_jobs(jobs: Iterable[Dict[str, Any]], output_path: Path) -> None:
    """
    Export parsed job records to a JSON file.

    The output is a pretty-printed JSON array for ease of inspection and downstream
    processing.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    jobs_list: List[Dict[str, Any]] = list(jobs)

    logger.info("Writing %d jobs to %s", len(jobs_list), output_path)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(jobs_list, f, ensure_ascii=False, indent=2)