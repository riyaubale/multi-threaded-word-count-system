import sys
import os
import gzip
import threading
from collections import Counter, defaultdict
import pandas as pd

shared_per_file_counts = {}
data_lock = threading.Lock()

def process_file(file_path, output_file, threads):
    """Processes a single gzipped text file to count word occurrences."""
    filename = os.path.basename(file_path)
    print(f"start {filename}")

    local_word_counts = Counter()
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            for line in f:
                words = line.lower().split()
                for word in words:
                    # Basic punctuation removal - can be expanded
                    cleaned_word = ''.join(filter(str.isdigit, word))
                    if cleaned_word:
                        local_word_counts[cleaned_word] += 1
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return

    with data_lock:
        shared_per_file_counts[filename] = local_word_counts

    print(f"finish {filename}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 PROGRAM_NAME <input_directory> <output_file> <threads>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_file = sys.argv[2]
    try:
        num_threads = int(sys.argv[3])
    except ValueError:
        print("Error: <threads> must be an integer.")
        sys.exit(1)

    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' not found.")
        sys.exit(1)

    # Find all .txt.gz files
    files_to_process = [
        os.path.join(input_directory, f)
        for f in os.listdir(input_directory)
        if f.endswith(".txt.gz")
    ]

    if not files_to_process:
        print(f"No .txt.gz files found in '{input_directory}'.")
        sys.exit(0)

    threads = []
    for file_path in files_to_process:
        thread = threading.Thread(target=process_file, args=(file_path, output_file, num_threads))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Aggregate results
    overall_word_counts = Counter()
    all_filenames = sorted(shared_per_file_counts.keys())

    for filename, counts in shared_per_file_counts.items():
        overall_word_counts.update(counts)

    # Prepare data for DataFrame
    data = defaultdict(lambda: defaultdict(int))
    for word, total_count in overall_word_counts.items():
        data[word]['word'] = word
        data[word]['count'] = total_count

    for filename in all_filenames:
        for word, count in shared_per_file_counts[filename].items():
            data[word][filename] = count

    # Convert to DataFrame
    df_data = list(data.values())
    df = pd.DataFrame(df_data)

    # Ensure all columns are present, fill missing with 0
    all_columns = ['word', 'count'] + all_filenames
    for col in all_columns:
        if col not in df.columns:
            df[col] = 0
    
    # Reorder columns to match spec
    df = df[['word', 'count'] + all_filenames]

    # Save to output file
    try:
        if output_file.endswith(".csv"):
            df.to_csv(output_file, index=False)
        elif output_file.endswith(".parquet"):
            df.to_parquet(output_file, index=False)
        elif output_file.endswith(".arrow"):
            df.to_arrow(output_file, index=False)
        else:
            print(f"Unsupported output file extension for '{output_file}'. Please use .csv, .parquet, or .arrow.")
            sys.exit(1)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving output file {output_file}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
