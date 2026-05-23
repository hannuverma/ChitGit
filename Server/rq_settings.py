from redis import Redis
from config.config import REDIS_URL
REDIS_CLASS = Redis

REDIS_URL = REDIS_URL

REDIS_KWARGS = {
    "ssl_cert_reqs": None
}   