Create a multithreaded word counting program in Python. To invoke the program, do this: 
python3 PROGRAM_NAME <input_directory> <output_file> <threads>

The arguments will be as follows:
<input_directory> will be a directory containing the .txt.gz compressed text files.
<output_file> is the output file path (CSV, Parquet, or Arrow based on extension)
<threads> is the number of worker threads to use

This is what the program should do: 
It will first find all the .txt.gz files from the input directory. E
ach file will be processed by 1 thread and print these messages when before processing and after finishing: start <filename>” and “finish <filename>”.
Then count the word occurrences, per file and also overall. Make sure ignore case. While processing, keep in mind that words are separated by whitespace and don't worry about punctuation. 
To store the count, use a dictionary and counters. If there's a missing argument or missing anything, handle that.

The output table should be as follows:
Columns
First column: word (the word as a string)
Second column: count (total count across all files)
Remaining columns: one column per input file with counts from that file.  The column name should be the filename (the directory containing the file should NOT be part of the column name).
For example, if the input directory has file1.gz, file2.gz, file3.gz, the output has columns: word, count, file1.gz, file2.gz, file3.gz.

How to deal with concurrency:
Use a lock to protect the updates within the shared data structures. Basically, while the threads are reading or counting the words, do that locally, OR when there is I/O happening, and then only use the lock to get the results. Also while reading the file, don't hold a lock. Also include a main thread that will start all the other worker threads, wait for them to finish and will write their results after finishing.
