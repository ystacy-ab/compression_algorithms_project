import wave
from wave import Wave_write, Wave_read
import os
import time
import matplotlib.pyplot as plt
import array

def read_wav_file(filename: str) -> tuple[bytes, Wave_read] | None:
    """
    Reads a WAV file, returning its audio data and parameters.
    """
    if not os.path.exists(filename):
        print(f"Error: File named '{filename}' was not found.")
        return None, None
    try:
        with wave.open(filename, "rb") as wav:
            audio_params = wav.getparams()
            frames = wav.readframes(audio_params.nframes)
            return frames, audio_params
    except wave.Error as e:
        print(f"Error while reading file named '{filename}': {e}")
        return None, None
    except EOFError:
        print(f"Unexpected outcome while reading file named \
'{filename}'. The file might have been damaged.")
        return None, None

def write_wav_file(filename: str, audio_params, frames: bytes) -> None:
    """
    Writes audio data to a WAV file.
    """
    with wave.open(filename, "wb") as wav:
        wav: Wave_write
        wav.setparams(audio_params)
        wav.writeframes(frames)

def lzw_encode(data: bytes) -> list[int]:
    """
    Encodes the given byte data using LZW.
    """
    table = {bytes([i]): i for i in range(256)} # початковий словник, де кожен елемент - 1 байт.
    next_code = 256
    P = bytes([data[0]])
    result = []

    for byte in data[1:]:
        C = bytes([byte])
        if P + C in table:
            P = P + C
        else:
            result.append(table[P])
            table[P + C] = next_code
            next_code += 1
            P = C

    result.append(table[P])
    return result

def lzw_decode(codes: list[int]) -> bytes:
    """
    Decodes the given byte data using LZW.
    """
    table = {i: bytes([i]) for i in range(256)}
    next_code = 256
    OLD = codes[0]
    S = table[OLD]
    result = bytearray(S)
    C = S[:1]

    for NEW in codes[1:]:
        if NEW not in table:
            S = table[OLD] + C
        else:
            S = table[NEW]
        result += S
        C = S[:1]
        table[next_code] = table[OLD] + C
        next_code += 1
        OLD = NEW

    return bytes(result)

def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Calculates the compression ratio between the original and compressed file sizes.
    """
    return original_size / compressed_size if compressed_size != 0 else 0

def calculate_file_size(filename: str) -> int:
    """
    Calculates the size of a file.
    """
    return os.path.getsize(filename)

def check_loss(original: bytes, decoded: bytes) -> bool:
    """
    Checks if there is any loss of data during compression and decompression.
    """
    return original != decoded

# Логіка для аудіо
audio_data, wav_audio_params = read_wav_file("Charli xcx - Mean girls featuring julian casablancas (audio).wav")
original_size = len(audio_data)

# Стиснення
start_compress = time.time()
compressed_codes = lzw_encode(audio_data)
end_compress = time.time()
compression_time = end_compress - start_compress

# Запис стисненого у бінарному вигляді
with open("compressed.lzw", "wb") as file:
    arr = array.array('I', compressed_codes)
    arr.tofile(file)

compressed_size = calculate_file_size("compressed.lzw")

# Розпакування
start_decompress = time.time()
with open("compressed.lzw", "rb") as file:
    arr = array.array('I')
    arr.fromfile(file, compressed_size // arr.itemsize)
    codes = arr.tolist()

decoded_audio = lzw_decode(codes)
end_decompress = time.time()
decompression_time = end_decompress - start_decompress

# Запис декодованого звуку
write_wav_file("output.wav", wav_audio_params, decoded_audio)

# Аналіз
compression_ratio = calculate_compression_ratio(original_size, compressed_size)
is_lossy = check_loss(audio_data, decoded_audio)

print(f"Original size (bytes): {original_size}")
print(f"Compressed size (bytes): {compressed_size}")
print(f"Compression time: {compression_time:.4f} seconds")
print(f"Decompression time: {decompression_time:.4f} seconds")
print(f"Lossy compression: {'Yes' if is_lossy else 'No'}")

# Графік
percentage = compressed_size / original_size * 100
labels = ['Оригінал', 'Стиснений']
values = [1.0, compressed_size / original_size]
percentages = [100.0, percentage]

plt.bar(labels, values, color=['gray', 'skyblue'])
plt.ylabel('Ступінь стиснення')
plt.title('Порівняння з Оригіналом')

for i, val in enumerate(values):
    plt.text(i, val + 0.02, f"{percentages[i]:.1f}%", \
ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.ylim(0, 1.2)
plt.show()

# Cтиснення тексту
def lzw_compress(input_text: str) -> list[int]:
    """
    Encodes the given data using LZW.
    """
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

def lzw_decompress(codes: list[int]) -> str:
    """
    Decodes the given data using LZW.
    """
    dictionary = {i: chr(i) for i in range(256)}
    next_code = 256
    OLD = codes[0]
    S = dictionary[OLD]
    result = S
    C = S[0]

    for NEW in codes[1:]:
        if NEW not in dictionary:
            S = dictionary[OLD] + C
        else:
            S = dictionary[NEW]
        result += S
        C = S[0]
        dictionary[next_code] = dictionary[OLD] + C
        next_code += 1
        OLD = NEW

    return result

test_files = ["short.txt", "medium.txt", "large.txt"]

results = []

# Аналіз
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
        "compression_ratio": original_size / compressed_size, #має бути > 1
        "compression_time": end_compress - start_compress,
        "decompression_time": end_decompress - start_decompress,
        "info_loss": info_loss,
    })

# Результат
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

# Графік
plt.figure(figsize=(10, 6))
plt.bar(file_labels, ratios, color="skyblue")
plt.title("Ступінь стиснення")
plt.ylabel("Стиснене")
plt.xlabel("Файл")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()  
