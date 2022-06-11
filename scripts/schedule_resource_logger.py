import logging
import json_log_formatter
import sys

def _get_logging(LOG_PATH):

    FORMATTER = json_log_formatter.VerboseJSONFormatter()
    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.INFO)

    FILE_HANDLER = logging.FileHandler(LOG_PATH)
    STREAM_HANDLER = logging.StreamHandler(sys.stdout)

    FILE_HANDLER.setFormatter(FORMATTER)
    STREAM_HANDLER.setFormatter(FORMATTER)

    LOGGER.addHandler(FILE_HANDLER)
    LOGGER.addHandler(STREAM_HANDLER)

    return LOGGER