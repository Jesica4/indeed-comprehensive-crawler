import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from parsers.job_parser import parse_job
from outputs.exporter import export_jobs

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT_DIR / "src" / "config" / "settings.example.json"

def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """Load configuration from JSON file, falling back to defaults."""
    config: Dict[str, Any] = {
        "input_path": "data/input.sample.json",
        "output_path": "data/sample_output.json",
        "max_jobs": None,
        "log_level": "INFO",
    }

    path: Optional[Path] = None
    if config_path:
        path = Path(config_path)
        if not path.is_absolute():
            path = ROOT_DIR / path
    else:
        path = DEFAULT_CONFIG_PATH

    if path and path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                user_config = json.load(f)
            if isinstance(user_config, dict):
                config.update(user_config)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Failed to load config from {path}: {exc}")

    return config

def resolve_path(path_str: str) -> Path:
    """Resolve a path relative to project root if not absolute."""
    path = Path(path_str)
    if path.is_absolute():
        return path
    return ROOT_DIR / path

def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

def load_input_data(path: Path) -> List[Dict[str, Any]]:
    logger = logging.getLogger("main")
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    logger.info("Loading input data from %s", path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    # Support alternative envelope formats, e.g., {"items": [...]}
    if isinstance(data, dict):
        for key in ("items", "results", "jobs"):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError("Unsupported input JSON structure; expected list of job objects.")

def process_jobs(
    raw_jobs: List[Dict[str, Any]],
    max_jobs: Optional[int] = None,
) -> List[Dict[str, Any]]:
    logger = logging.getLogger("main")
    processed: List[Dict[str, Any]] = []

    to_process = raw_jobs if max_jobs is None else raw_jobs[: max_jobs]
    logger.info("Processing %d job records", len(to_process))

    for idx, raw in enumerate(to_process, start=1):
        try:
            parsed = parse_job(raw)
            processed.append(parsed)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to parse job at index %d: %s", idx, exc)

    logger.info(
        "Finished processing jobs. Successful: %d / %d",
        len(processed),
        len(to_process),
    )
    return processed

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Indeed Comprehensive Crawler - job & company parser",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_path",
        help="Path to input JSON file with raw Indeed data",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Path to output JSON file for parsed data",
    )
    parser.add_argument(
        "-m",
        "--max-jobs",
        dest="max_jobs",
        type=int,
        help="Maximum number of jobs to process",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        help="Path to configuration JSON file",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    config = load_config(args.config_path)

    # CLI args override config file
    input_path_str = args.input_path or config.get("input_path", "data/input.sample.json")
    output_path_str = args.output_path or config.get("output_path", "data/sample_output.json")
    max_jobs = args.max_jobs if args.max_jobs is not None else config.get("max_jobs")
    log_level = config.get("log_level", "INFO")

    configure_logging(log_level)
    logger = logging.getLogger("main")

    try:
        input_path = resolve_path(input_path_str)
        output_path = resolve_path(output_path_str)

        raw_jobs = load_input_data(input_path)
        logger.info("Loaded %d raw job records", len(raw_jobs))

        parsed_jobs = process_jobs(raw_jobs, max_jobs=max_jobs)
        export_jobs(parsed_jobs, output_path)

        logger.info("Exported %d parsed job records to %s", len(parsed_jobs), output_path)
        print(f"Processed {len(parsed_jobs)} jobs. Output written to: {output_path}")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Fatal error: %s", exc)
        raise SystemExit(1) from exc

if __name__ == "__main__":
    main()