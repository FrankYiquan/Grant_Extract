from pathlib import Path
import logging

from funder_pipeline.utils.logging import log_stage

logger = logging.getLogger(__name__)


OUTPUTS_DIR = Path("outputs")


def iter_output_files(outputs_dir=OUTPUTS_DIR):
    root = outputs_dir.resolve()

    if not root.exists():
        raise ValueError(f"Output directory does not exist: {outputs_dir}")

    if not root.is_dir():
        raise ValueError(f"Output path is not a directory: {outputs_dir}")

    expected_root = (Path.cwd() / OUTPUTS_DIR).resolve()
    if root != expected_root:
        raise ValueError(
            "Refusing to clean a path outside the project outputs directory."
        )

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    )


def clean_outputs(dry_run=False):
    files = iter_output_files()

    if not dry_run:
        for path in files:
            path.unlink()

    return files


def run_clean_outputs(args):
    logger.info("")
    logger.info("=" * 80)
    logger.info(
        "JOB RUN: clean_outputs, dry_run=%s",
        args.dry_run,
    )
    logger.info("=" * 80)

    files = clean_outputs(dry_run=args.dry_run)

    log_stage(
        "[1/1] Clean Outputs",
        {
            "Mode": "dry run" if args.dry_run else "delete files",
            "Files Found": len(files),
            "Outputs Directory": OUTPUTS_DIR,
        },
    )

    if args.dry_run:
        for path in files:
            logger.info("Would delete: %s", path)

    logger.info("")
    logger.info("=" * 80)
    logger.info("JOB COMPLETE")
    logger.info("=" * 80)
