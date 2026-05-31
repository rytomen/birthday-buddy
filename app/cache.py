import os


class Cache:
    """Обертка над Redis, которая молча отключается, если Redis недоступен."""

    def __init__(self, redis_url=None):
        self._client = None
        url = redis_url or os.environ.get("REDIS_URL")
        if url:
            try:
                import redis

                client = redis.Redis.from_url(url)
                client.ping()
                self._client = client
            except Exception:
                self._client = None

    def get(self, key):
        if self._client is None:
            return None
        try:
            return self._client.get(key)
        except Exception:
            return None

    def set(self, key, value, ttl=3600):
        if self._client is None:
            return None
        try:
            self._client.set(key, value, ex=ttl)
        except Exception:
            return None

    def delete(self, key):
        if self._client is None:
            return None
        try:
            self._client.delete(key)
        except Exception:
            return None
