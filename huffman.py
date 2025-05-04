"""hfn"""
import os
import pickle

class Node:
    """_summary_
    """
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

def build_frequency_dict(text):
    """_summary_

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    dct = {}
    for char in text:
        dct[char] = dct.get(char, 0) + 1
    return dct

def build_huffman_tree(freq):
    """_summary_

    Args:
        freq (_type_): _description_

    Returns:
        _type_: _description_
    """
    lst = [Node(char, freq) for char, freq in freq.items()]
    lst = sorted(lst, key=lambda node: node.freq)

    while len(lst) > 1:
        left = lst.pop(0)
        right = lst.pop(0)
        joined = Node(None, left.freq + right.freq)
        joined.left = left
        joined.right = right
        lst.append(joined)
        lst.sort(key=lambda node: node.freq)

    return lst[0] if lst else None

def build_codes(root):
    """_summary_

    Args:
        root (_type_): _description_

    Returns:
        _type_: _description_
    """
    codes = {}
    stack = [(root, "")]
    while stack:
        node, curr = stack.pop()
        if node is not None:
            if node.char is not None:
                codes[node.char] = curr
            else:
                stack.append((node.left, curr + "0"))
                stack.append((node.right, curr + "1"))
    return codes

def compress_file(filepath):
    """_summary_

    Args:
        filepath (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open(filepath, "rb") as f:
        data = f.read()

    freq_dict = build_frequency_dict(data)
    tree = build_huffman_tree(freq_dict)
    codes = build_codes(tree)

    encoded_bits = ''.join(codes[byte] for byte in data)
    padded_bits = encoded_bits + '0' * ((8 - len(encoded_bits) % 8) % 8)
    byte_array = bytearray(int(padded_bits[i:i+8], 2) for i in range(0, len(padded_bits), 8))

    output_path = os.path.splitext(filepath)[0] + ".huff"
    with open(output_path, "wb") as out:
        pickle.dump((byte_array, codes, len(encoded_bits)), out)
    return output_path

def decompress_file(filepath):
    """_summary_

    Args:
        filepath (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open(filepath, "rb") as f:
        byte_array, codes, bit_length = pickle.load(f)
    reversed_codes = {v: k for k, v in codes.items()}
    bit_string = ''.join(f"{byte:08b}" for byte in byte_array)
    bit_string = bit_string[:bit_length]
    curr = ""
    result = bytearray()
    for bit in bit_string:
        curr += bit
        if curr in reversed_codes:
            result.append(reversed_codes[curr])
            curr = ""
    output_path = os.path.splitext(filepath)[0] + "_decompressed.wav"
    with open(output_path, "wb") as out:
        out.write(result)

    return output_path
