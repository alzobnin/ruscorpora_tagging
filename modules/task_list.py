import multiprocessing

TASKS = []

import config

def add_task(in_path, out_path):
    global TASKS
    TASKS.append((in_path, out_path))

def execute_tasks_chunked(in_callback):
    task_chunk_size = 100
    result = []
    try:
        for task_chunk_index in xrange(0, len(TASKS), task_chunk_size):
            pool = multiprocessing.Pool(processes=config.CONFIG['jobs_number'])
            chunk_result = pool.map(in_callback, TASKS[task_chunk_size * task_chunk_index : task_chunk_size * (task_chunk_index + 1)])
            pool.close()
            pool.join()
            result += chunk_result
    except:
        pool.terminate()
    return result

def execute_tasks(in_callback):
    try:
        pool = multiprocessing.Pool(processes=config.CONFIG['jobs_number'])
        result = pool.map(in_callback, TASKS)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pool.terminate()
    return result

def execute_tasks_single_thread(in_callback):
    result = [in_callback(task) for task in TASKS]
    return result
