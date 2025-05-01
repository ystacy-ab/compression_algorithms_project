import os
import time
import matplotlib.pyplot as plt

def lzw_compress(input_text):
    dictionary = {chr(i): i for i in range(256)}
    next_code = 256
    P = input_text[0]
    result = []

    for C in input_text[1:]:
        if P + C in dictionary:
            P = P + C
        else:
            result.append(dictionary[P])
            dictionary[P + C] = next_code
            next_code += 1
            P = C

    result.append(dictionary[P])
    return result

def lzw_decompress(compressed_codes):
    dictionary = {i: chr(i) for i in range(256)}
    next_code = 256
    OLD = compressed_codes[0]
    S = dictionary[OLD]
    result = S

    for NEW in compressed_codes[1:]:
        if NEW in dictionary:
            S = dictionary[NEW]
        else:
            S = dictionary[OLD] + C
        result += S
        C = S[0]
        dictionary[next_code] = dictionary[OLD] + C
        next_code += 1
        OLD = NEW

    return result

test_files = ["short.txt", "medium.txt", "large.txt"]

results = []

for filename in test_files:
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    original_size = len(text.encode("utf-8"))

    start_compress = time.time()
    compressed = lzw_compress(text)
    end_compress = time.time()

    compressed_size = len(compressed) * 2

    start_decompress = time.time()
    decompressed = lzw_decompress(compressed)
    end_decompress = time.time()

    info_loss = text != decompressed

    results.append({
        "file": filename,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compressed_size / original_size,
        "compression_time": end_compress - start_compress,
        "decompression_time": end_decompress - start_decompress,
        "info_loss": info_loss,
    })


print("{:<10} {:>15} {:>17} {:>20} {:>20} {:>20} {:>15}".format(
    "File", "Original Size", "Compressed Size", "Compression Ratio",
    "Compression Time", "Decompression Time", "Info Loss"
))
for res in results:
    print("{:<10} {:>15} {:>17} {:>20.2f} {:>20.6f} {:>20.6f} {:>15}".format(
        res["file"], res["original_size"], res["compressed_size"],
        res["compression_ratio"], res["compression_time"],
        res["decompression_time"], str(res["info_loss"])
    ))


file_labels = [res["file"] for res in results]
ratios = [res["compression_ratio"] for res in results]

plt.figure(figsize=(10, 6))
plt.bar(file_labels, ratios, color="skyblue")
plt.title("Ступінь стиснення (менше — краще)")
plt.ylabel("Стиснене / Оригінальне")
plt.xlabel("Файл")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
