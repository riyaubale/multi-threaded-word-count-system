import os
import sys
import time
import gzip
import random
import string
import subprocess
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq
import pyarrow.feather as feather
import matplotlib.pyplot as plt
import pandas as pd


# -------------------------------------------------------------
# Generate random input dataset (same method as thread_bench.py)
# -------------------------------------------------------------
def generate_inputs(input_dir):
    os.makedirs(input_dir, exist_ok=True)
    vocab = [''.join(random.choices(string.ascii_lowercase, k=8)) for _ in range(1000)]
    for i in range(256):
        words = random.choices(vocab, k=1_000_000)
        text = ' '.join(words)
        with gzip.open(os.path.join(input_dir, f"file_{i:03d}.txt.gz"), "wt") as f:
            f.write(text)


# -------------------------------------------------------------
# Run final.py to generate wordcount outputs in each format
# -------------------------------------------------------------
def run_wordcount(input_dir, output_file):
    subprocess.run(
        ["python3.13", "final.py", input_dir, output_file, "8"],
        check=True
    )


# -------------------------------------------------------------
# Benchmark the read time for each format
# -------------------------------------------------------------
def benchmark_reads(outputs_dir):
    formats = ["csv", "parquet", "arrow"]
    results = []

    for fmt in formats:
        path = os.path.join(outputs_dir, f"output.{fmt}")
        start = time.perf_counter()

        if fmt == "csv":
            # Normal CSV read — all columns loaded
            table = csv.read_csv(path)
            total = pa.compute.sum(table["count"]).as_py()

        elif fmt == "parquet":
            # Selective column read for efficiency
            dataset = pq.ParquetFile(path)
            col = dataset.read(columns=["count"])
            total = pa.compute.sum(col["count"]).as_py()

        elif fmt == "arrow":
            # Memory-mapped read for Arrow (zero-copy)
            with pa.memory_map(path, "r") as source:
                table = feather.read_table(source)
                total = pa.compute.sum(table["count"]).as_py()

        elapsed = time.perf_counter() - start
        print(f"{fmt}: {elapsed:.4f}s (sum={total})")

        results.append({"format": fmt, "read_seconds": elapsed})

    return results


# -------------------------------------------------------------
# Create bar chart of results
# -------------------------------------------------------------
def make_plot(df, output_path):
    plt.figure(figsize=(6, 4))
    plt.bar(df["format"], df["read_seconds"] * 1000, color="steelblue")
    plt.title("Read Performance by File Format")
    plt.ylabel("Read Time (ms)")
    plt.xlabel("Format")
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")


# -------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 format_bench.py <output_directory>", file=sys.stderr)
        sys.exit(1)

    outputs_dir = sys.argv[1]
    os.makedirs(outputs_dir, exist_ok=True)

    # Step 1: Generate random gzipped input dataset
    input_dir = os.path.join(outputs_dir, "bench_inputs")
    generate_inputs(input_dir)

    # Step 2: Run wordcount for each format
    print("Running wordcount for CSV...")
    run_wordcount(input_dir, os.path.join(outputs_dir, "output.csv"))

    print("Running wordcount for Parquet...")
    run_wordcount(input_dir, os.path.join(outputs_dir, "output.parquet"))

    print("Running wordcount for Arrow...")
    run_wordcount(input_dir, os.path.join(outputs_dir, "output.arrow"))

    # Step 3: Benchmark the read performance
    print("\nBenchmarking read performance...")
    results = benchmark_reads(outputs_dir)

    # Step 4: Write CSV + plot
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(outputs_dir, "formats.csv"), index=False)
    make_plot(df, os.path.join(outputs_dir, "formats.svg"))

    print("\nBenchmark complete. Results:")
    print(df)


if __name__ == "__main__":
    main()

