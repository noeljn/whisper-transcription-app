import os
import redis
from rq import Queue
from rq.worker import Worker

listen = ['default']
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # Create queue objects for each queue name in `listen`
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work()
