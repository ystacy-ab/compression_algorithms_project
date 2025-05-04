import os
import time
import pickle
import matplotlib.pyplot as plt

def lz77_compress(input_data, window_size=20):
    """Compress input data using the LZ77 algorithm."""
    i = 0
    compressed = []
    window = b""
    input_bytes = bytes(input_data) if not isinstance(input_data, bytes) else input_data
    while i < len(input_bytes):
        distance = 0
        length = 0
        lookahead_buffer = input_bytes[i:]
        for j in range(1, len(lookahead_buffer) + 1):
            substring = lookahead_buffer[:j]
            pos = window.rfind(substring)
            if pos != -1:
                distance = len(window) - pos
                length = j
            else:
                break
        if length > 0:
            next_char = lookahead_buffer[length:length+1] if i + length < len(input_bytes) else b''
        else:
            next_char = input_bytes[i:i+1]
        compressed.append((distance, length, next_char))
        shift = length + 1
        window += input_bytes[i:i+shift]
        if len(window) > window_size:
            window = window[-window_size:]
        i += shift
    return compressed

def lz77_decompress(compressed):
    """Decompress LZ77-compressed data."""
    result = bytearray()
    for distance, length, char_bytes in compressed:
        if distance == 0 and length == 0:
            result.extend(char_bytes)
        else:
            start = len(result) - distance
            for i in range(length):
                result.append(result[start + i])
            result.extend(char_bytes)
    return bytes(result)

def get_compressed_size(compressed_data):
    """Return the byte size of compressed data."""
    size = 0
    for distance, length, _ in compressed_data:
        distance_size = 1 if distance < 256 else 2 if distance < 65536 else 4
        length_size = 1 if length < 256 else 2 if length < 65536 else 4
        char_size = 1
        size += distance_size + length_size + char_size
    return size

def process_text_file(file_path, window_size):
    """Compress and decompress a text file, returning stats."""
    with open(file_path, 'r', encoding='utf-8') as file:
        input_string = file.read()
    original_size = len(input_string.encode('utf-8'))
    start_time = time.time()
    compressed_data = lz77_compress(input_string.encode('utf-8'), window_size)
    compression_time = time.time() - start_time
    compressed_size = get_compressed_size(compressed_data)
    start_time = time.time()
    decompressed_bytes = lz77_decompress(compressed_data)
    decompression_time = time.time() - start_time
    decompressed_string = decompressed_bytes.decode('utf-8')
    assert decompressed_string == input_string, "Decompression did not restore the original"
    ratio = original_size / compressed_size if compressed_size != 0 else float('inf')
    compressed_file_path = file_path.replace('.txt', '_compressed.bin')
    with open(compressed_file_path, 'wb') as f:
        pickle.dump(compressed_data, f)
    decompressed_file_path = file_path.replace('.txt', '_decompressed.txt')
    with open(decompressed_file_path, 'w', encoding='utf-8') as f:
        f.write(decompressed_string)
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_time': compression_time,
        'decompression_time': decompression_time,
        'compression_ratio': ratio,
        'compressed_file': compressed_file_path,
        'decompressed_file': decompressed_file_path
    }

def process_video_file(file_path, window_size):
    """Compress and decompress a video file, returning stats."""
    with open(file_path, 'rb') as file:
        data = file.read()
    original_size = len(data)
    start_time = time.time()
    compressed_data = lz77_compress(data, window_size)
    compression_time = time.time() - start_time
    compressed_size = get_compressed_size(compressed_data)
    start_time = time.time()
    decompressed_data = lz77_decompress(compressed_data)
    decompression_time = time.time() - start_time
    assert decompressed_data == data, "Decompression did not restore the original"
    ratio = original_size / compressed_size if compressed_size != 0 else float('inf')
    compressed_file_path = file_path.replace('.mp4', '_compressed.bin')
    with open(compressed_file_path, 'wb') as f:
        pickle.dump(compressed_data, f)
    decompressed_file_path = file_path.replace('.mp4', '_decompressed.mp4')
    with open(decompressed_file_path, 'wb') as f:
        f.write(decompressed_data)
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_time': compression_time,
        'decompression_time': decompression_time,
        'compression_ratio': ratio,
        'compressed_file': compressed_file_path,
        'decompressed_file': decompressed_file_path
    }

def compare_files(files, window_size=10000):
    """Compare compression stats across files and show plots."""
    original_sizes = []
    compressed_sizes = []
    compression_ratios = []
    labels = []
    for file_path in files:
        print(f"\nProcessing: {file_path}")
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.txt':
            stats = process_text_file(file_path, window_size)
        elif ext == '.mp4':
            stats = process_video_file(file_path, window_size)
        else:
            print(f"Skipped (unsupported): {file_path}")
            continue
        labels.append(os.path.basename(file_path))
        original_sizes.append(stats['original_size'])
        compressed_sizes.append(stats['compressed_size'])
        percent_ratio = (stats['compressed_size'] / stats['original_size']) * 100
        compression_ratios.append(percent_ratio)
        print(f"Original size: {stats['original_size']} bytes")
        print(f"Compressed size: {stats['compressed_size']} bytes")
        print(f"Compression ratio: {percent_ratio:.2f}%")
        print(f"Compression time: {stats['compression_time']:.4f} s")
        print(f"Decompression time: {stats['decompression_time']:.4f} s")

    _, axes = plt.subplots(2, 1, figsize=(10, 10))
    x = list(range(len(labels)))
    axes[0].bar(x, original_sizes, width=0.4, label="Original", align='center', color='blue')
    axes[0].bar([i + 0.4 for i in x], compressed_sizes, width=0.4, label="Compressed", align='center', color='orange')
    axes[0].set_xticks([i + 0.2 for i in x])
    axes[0].set_xticklabels(labels, rotation=45)
    axes[0].set_ylabel("Size (bytes)")
    axes[0].set_title("File Sizes")
    axes[0].legend()
    axes[1].bar(x, compression_ratios, width=0.6, color='grey')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=45)
    axes[1].set_ylabel("Compressed size (% of original)")
    axes[1].set_title("Compression Efficiency (lower is better)")
    axes[1].axhline(100, color='red', linestyle='--', linewidth=1, label='Original size (100%)')
    axes[1].legend()


    plt.tight_layout()
    plt.show()

files = [
    'input_text1.txt',
    'input_text2.txt',
    'small_video.mp4'
]
compare_files(files)