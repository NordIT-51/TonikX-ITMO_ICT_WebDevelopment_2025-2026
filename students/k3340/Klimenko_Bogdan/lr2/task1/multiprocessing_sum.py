import multiprocessing
import time

N = 100_000_000
NUM_PROCESSES = 4

def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

def run():
    chunk_size = N // NUM_PROCESSES
    tasks = []
    for i in range(NUM_PROCESSES):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_PROCESSES - 1 else N
        tasks.append((start, end))
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.starmap(calculate_sum, tasks)
    total = sum(results)
    expected = N * (N + 1) // 2
    if total != expected:
        print(f"Ошибка: {total} != {expected}")
    return total

def main():
    start_time = time.time()
    result = run()
    elapsed = time.time() - start_time
    print(f"Сумма от 1 до {N}: {result}")
    print(f"Время выполнения (multiprocessing): {elapsed:.4f} секунд")

if __name__ == "__main__":
    main()