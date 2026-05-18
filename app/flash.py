import sys, gzip, os, collections

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 flash.py <input_dir> <output_file> <threads>")
        return

    input_dir, output_file, threads = sys.argv[1], sys.argv[2], int(sys.argv[3])
    counts = collections.Counter()

    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.endswith(".txt.gz"):
                with gzip.open(os.path.join(root, f), 'rt', encoding='utf-8', errors='ignore') as fh:
                    for line in fh:
                        counts.update(line.lower().split())

    with open(output_file, 'w') as out:
        out.write("word,count\n")
        for w, c in counts.items():
            out.write(f"{w},{c}\n")

if __name__ == "__main__":
    main()
