# Multi-Threaded Word Count System – AI-Assisted Concurrent Processing Project

A multi-threaded Python application that processes compressed text files, performs concurrent word counting, exports structured datasets in multiple formats, and benchmarks threading and storage performance across Python runtimes.

---

## Project Overview

This project explores:
- Concurrent programming
- Multi-threaded data processing
- AI-assisted software generation
- Performance benchmarking
- Data serialization formats

The system reads compressed `.txt.gz` files, counts word frequencies across files, and outputs results in:
- CSV
- Parquet
- Arrow

The project also compares:
- Different AI-generated implementations
- Python runtimes with and without the Global Interpreter Lock (GIL)
- File format read performance
- Thread scalability

---

## Features

- Built a multi-threaded word counting engine in Python
- Processed compressed `.txt.gz` datasets concurrently
- Implemented thread-safe shared data structures using locks
- Generated outputs in:
  - CSV
  - Parquet
  - Arrow
- Created automated benchmarking tools
- Compared GIL vs no-GIL Python runtimes
- Benchmarked storage format read performance
- Designed a pytest-based testing suite
- Used AI-assisted development with multiple Gemini models

---

## AI-Assisted Development

Generated and evaluated implementations using:
- Gemini 2.5 Pro
- Gemini 2.5 Flash
- Gemini 2.5 Flash-Lite

Workflow included:
- Writing detailed implementation specifications
- Generating code with Aider
- Comparing AI-generated solutions
- Identifying bugs and validating correctness
- Benchmarking implementation quality

---

## Word Counting Application

### Program Usage

```bash id="jlwmj2"
python3 PROGRAM_NAME <input_directory> <output_file> <threads>
