import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Any

class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head: Node | None = None
        self.tail: Node | None = None

    def push(self, key, value) -> Node:
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node: Node) -> None:
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node: Node) -> None:
        if node is self.head:
            return
        self.remove(node)
        node.next = self.head
        if self.head:
            self.head.prev = node
        else:
            self.tail = node
        self.head = node

    def remove_last(self) -> Node | None:
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[Any, Node] = {}
        self.list = DoublyLinkedList()

    def get(self, key: Any):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key: Any, value: Any) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node

def range_sum_no_cache(array: List[int], left: int, right: int) -> int:
    return sum(array[left:right+1])

def update_no_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value

def range_sum_with_cache(array: List[int], left: int, right: int, cache: LRUCache) -> int:
    key = (left, right)
    cached = cache.get(key)
    if cached != -1:
        return cached
    res = sum(array[left:right+1])
    cache.put(key, res)
    return res

def update_with_cache(array: List[int], index: int, value: int, cache: LRUCache) -> None:
    array[index] = value
    keys = list(cache.cache.keys())
    for k in keys:
        l, r = k
        if l <= index <= r:
            node = cache.cache.pop(k, None)
            if node:
                cache.list.remove(node)

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries

@dataclass
class BenchResult:
    elapsed_sec: float
    checksum: int
    label: str

def run_benchmark(n: int, q: int, seed: int, use_cache: bool) -> BenchResult:
    random.seed(seed)
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    a = array.copy()
    cache = LRUCache(1000) if use_cache else None
    checksum = 0
    t0 = time.perf_counter()

    for item in queries:
        if item[0] == "Range":
            _, L, R = item
            if use_cache:
                res = range_sum_with_cache(a, L, R, cache)
            else:
                res = range_sum_no_cache(a, L, R)
            checksum = (checksum * 1315423911) ^ res
        else:
            _, idx, val = item
            if use_cache:
                update_with_cache(a, idx, val, cache)
            else:
                update_no_cache(a, idx, val)

    t1 = time.perf_counter()
    return BenchResult(t1 - t0, checksum, "LRU-кеш" if use_cache else "Без кешу")

def main():
    N = 100000
    Q = 50000
    SEED = 34

    no_cache = run_benchmark(N, Q, SEED, use_cache=False)
    with_cache = run_benchmark(N, Q, SEED, use_cache=True)

    if no_cache.checksum != with_cache.checksum:
        print("⚠️ Checksums differ! Можлива помилка в реалізації.")

    print(f"Без кешу : {no_cache.elapsed_sec:8.2f} c")
    print(f"LRU-кеш  : {with_cache.elapsed_sec:8.2f} c  (прискорення ×{no_cache.elapsed_sec / with_cache.elapsed_sec:0.2f})")

if __name__ == "__main__":
    main()
