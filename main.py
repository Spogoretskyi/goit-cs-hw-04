import argparse
import logging
import time
from pathlib import Path
from shutil import copyfile
from threading import Thread
from files_processors import ThreadingFiles


# parser = argparse.ArgumentParser(description="Sorting files")
# parser.add_argument("--source", "-s", required=True, help="Source dir")
# parser.add_argument("--output", "-o", help="Output dir", default="destination")
# args = vars(parser.parse_args())
# source = Path(args["source"])
# output = Path(args["output"])


# Отримаємо папки
def get_folders(path: Path):
    folders = []
    for file in path.iterdir():
        if file.is_dir():
            folders.append(file)
            folders.extend(get_folders(file))
    return folders


# Результати пошуку
def print_results(results):
    print("Search results:")
    for key, value in results.items():
        print(f"Keyword '{key}' found in:")
        for file_path, line_num in value:
            print(f"  - {file_path}, line {line_num}")


# Записуємо результати пошуку у файл
def write_output(results, execution_time, output_path):
    try:
        with open(output_path, "w") as file:
            for key, value in results.items():
                file.write(f"Keyword '{key}' found in:\n")
                for file_path, line_num in value:
                    file.write(f"  - {file_path}, line {line_num}\n")
            file.write(f"Execution time: {execution_time} seconds")
        logger.info(f"Results have been written to '{output_path}' successfully.")
    except Exception as e:
        logger.error(f"An error occurred while writing results to '{output_path}': {e}")


def main():
    logger = logging.getLogger(__name__)
    format = "%(threadName)s %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # source hardcoded or from args = vars(parser.parse_args())
    source = Path(".\\files\\")
    folders = [source] + get_folders(source)
    print(folders)

    keywords = ("python", "science", "guitar", "computer", "JSON", "cluster")

    start_time = time.time()

    threading_files = ThreadingFiles(logger, folders, 5)
    result = threading_files.process_files(keywords)

    end_time = time.time()
    execution_time = end_time - start_time

    print_results(result)
    # write_output(result, execution_time, "output_path.txt")
    print(f"Execution time: {execution_time} seconds")


if __name__ == "__main__":
    main()
