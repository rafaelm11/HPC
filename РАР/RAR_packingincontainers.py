import multiprocessing
from itertools import combinations

def can_partition_subset(weights, B):
    """
    Вспомогательная функция для проверки наличия подмножества с суммой <= B.
    """
    n = len(weights)
    dp = [False] * (B + 1)
    dp[0] = True

    for weight in weights:
        for i in range(B, weight - 1, -1):
            if dp[i - weight]:
                dp[i] = True

    for i in range(B, -1, -1):
        if dp[i]:
            return True, i
    return False, 0

def subset_partitioner(weights, B, K, start_idx, end_idx, queue):
    """
    Рабочая функция для разделения подмножества списка весов между start_idx и end_idx.
 Добавляет результаты в очередь многопроцессорной обработки.
    """
    n = len(weights)
    for subset_size in range(start_idx, end_idx):
        for subset in combinations(weights, subset_size):
            can_partition, used_weight = can_partition_subset(subset, B)
            if can_partition:
                remaining_weights = [w for w in weights if w not in subset]
                if K == 1:
                    result = sum(remaining_weights) <= B
                else:
                    result = can_partition_subset(remaining_weights, B)[0]
                if result:
                    queue.put(True)
                    return
    queue.put(False)

def can_partition(weights, B, K):
    """
    Основная функция для проверки того, можно ли разделить веса на K групп с весом каждой группы <= B.
    """
    weights.sort(reverse=True)  # Сортировка весов для повышения производительности
    n = len(weights)
    
    if sum(weights) > K * B:
        return False

    if K == 1:
        return sum(weights) <= B

    queue = multiprocessing.Queue()
    num_workers = multiprocessing.cpu_count()
    batch_size = n // num_workers
    processes = []

    for i in range(num_workers):
        start_idx = i * batch_size
        if i == num_workers - 1:
            end_idx = n
        else:
            end_idx = (i + 1) * batch_size
        
        p = multiprocessing.Process(target=subset_partitioner, args=(weights, B, K-1, start_idx, end_idx, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    while not queue.empty():
        if queue.get():
            return True

    return False
    
if __name__ == "__main__":
    weights = [4, 8, 3, 5, 2, 7, 1]
    B = 10
    K = 3
    print(can_partition(weights, B, K))  # Пример вызова функции, ожидаемый результат: True/False