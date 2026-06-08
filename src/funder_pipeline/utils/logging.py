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
    logger.info("")
    logger.info("┌" + "─" * 70 + "┐")

    for key, value in summary.items():
        logger.info(
            "│ %-25s %-42s │",
            key,
            str(value)
        )

    logger.info("└" + "─" * 70 + "┘")