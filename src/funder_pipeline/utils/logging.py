import logging

logger = logging.getLogger(__name__)


def log_stage(title, metrics):
    logger.info("")
    logger.info("=" * 80)
    logger.info("%s", title)
    logger.info("-" * 80)

    for key, value in metrics.items():
        logger.info("%-25s : %s", key, value)


def log_summary(summary):
    value_width = max(42, *(len(str(value)) for value in summary.values()))
    inner_width = 1 + 25 + 1 + value_width + 1

    logger.info("")
    logger.info("┌" + "─" * inner_width + "┐")

    for key, value in summary.items():
        logger.info(
            "│ %-25s %-*s │",
            key,
            value_width,
            str(value)
        )

    logger.info("└" + "─" * inner_width + "┘")
