from collections import defaultdict, deque
from time import time

from fastapi import HTTPException, status


class RateLimiter:
    def __init__(self) -> None:
        self.storage: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str, limit: int, window_seconds: int) -> None:
        now = time()
        attempts = self.storage[key]
        while attempts and now - attempts[0] >= window_seconds:
            attempts.popleft()
        if len(attempts) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
            )
        attempts.append(now)
