import sys
from tools import read_file, write_file, ASCII_NUM, get_index_from_char, get_char_from_index
from ukkonen_algo import SuffixTree
import heapq
from bitarray import bitarray


class HuffmanNode:
    def __init__(self, frequency, data):
        self.freq = frequency
        self.data = data
        self.left = None

        self.right = None

    def __lt__(self, other_node):
        return self.freq < other_node.freq

    def __add__(self, other_node):
        if not isinstance(other_node, HuffmanNode):
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other_node).__name__}'")

        added_freq = self.freq + other_node.freq
        added_data = self.data + other_node.data

        new_combined_node = HuffmanNode(added_freq, added_data)

        new_combined_node.left = self
        new_combined_node.right = other_node

        return new_combined_node


class HuffmanCode:
    def __init__(self, freq_arr):
        self.freq_arr = freq_arr
        self.letters_encoding = [None] * ASCII_NUM
        self.get_letters_encoding()

    def get_freq_heap(self):
        freq_heap = []
        for index, freq in enumerate(self.freq_arr):
            if freq:
                # push the tuple with following info : freq, character, is leaf
                heapq.heappush(
                    freq_heap, HuffmanNode(freq, get_char_from_index(index)))

        return freq_heap

    def build_tree(self):
        freq_heap = self.get_freq_heap()

        while len(freq_heap) > 1:
            first = heapq.heappop(freq_heap)
            second = heapq.heappop(freq_heap)

            combined = first + second

            heapq.heappush(freq_heap, combined)

        return freq_heap[0]

    def get_letters_encoding(self, node=None, bitstring=""):
        if not node:
            node = self.build_tree()

        if node.left:
            self.get_letters_encoding(node.left, bitstring + "0")

        if node.right:
            self.get_letters_encoding(node.right, bitstring + "1")

        if not node.left and not node.right:
            leaf_char = node.data
            self.letters_encoding[get_index_from_char(
                leaf_char)] = bitarray(bitstring)

    def encode(self, char):
        return self.letters_encoding[get_index_from_char(char)]

    def decode(self, binary):
        pass


class EliasCode:
    def __init__(self, length=0) -> None:
        self.length = length
        self.encoded_num = [None] * length

        self.decoded_num = {}

    def encode(self, num):
        if self.encoded_num[num - 1]:

            return self.encoded_num[num - 1]

        encoded_bin = decimal_to_binary(num)

        final_encoded_bin = encoded_bin

        while len(encoded_bin) > 1:
            length_comp = len(encoded_bin) - 1
            encoded_bin = decimal_to_binary(length_comp)
            encoded_bin[0] = 0

            final_encoded_bin = encoded_bin + final_encoded_bin

        self.encoded_num[num - 1] = final_encoded_bin

        return final_encoded_bin

    def decode(self, binary):
        pass


class RunlengthEncoder:
    def __init__(self, string) -> None:
        self.length = len(string)
        self.bwt_string = self.get_bwt(string)
        self.unique_char_arr, self.freq_arr = self.get_freq_arr()
        self.huffman = HuffmanCode(self.freq_arr)
        self.elias = EliasCode(self.length)

    def get_bwt(self, string):
        suffix_tree = SuffixTree(string)
        suffix_arr = suffix_tree.get_suffix_array()

        return "".join([string[(suffix-1) % self.length] for suffix in suffix_arr])

    def get_freq_arr(self):
        freq_arr = [0] * ASCII_NUM
        unique_char_arr = []
        for char in self.bwt_string:
            if not freq_arr[get_index_from_char(char)]:
                unique_char_arr.append(char)
            freq_arr[get_index_from_char(char)] += 1

        return unique_char_arr, freq_arr

    def encode_runlength(self, char, char_count):
        encoded_char = self.huffman.encode(char)
        encoded_char_count = self.elias.encode(char_count)
        return encoded_char + encoded_char_count

    def encode(self):
        encoded_length = self.elias.encode(self.length)

        final_encoded_bin = encoded_length.copy()

        encoded_uniq_chars = self.elias.encode(len(self.unique_char_arr))

        final_encoded_bin += encoded_uniq_chars

        for char in self.unique_char_arr:
            # get ascii binary (7 bit)
            ascii_binary = decimal_to_binary(ord(char))
            ascii_binary = bitarray(
                "0") * (7 - len(ascii_binary)) + ascii_binary

            char_huffman_encode = self.huffman.encode(char)
            code_len_encode = self.elias.encode(len(char_huffman_encode))

            final_encoded_bin += ascii_binary + code_len_encode + char_huffman_encode

        current_char = self.bwt_string[0]
        current_char_count = 1

        for index in range(1, len(self.bwt_string)):

            if self.bwt_string[index] == current_char:
                current_char_count += 1

            else:

                final_encoded_bin += self.encode_runlength(
                    current_char, current_char_count)
                current_char = self.bwt_string[index]
                current_char_count = 1

        final_encoded_bin += self.encode_runlength(
            current_char, current_char_count)

        final_encoded_bin += bitarray("0") * (-len(final_encoded_bin) % 8)
        return final_encoded_bin


class RunlengthDecoder:
    def __init__(self, binary):
        self.binary = binary

    def decode(self):
        pass


def decimal_to_binary(num):
    binary = ""

    while num > 0:
        remainder = num % 2
        binary = str(remainder) + binary
        num //= 2

    return bitarray(binary)


if __name__ == "__main__":
    text = "banana$"
    encoder = RunlengthEncoder(text)
    huff = encoder.huffman
    print(encoder.encode())
