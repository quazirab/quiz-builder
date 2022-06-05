import logging
import logging.handlers
import os
import sys

# =================================================


def init_logging(level="DEBUG", log_filename=None, slack_hook=None) -> None:
    """
    Initiates logger
    Args:
        level:        logging level (debug or info)
        log_filename: log filename
        slack_hook:   slack hook
    Returns:
        None
    """

    main_logger = logging.getLogger()

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d: %(levelname)-8s: %(name)-24s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if level == "DEBUG":
        main_logger.setLevel(logging.DEBUG)
    else:
        main_logger.setLevel(logging.INFO)

    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setFormatter(formatter)
    main_logger.addHandler(handler_stream)

    if log_filename:
        # Check if log exists and should therefore be rolled
        needRoll = os.path.isfile(log_filename)

        handler_file = logging.handlers.RotatingFileHandler(
            log_filename, maxBytes=2**24, backupCount=10
        )

        handler_file.setFormatter(formatter)

        main_logger.addHandler(handler_file)

        if needRoll:
            # Roll over on application start
            handler_file.doRollover()

    if slack_hook:
        try:
            from slack_log_handler import SlackLogHandler
        except ImportError:
            print("pip install slack_log_handler to use slack hooks")

        slack_handler = SlackLogHandler(slack_hook)
        slack_handler.setLevel(logging.WARNING)
        main_logger.addHandler(slack_handler)


# =================================================
