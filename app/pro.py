import sys
import os
import gzip
import threading
from collections import Counter
import queue
import pandas as pd
import re

def worker(file_queue, global_counts, file_counts, lock):
    """Worker thread function to process files from the queue."""
    while True:
        try:
            filepath = file_queue.get_nowait()
        except queue.Empty:
            break  # Queue is empty

        filename = os.path.basename(filepath)
        print(f"start {filename}")

        local_counts = Counter()
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                for line in f:
                    # Convert to lowercase and find all word characters, ignoring punctuation
                    words = re.findall(r'\b\w+\b', line.lower())
                    local_counts.update(words)
        except Exception as e:
            print(f"Error processing file {filename}: {e}", file=sys.stderr)
            continue

        with lock:
            global_counts.update(local_counts)
            file_counts[filename] = local_counts

        print(f"finish {filename}")

def main():
    """Main function to drive the word counting program."""
    if len(sys.argv) != 4:
        print("Usage: python3 pro.py <input_directory> <output_file> <threads>", file=sys.stderr)
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    try:
        num_threads = int(sys.argv[3])
        if num_threads <= 0:
            raise ValueError
    except ValueError:
        print("Error: <threads> must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    files_to_process = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt.gz')]

    if not files_to_process:
        print(f"No .txt.gz files found in '{input_dir}'.")
        sys.exit(0)

    # Setup for threading
    file_queue = queue.Queue()
    for f in files_to_process:
        file_queue.put(f)

    global_word_counts = Counter()
    file_word_counts = {}  # {filename: Counter}
    lock = threading.Lock()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(file_queue, global_word_counts, file_word_counts, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Prepare data for output
    if not global_word_counts:
        print("No words found in any files.")
        open(output_file, 'w').close()
        return

    all_words = sorted(list(global_word_counts.keys()))
    
    output_data = {
        'word': all_words,
        'count': [global_word_counts[word] for word in all_words]
    }

    file_columns = sorted(file_word_counts.keys())
    for filename in file_columns:
        counts_per_file = file_word_counts[filename]
        output_data[filename] = [counts_per_file.get(word, 0) for word in all_words]

    df = pd.DataFrame(output_data)

    # Write output based on file extension
    try:
        _root, extension = os.path.splitext(output_file)
        if extension == '.csv':
            df.to_csv(output_file, index=False)
        elif extension == '.parquet':
            df.to_parquet(output_file, index=False)
        elif extension == '.arrow':
            df.to_feather(output_file)
        else:
            print(f"Error: Unsupported output format '{extension}'. Supported formats: .csv, .parquet, .arrow", file=sys.stderr)
            sys.exit(1)
        print(f"Successfully wrote results to {output_file}")
    except Exception as e:
        print(f"Error writing to output file {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
