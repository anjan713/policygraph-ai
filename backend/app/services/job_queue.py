from redis import Redis
from rq import Queue
from ..core.config import settings

def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)

def get_queue() -> Queue:
    return Queue(settings.queue_name, connection=get_redis())
