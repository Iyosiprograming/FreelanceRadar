import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] [%(levelname)-8s] [%(name)s]%(reset)s: %(message_log_color)s%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'message': {
                'ERROR': 'red',
                'CRITICAL': 'red',
            }
        }
    )
)

logger = logging.getLogger("FreelanceRadar")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False