import time
import threading_sum
import multiprocessing_sum
import async_sum

M = 20                  # количество замеряемых запусков
WARMUP = 2              # прогревочные запуски (не учитываются)
DELAY = 0.5             # задержка между запусками (секунды)

def benchmark_module(module, name):
    # Прогрев
    print(f"Прогрев {name}...")
    for _ in range(WARMUP):
        module.run()
        time.sleep(DELAY)

    times = []
    for i in range(M):
        start = time.perf_counter()
        module.run()
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        print(f"{name}: запуск {i+1}) {elapsed:.3f} с")
        if i < M - 1:
            time.sleep(DELAY)

    avg = sum(times) / M
    sorted_times = sorted(times)
    if M % 2:
        median = sorted_times[M // 2]
    else:
        median = (sorted_times[M // 2 - 1] + sorted_times[M // 2]) / 2
    return times, avg, median

def main():
    print("=== task1: статистика времени ===")
    avgs = {}
    medians = {}
    for module, name in [(threading_sum, "threading"),
                         (multiprocessing_sum, "multiprocessing"),
                         (async_sum, "async")]:
        print(f"\n---{name}:---")
        times, avg, median = benchmark_module(module, name)
        avgs[name] = avg
        medians[name] = median
        for i, t in enumerate(times, 1):
            print(f"{i}) {t:.3f} с")
        print(f"Среднее: {avg:.3f} с")
        print(f"Медиана: {median:.3f} с")

    print("\n=== Сравнение ===")
    for name in avgs:
        print(f"{name}: среднее {avgs[name]:.3f} с, медиана {medians[name]:.3f} с")
    best_avg = min(avgs, key=avgs.get)
    best_median = min(medians, key=medians.get)
    print(f"Самый быстрый по среднему: {best_avg} ({avgs[best_avg]:.3f} с)")
    print(f"Самый быстрый по медиане: {best_median} ({medians[best_median]:.3f} с)")

if __name__ == "__main__":
    main()