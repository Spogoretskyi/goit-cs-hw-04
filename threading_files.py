import os
import time
import concurrent.futures


# Шукаємо ключове слово у файлі
def search_keyword_in_file(keyword, file_path):
    found_paths = []
    try:
        with open(file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                if keyword in line:
                    found_paths.append((file_path, line_num))
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return found_paths


# Шукаємо ключове слово у кожному файлі в певному каталозі
def search_keyword_in_directory(keyword, directory):
    keyword_found = {}
    # Використовуэмо пул потоків для шукання ключового слова
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                futures.append(
                    executor.submit(search_keyword_in_file, keyword, file_path)
                )
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                for file_path, line_num in result:
                    if keyword not in keyword_found:
                        keyword_found[keyword] = []
                    keyword_found[keyword].append((file_path, line_num))
    return keyword_found


# Отримаємо результати пошуку
def get_results(keywords, directory):
    results = {}
    for keyword in keywords:
        result = search_keyword_in_directory(keyword, directory).items()
        results.update(result)
    return results


# Друкуємо результати
def print_results(results):
    print("Search results:")
    for key, value in results.items():
        print(f"Keyword '{key}' found in:")
        for file_path, line_num in value:
            print(f"  - {file_path}, line {line_num}")


def main():
    directory = ".\\files\\"
    keywords = ("python", "science", "guitar", "computer", "JSON", "cluster")

    if not os.path.isdir(directory):
        print("Invalid directory path.")
        return

    start_time = time.time()

    result = get_results(keywords, directory)

    end_time = time.time()
    execution_time = end_time - start_time
    print_results(result)
    print(f"Execution time: {execution_time} seconds")


if __name__ == "__main__":
    main()
