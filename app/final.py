import os
import sys
import gzip
import collections
import concurrent.futures
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq
import pyarrow.feather as feather
import random

def process_file(file_path):
    """Process one gzipped text file and return a (filename, Counter)."""
    filename = os.path.basename(file_path)
    print(f"start {filename}")

    local_counts = collections.Counter()
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
            data = f.read()
        words = data.lower().split()
        local_counts.update(words)
    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)

    print(f"finish {filename}")
    return filename, local_counts


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 final.py <input_directory> <output_file> <threads>", file=sys.stderr)
        sys.exit(1)

    input_dir, output_file, threads = sys.argv[1], sys.argv[2], int(sys.argv[3])
    if not os.path.isdir(input_dir):
        print(f"Input directory '{input_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    # Find and shuffle gzipped files
    gz_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(input_dir)
        for f in files if f.endswith(".txt.gz")
    ]
    if not gz_files:
        print(f"No .txt.gz files found in '{input_dir}'.", file=sys.stderr)
        sys.exit(0)

    random.shuffle(gz_files)
    print(f"Found {len(gz_files)} files, using {threads} threads.")

    # Process in parallel — no global lock
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for filename, counts in executor.map(process_file, gz_files):
            results.append((filename, counts))

    # Merge all word counts
    all_counts = collections.Counter()
    for _, counts in results:
        all_counts.update(counts)

    words = sorted(all_counts)
    total = [all_counts[w] for w in words]
    columns = {"word": pa.array(words), "count": pa.array(total)}

    for filename, counts in sorted(results):
        columns[filename] = pa.array([counts.get(w, 0) for w in words])

    table = pa.table(columns)

    # Write the chosen format
    ext = os.path.splitext(output_file)[1].lower()
    try:
        if ext == ".csv":
            with pa.OSFile(output_file, "wb") as f:
                csv.write_csv(table, f)
        elif ext == ".parquet":
            pq.write_table(table, output_file)
        elif ext in (".arrow", ".feather"):
            feather.write_feather(table, output_file)
        else:
            print(f"Unsupported extension '{ext}'.", file=sys.stderr)
            sys.exit(1)
        print(f"Results successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

