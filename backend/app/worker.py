import logging
import time

from .config import settings

logger = logging.getLogger(__name__)


def run() -> None:
    logger.info("Aria worker started; queue=%s", settings.redis_url)
    while True:
        time.sleep(5)


if __name__ == "__main__":
    run()
