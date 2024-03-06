import logging
from pathlib import Path
from threading import Thread, Semaphore
from multiprocessing import JoinableQueue, Process, Lock, Manager


class BaseThreadingFiles:
    def __init__(self, logger):
        self.logger = logger

    # Шукаємо ключове слово у файлі
    def search_keyword_in_file(self, keyword, file_path):
        found_paths = []
        try:
            with open(file_path, "r") as file:
                for line_num, line in enumerate(file, 1):
                    if keyword in line:
                        found_paths.append((file_path, line_num))
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
        return found_paths

    # Шукаємо ключове слово у кожному файлі в певному каталозі
    def search_keyword_in_directory(self, keyword, directory):
        keyword_found = {}
        for file_path in Path(directory).rglob("*"):
            if file_path.is_file():
                result = self.search_keyword_in_file(keyword, str(file_path))
                if result:
                    if keyword not in keyword_found:
                        keyword_found[keyword] = []
                    keyword_found[keyword].extend(result)
        return keyword_found


class ThreadingFiles(BaseThreadingFiles):
    def __init__(self, logger, folders, pool_amount):
        super().__init__(logger)
        self.folders = folders
        self.pool_amount = pool_amount

    # Оброблюємо файли
    def process_files(self, keywords):
        self.logger.info(f"{self.__class__.__name__}: process files.")
        results = {}
        threads = []
        semaphore = Semaphore(self.pool_amount)

        for folder in self.folders:
            th = Thread(
                target=self.get_results,
                args=(semaphore, folder, keywords, results),
            )
            th.start()
            threads.append(th)

        for thread in threads:
            thread.join()

        return results

    # Отримаємо результати пошуку
    def get_results(self, semaphore, directory, keywords, results):
        semaphore.acquire()
        try:
            for keyword in keywords:
                result = self.search_keyword_in_directory(keyword, directory)
                if result:
                    results.update(result)
        finally:
            semaphore.release()


class MultiprocessingFiles(BaseThreadingFiles):
    def __init__(self, logger, folders, queue_length):
        super().__init__(logger)
        self.folders = folders
        self.queue_length = queue_length

    # Оброблюємо файли
    def process_files(self, keywords):
        self.logger.info(f"{self.__class__.__name__}: process files.")
        results = Manager().dict()
        processes = []
        joinable_queue = JoinableQueue()

        for folder in self.folders:
            joinable_queue.put(folder)

        for _ in range(len(self.folders)):
            process = Process(
                target=self.get_results,
                args=(joinable_queue, keywords, results),
            )
            process.start()
            processes.append(process)

        joinable_queue.join()

        for process in processes:
            process.join()

        return dict(results)

    # Отримаємо результати пошуку
    def get_results(self, joinable_queue, keywords, results):
        lock = Lock()
        local_results = {}
        try:

            directory = joinable_queue.get()
            for keyword in keywords:
                result = self.search_keyword_in_directory(keyword, directory)
                if result:
                    self.update_Local_results(result, local_results)
        finally:
            joinable_queue.task_done()
            with lock:
                results.update(local_results)

    @staticmethod
    def update_Local_results(result, local_results):
        for key, value in result.items():
            if key in local_results:
                local_results[key].extend(value)
            else:
                local_results[key] = value
