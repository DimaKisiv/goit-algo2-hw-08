import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = float(window_size)
        self.max_requests = int(max_requests)
        self.history: Dict[str, deque[float]] = {}
        self._now = time.monotonic

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        dq = self.history.get(user_id)
        if not dq:
            return

        window_start = current_time - self.window_size
        while dq and dq[0] <= window_start:
            dq.popleft()

        if not dq:
            del self.history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        now = self._now()
        self._cleanup_window(user_id, now)
        dq = self.history.get(user_id)
        return (dq is None) or (len(dq) < self.max_requests)

    def record_message(self, user_id: str) -> bool:
        now = self._now()
        self._cleanup_window(user_id, now)

        if self.can_send_message(user_id):
            dq = self.history.setdefault(user_id, deque())
            dq.append(now)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        now = self._now()
        self._cleanup_window(user_id, now)
        dq = self.history.get(user_id)

        if not dq or len(dq) < self.max_requests:
            return 0.0

        oldest = dq[0]
        wait = (oldest + self.window_size) - now
        return max(0.0, wait)


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
