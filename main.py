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
