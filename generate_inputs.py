import os
import gzip
import random
import string

def generate_random_text(word_count=1000, sentence_length=15):
    """Generates random text suitable for word counting."""
    words = []
    for _ in range(word_count):
        word_len = random.randint(3, 10)
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(word_len))
        words.append(word)

    text_lines = []
    current_sentence_words = []
    for i, word in enumerate(words):
        current_sentence_words.append(word)
        if (i + 1) % sentence_length == 0 or i == word_count - 1:
            text_lines.append(' '.join(current_sentence_words).capitalize() + '.')
            current_sentence_words = []
    return '\n'.join(text_lines)

def main():
    """Generates sample compressed text files in the inputs/ directory."""
    input_dir = 'inputs'
    os.makedirs(input_dir, exist_ok=True)

    file_names = ['sample_01.txt.gz', 'sample_02.txt.gz', 'sample_03.txt.gz']
    for i, filename in enumerate(file_names):
        filepath = os.path.join(input_dir, filename)
        content = generate_random_text(word_count=1000 * (i + 1))
        with gzip.open(filepath, 'wt', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filepath} with {len(content.split())} words.")

    print(f"\nSample compressed text files generated in '{input_dir}/' directory.")

if __name__ == "__main__":
    main()
