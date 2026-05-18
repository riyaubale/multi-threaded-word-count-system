import os
import gzip
import csv
import subprocess
import pytest
import pyarrow.parquet as pq
import pyarrow.feather as feather

PROGRAM = os.environ.get("PROGRAM")

# Skip all tests if PROGRAM not provided
if not PROGRAM:
    pytest.skip("Environment variable PROGRAM not set.", allow_module_level=True)

# ---------------------------------------------------------------------
# Helper: create temporary gzipped text files
# ---------------------------------------------------------------------
def create_gzipped_temp_files(tmp_path, files_data):
    """
    Creates gzipped text files in a temporary directory.
    files_data: dict of {filename: content}
    Returns the input directory path as string.
    """
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    for filename, content in files_data.items():
        path = input_dir / f"{filename}.txt.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            f.write(content)
    return str(input_dir)


# ---------------------------------------------------------------------
# 1. Basic correctness tests across formats (parameterized)
# ---------------------------------------------------------------------
@pytest.mark.parametrize("ext", [".csv", ".parquet", ".feather"])
def test_basic_wordcount_formats(tmp_path, ext):
    """Check that program counts words correctly and outputs valid formats."""
    files_data = {"f1": "hello world hello", "f2": "world test"}
    input_dir = create_gzipped_temp_files(tmp_path, files_data)
    output_file = tmp_path / f"output{ext}"

    subprocess.run(
        ["python3.13", PROGRAM, input_dir, str(output_file), "2"],
        check=True,
    )

    # Read the output and verify counts
    if ext == ".csv":
        with open(output_file, newline="") as f:
            rows = list(csv.DictReader(f))
        words = {r["word"]: int(float(r["count"])) for r in rows}
    elif ext == ".parquet":
        tbl = pq.read_table(output_file)
        words = dict(zip(tbl["word"].to_pylist(), tbl["count"].to_pylist()))
    else:
        tbl = feather.read_table(output_file)
        words = dict(zip(tbl["word"].to_pylist(), tbl["count"].to_pylist()))

    assert words.get("hello", 0) == 2, "hello should appear twice"
    assert words.get("world", 0) == 2, "world should appear twice"
    assert words.get("test", 0) == 1, "test should appear once"
    assert os.path.exists(output_file)


# ---------------------------------------------------------------------
# 2. Empty input directory
# ---------------------------------------------------------------------
def test_empty_input_directory(tmp_path):
    """Program should exit gracefully when input dir is empty."""
    input_dir = tmp_path / "empty_inputs"
    input_dir.mkdir()
    output_file = tmp_path / "empty.csv"

    result = subprocess.run(
        ["python3.13", PROGRAM, str(input_dir), str(output_file), "2"],
        capture_output=True,
        text=True,
    )

    assert "No .txt.gz files found" in result.stderr or "No .txt.gz files found" in result.stdout
    assert result.returncode in (0, 1)
    assert not output_file.exists(), "No output file should be created for empty input"


# ---------------------------------------------------------------------
# 3. Invalid argument handling
# ---------------------------------------------------------------------
def test_invalid_args(tmp_path):
    """Program should print usage and exit nonzero on missing args."""
    result = subprocess.run(["python3.13", PROGRAM], capture_output=True, text=True)
    assert "Usage:" in result.stderr or "Usage:" in result.stdout
    assert result.returncode != 0


# ---------------------------------------------------------------------
# 4. Thread count consistency
# ---------------------------------------------------------------------
def test_thread_consistency(tmp_path):
    """Running with 1 vs multiple threads should yield identical results."""
    files_data = {"f": "one two three two one"}
    input_dir = create_gzipped_temp_files(tmp_path, files_data)

    out1 = tmp_path / "out1.csv"
    out4 = tmp_path / "out4.csv"

    subprocess.run(["python3.13", PROGRAM, input_dir, str(out1), "1"], check=True)
    subprocess.run(["python3.13", PROGRAM, input_dir, str(out4), "4"], check=True)

    with open(out1, newline="") as f1, open(out4, newline="") as f4:
        c1 = {r["word"]: int(float(r["count"])) for r in csv.DictReader(f1)}
        c4 = {r["word"]: int(float(r["count"])) for r in csv.DictReader(f4)}

    assert c1 == c4, "Results should be identical regardless of thread count"


# ---------------------------------------------------------------------
# 5. Punctuation and case normalization (if implementation supports it)
# ---------------------------------------------------------------------
def test_case_and_punctuation(tmp_path):
    """Checks case insensitivity and punctuation behavior."""
    files_data = {"f": "Word, word! WORD? another-word"}
    input_dir = create_gzipped_temp_files(tmp_path, files_data)
    output_file = tmp_path / "case.csv"

    subprocess.run(["python3.13", PROGRAM, input_dir, str(output_file), "2"], check=True)

    with open(output_file, newline="") as f:
        rows = list(csv.DictReader(f))
    words = [r["word"] for r in rows]

    total_word_count = sum(
        int(float(r["count"])) for r in rows if r["word"].startswith("word")
    )
    assert total_word_count >= 3, "Total 'word' variants should sum to at least 3"


# ---------------------------------------------------------------------
# 6. Verify output columns exist
# ---------------------------------------------------------------------
def test_output_columns_exist(tmp_path):
    """Output must contain 'word' and 'count' columns."""
    files_data = {"doc": "alpha beta alpha"}
    input_dir = create_gzipped_temp_files(tmp_path, files_data)
    output_file = tmp_path / "cols.csv"

    subprocess.run(["python3.13", PROGRAM, input_dir, str(output_file), "2"], check=True)

    with open(output_file, newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

    assert "word" in header and "count" in header, "Required columns missing"

