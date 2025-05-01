"""huff"""
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
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    codes = build_codes(build_huffman_tree(build_frequency_dict(text)))

    encoded_text = ''.join(codes[char] for char in text)
    padded_text = encoded_text + '0' * ((8 - len(encoded_text) % 8) % 8)
    b = bytearray(int(padded_text[i:i+8], 2) for i in range(0, len(padded_text), 8))

    output_path = os.path.splitext(filepath)[0] + ".huff"
    with open(output_path, "wb") as out:
        pickle.dump((b, codes, len(encoded_text)), out)

    return output_path

def decompress_file(filepath):
    """_summary_

    Args:
        filepath (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open(filepath, "rb") as f:
        b, codes, enc_len = pickle.load(f)

    rev = {}
    for k, v in codes.items():
        rev[v] = k
    bitstr = ''.join(f"{byte:08b}" for byte in b)
    bitstr = bitstr[:enc_len]

    curr = ""
    result = ""
    for bit in bitstr:
        curr += bit
        if curr in rev:
            result += rev[curr]
            curr = ""

    output_path = os.path.splitext(filepath)[0] + "_decompressed.txt"
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(result)

    return output_path
