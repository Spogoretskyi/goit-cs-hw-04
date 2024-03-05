import logging
from pathlib import Path
from threading import Thread, Semaphore


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
        results = {}
        threads = []
        semaphore = Semaphore(self.pool_amount)

        for folder in self.folders:
            th = Thread(
                target=self.__get_results,
                args=(semaphore, folder, keywords, results),
            )
            th.start()
            threads.append(th)

        for thread in threads:
            thread.join()

        return results

    # Отримаємо результати пошуку
    def __get_results(self, semaphore, directory, keywords, results):
        semaphore.acquire()
        try:
            for keyword in keywords:
                result = self.search_keyword_in_directory(keyword, directory)
                if result:
                    results.update(result)
        finally:
            semaphore.release()
