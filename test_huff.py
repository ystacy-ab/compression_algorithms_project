import os
import time
import matplotlib.pyplot as plt
from huffman import compress_file, decompress_file

def get_file_size(filepath):
    return os.path.getsize(filepath)

def visualize(filepaths):
    file_names = [os.path.basename(f) for f in filepaths]
    compress_times = []
    decompress_times = []
    original_sizes = []
    compressed_sizes = []
    decompressed_sizes = []

    for filepath in filepaths:
        original_sizes.append(get_file_size(filepath))

        start_compress = time.time()
        compressed_path = compress_file(filepath)
        compress_times.append(time.time() - start_compress)
        compressed_sizes.append(get_file_size(compressed_path))

        start_decompress = time.time()
        decompressed_path = decompress_file(compressed_path)
        decompress_times.append(time.time() - start_decompress)
        decompressed_sizes.append(get_file_size(decompressed_path))

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    x = range(len(filepaths))
    width = 0.25
    plt.bar([i - width for i in x], original_sizes, width=width, label='Original', color='skyblue')
    plt.bar(x, compressed_sizes, width=width, label='Compressed', color='orange')
    plt.bar([i + width for i in x], decompressed_sizes, width=width, label='Decompressed', color='lightgreen')
    plt.xticks(x, file_names, rotation=45)
    plt.title('File Sizes (bytes)')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(file_names, compress_times, marker='o', label='Compress Time', color='skyblue')
    plt.plot(file_names, decompress_times, marker='o', label='Decompress Time', color='lightgreen')
    plt.title('Execution Time (seconds)')
    plt.xlabel('File')
    plt.ylabel('Time (s)')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize(["hello.txt", "gl.txt", "hf.txt"])
