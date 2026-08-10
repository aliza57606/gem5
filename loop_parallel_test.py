import math
import os
import time
from concurrent.futures import ProcessPoolExecutor

LIMIT = 1_000_000
WORKERS = min(8, os.cpu_count() or 1)


def is_prime(number: int) -> bool:
    if number < 2:
        return False

    if number == 2:
        return True

    if number % 2 == 0:
        return False

    maximum_divisor = int(math.sqrt(number))

    for divisor in range(3, maximum_divisor + 1, 2):
        if number % divisor == 0:
            return False

    return True


def count_primes_in_range(start: int, end: int) -> int:
    count = 0

    for number in range(start, end):
        if is_prime(number):
            count += 1

    return count


def create_ranges(limit: int, workers: int) -> list[tuple[int, int]]:
    chunk_size = math.ceil(limit / workers)
    ranges = []

    for start in range(0, limit, chunk_size):
        end = min(start + chunk_size, limit)
        ranges.append((start, end))

    return ranges


def run_sequential() -> tuple[int, float]:
    start_time = time.perf_counter()

    count = count_primes_in_range(0, LIMIT)

    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


def run_parallel() -> tuple[int, float]:
    ranges = create_ranges(LIMIT, WORKERS)

    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        results = executor.map(
            count_primes_in_range,
            [item[0] for item in ranges],
            [item[1] for item in ranges],
        )

    count = sum(results)

    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


def main() -> None:
    sequential_count, sequential_time = run_sequential()
    parallel_count, parallel_time = run_parallel()

    speedup = sequential_time / parallel_time

    print(f"CPU cores available: {os.cpu_count()}")
    print(f"Workers used: {WORKERS}")
    print(f"Search range: 0 to {LIMIT:,}")
    print(f"Sequential prime count: {sequential_count}")
    print(f"Parallel prime count: {parallel_count}")
    print(f"Sequential time: {sequential_time:.3f} seconds")
    print(f"Parallel time: {parallel_time:.3f} seconds")
    print(f"Parallel speedup: {speedup:.2f}x")
    print(
        "Results match:",
        sequential_count == parallel_count,
    )


if __name__ == "__main__":
    main()
