import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

N = 100_000_000
NUM_TASKS = 4

def calculate_sum_sync(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

async def calculate_sum_async(start, end, executor):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, calculate_sum_sync, start, end)
    return result

async def run_async():
    chunk_size = N // NUM_TASKS
    tasks = []
    with ThreadPoolExecutor(max_workers=NUM_TASKS) as executor:
        for i in range(NUM_TASKS):
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size if i < NUM_TASKS - 1 else N
            tasks.append(calculate_sum_async(start, end, executor))
        results = await asyncio.gather(*tasks)
    total = sum(results)
    expected = N * (N + 1) // 2
    if total != expected:
        print(f"Ошибка: {total} != {expected}")
    return total

def run():
    return asyncio.run(run_async())

def main():
    start_time = time.time()
    result = run()
    elapsed = time.time() - start_time
    print(f"Сумма от 1 до {N}: {result}")
    print(f"Время выполнения (async): {elapsed:.4f} секунд")

if __name__ == "__main__":
    main()