import logging
from environs import Env

env = Env(expand_vars=True)
env.read_env('../.env')

logging.basicConfig(format='[%(asctime)s]:%(name)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
# New in version 3.11
# LOGGING_LEVEL = logging.getLevelNamesMapping()[env("LOGGING_LEVEL", 'WARNING')]
LOGGING_LEVEL = env("LOGGING_LEVEL", 'WARNING')
logger.setLevel(LOGGING_LEVEL)
logging.getLogger('schedule').setLevel(LOGGING_LEVEL)
logging.getLogger('sqlalchemy.engine').setLevel(LOGGING_LEVEL)
