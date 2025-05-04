import numpy as np
from collections import Counter
import heapq
from PIL import Image
import os
import pickle
from datetime import datetime
import matplotlib.pyplot as plt

class HuffmanNode:
    def __init__(self, symbol, freq):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequencies):
    heap = [HuffmanNode(symbol, freq) for symbol, freq in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)
    return heap[0]

def generate_huffman_codes(root, current_code="", codes=None):
    if codes is None:
        codes = {}
    if root is None:
        return
    if root.symbol is not None:
        codes[root.symbol] = current_code or "0"
    generate_huffman_codes(root.left, current_code + "0", codes)
    generate_huffman_codes(root.right, current_code + "1", codes)
    return codes

def rle_encode(pixels):
    encoded = []
    count = 1
    current = pixels[0]
    for pixel in pixels[1:]:
        if pixel == current and count < 255:
            count += 1
        else:
            encoded.append((current, count))
            current = pixel
            count = 1
    encoded.append((current, count))
    return encoded

def compress_image(image_path, output_path):
    img = Image.open(image_path).convert('L')
    pixels = np.array(img).flatten()
    rle_data = rle_encode(pixels)
    symbols = [(pixel, run) for pixel, run in rle_data]
    frequencies = Counter(symbols)
    huffman_tree = build_huffman_tree(frequencies)
    huffman_codes = generate_huffman_codes(huffman_tree)
    compressed_data = ""
    for symbol in symbols:
        compressed_data += huffman_codes[symbol]
    with open(output_path, 'wb') as f:
        pickle.dump(huffman_codes, f)
        packed_data = int(compressed_data, 2).to_bytes((len(compressed_data) + 7) // 8, 'big')
        f.write(packed_data)

    return len(packed_data)

def show_results(input_image, output_file, output=False):
    start = datetime.now()
    compress_image(input_image, output_file)
    end = datetime.now()
    start_size = os.path.getsize(input_image)
    end_size = os.path.getsize(output_file)
    if output:
        print(start_size)
        print(end_size)
        print(f'Time: {end - start}')
    return (start_size, end_size)

show_results('test_image.bmp', 'compressed.png')

def statistics(file_pairs):
    file_names = []
    original_sizes = []
    compressed_sizes = []
    compression_times = []

    for original, compressed in file_pairs:
        start_time = datetime.now()
        compressed_size = compress_image(original, compressed)
        end_time = datetime.now()
        file_names.append(os.path.basename(original))
        original_sizes.append(os.path.getsize(original))
        compressed_sizes.append(compressed_size)
        compression_times.append((end_time - start_time).total_seconds())
    plt.figure(figsize=(14, 7))
    bar_width = 0.35
    indices = np.arange(len(file_names))

    bars1 = plt.bar(indices - bar_width/2, original_sizes, bar_width, 
                   label='Оригінальний розмір', color='#1f77b4')
    bars2 = plt.bar(indices + bar_width/2, compressed_sizes, bar_width, 
                   label='Стиснутий розмір', color='#ff7f0e')

    plt.xlabel('Файли')
    plt.ylabel('Розмір (байти)')
    plt.title('Порівняння розмірів файлів до та після стиснення')
    plt.xticks(indices, file_names, rotation=45, ha='right')
    plt.legend()

    for i in range(len(file_names)):
        plt.text(i - bar_width/2, original_sizes[i] + 100, 
                f'{original_sizes[i]}\n({compression_times[i]:.2f} сек)', 
                ha='center', va='bottom', fontsize=8)
        plt.text(i + bar_width/2, compressed_sizes[i] + 100, 
                f'{compressed_sizes[i]}\n({compressed_sizes[i]/original_sizes[i]*100:.1f}%)', 
                ha='center', va='bottom', fontsize=8)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    print("\nЗагальна статистика:")
    for i in range(len(file_names)):
        print(f"\nФайл: {file_names[i]}")
        print(f"Оригінальний розмір: {original_sizes[i]} байт")
        print(f"Стиснутий розмір: {compressed_sizes[i]} байт")
        print(f"Коефіцієнт стиснення: {compressed_sizes[i]/original_sizes[i]*100:.1f}%")
        print(f"Час стиснення: {compression_times[i]:.2f} секунд")
    plt.show()

statistics([('test_image.bmp', 'a_compressed.png'),
            ('250-251.jpg', '250-251-compressed.png')])
