import os
import logging.config

LOG_FILE = "twitchbot.log"
FORMAT = "%(asctime)-15s | %(threadName)-11s | %(levelname)-5s | %(message)s"


def configure_logging():
    """Configures logging for the project"""

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'root_formatter': {
                'format': FORMAT
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO' if not os.environ.get("DEBUG") else 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'root_formatter'
            },
            'log_file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'filename': LOG_FILE,
                'formatter': 'root_formatter',
            }
        },
        'loggers': {
            '': {
                'handlers': [
                    'console',
                    'log_file',
                ],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    })
