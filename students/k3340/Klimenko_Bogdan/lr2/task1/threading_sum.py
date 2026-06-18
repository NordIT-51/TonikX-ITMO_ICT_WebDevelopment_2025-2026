import threading
import time

N = 100_000_000
NUM_THREADS = 4

def calculate_sum(start, end, results, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    results[index] = total

def run():
    chunk_size = N // NUM_THREADS
    results = [0] * NUM_THREADS
    threads = []
    for i in range(NUM_THREADS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_THREADS - 1 else N
        t = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
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
    print(f"Время выполнения (threading): {elapsed:.4f} секунд")

if __name__ == "__main__":
    main()