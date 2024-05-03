from tools import ASCII_NUM, get_index_from_char, get_char_from_index
from ukkonen_algo import SuffixTree
import heapq
from bitarray import bitarray


class HuffmanNode:
    """
    Represents a node in a Huffman tree

    Attributes:
        freq (int): The frequency of the character or combined frequencies of child nodes
        data (str): The character or combined characters of child nodes
        left (HuffmanNode): The left child node
        right (HuffmanNode): The right child node
    """

    def __init__(self, frequency: int, data: str) -> None:
        self.freq = frequency
        self.data = data
        self.left = None

        self.right = None

    def __lt__(self, other_node):
        """
        Compares two HuffmanNode objects based on their frequencies

        Parameters:
            other_node (HuffmanNode): Another HuffmanNode object

        Returns:
            bool: True if the frequency of this node is less than the frequency of the other node, False otherwise
        """
        return self.freq < other_node.freq

    def __add__(self, other_node):
        """
        Adds two HuffmanNode objects together to create a new combined node

        Parameters:
            other_node (HuffmanNode): Another HuffmanNode object

        Returns:
            HuffmanNode: A new HuffmanNode representing the combined frequencies and characters of the two input nodes

        Raises:
            TypeError: If the other node is not a HuffmanNode object
        """

        # Check if other node is an object of huffman node, if not raise type error
        if not isinstance(other_node, HuffmanNode):
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other_node).__name__}'")

        # Add freq and combine the strings to create a new combined node
        added_freq = self.freq + other_node.freq
        added_data = self.data + other_node.data

        new_combined_node = HuffmanNode(added_freq, added_data)

        # Set left and right to be self and the other node
        new_combined_node.left = self
        new_combined_node.right = other_node

        return new_combined_node


class HuffmanCode:
    """
    Represents a Huffman code encoder and decoder

    Attributes:
        freq_arr (list[int]): A fixed size list containing the frequencies of characters
        letters_encoding (list[bitarray]): A list containing the bitarray of Huffman encoding for each character
        decoding_table (dict[string, int]): A dictionary containing the decoding table for the Huffman code
    """

    def __init__(self, freq_arr: list[int] = None) -> None:

        # If freq_arr is passed in, means that its encoding
        if freq_arr:
            self.freq_arr = freq_arr
            self.letters_encoding = [None] * ASCII_NUM
            self.get_letters_encoding()

        else:
            self.decoding_table = {}

    def get_freq_heap(self) -> list[HuffmanNode]:
        """
        Builds a min-heap of Huffman nodes based on character frequencies

        Returns:
            list[HuffmanNode]: A min-heap containing Huffman nodes
        """
        freq_heap = []
        # loop each of the frequencies in the freq arr, and check if there's a valid freq
        for index, freq in enumerate(self.freq_arr):
            if freq:
                # push new HuffmanNode with freq and char into the min heap
                heapq.heappush(
                    freq_heap, HuffmanNode(freq, get_char_from_index(index)))

        return freq_heap

    def build_tree(self) -> HuffmanNode:
        """
        Builds the Huffman tree based on character frequencies by combining first two elements
        in the min heap

        Returns:
            HuffmanNode: The root node of the Huffman tree
        """
        # Get the base frequency heap
        freq_heap = self.get_freq_heap()

        # Loop until frequency heap length reaches 1
        while len(freq_heap) > 1:
            # Pop the first 2 least frequent element and combine them
            first = heapq.heappop(freq_heap)
            second = heapq.heappop(freq_heap)

            combined = first + second
            # Push back into the heap
            heapq.heappush(freq_heap, combined)

        # Return the top element (Root)
        return freq_heap[0]

    def get_letters_encoding(self, node: HuffmanNode = None, bitstring: str = ""):
        """
        Recursively generates Huffman encoding for each character by traversing
        down the binary Huffman tree

        Parameters:
            node (Node): The current node in the Huffman tree.
            bitstring (str): The bit string representing the encoding path.

        """
        # If theres no node being passed in the build the huffman encoding tree
        if not node:
            node = self.build_tree()

        # If left node exists then traverse left while adding 0 to the bitstring
        if node.left:
            self.get_letters_encoding(node.left, bitstring + "0")

        # If right node exists then traverse right while adding 1 to bitstring
        if node.right:
            self.get_letters_encoding(node.right, bitstring + "1")

        # If node is a leaf then add to letters encoding list with bitstring converted to bitarray
        if not node.left and not node.right:
            leaf_char = node.data
            self.letters_encoding[get_index_from_char(
                leaf_char)] = bitarray(bitstring)

    def encode(self, char: str) -> bitarray:
        """
        Encodes a character using the Huffman encoding by looking at the precomputed encoding table

        Parameters:
            char (str): The character to encode

        Returns:
            bitarray: The Huffman encoding for the character in bits
        """
        return self.letters_encoding[get_index_from_char(char)]

    def add_to_decoder_table(self, binary: str, char: str) -> None:
        """
        Adds an entry to the decoding table

        Parameters:
            binary (str): The Huffman binary code
            char (str): The corresponding character
        """
        # Add binary as key and char as value into the decoding table
        self.decoding_table[binary] = char


class EliasCode:
    """
    Represents an Elias Code encoder and decoder

    Attributes:
        length (int): The length of the encoded numbers cache
        encoded_num (list): A cache to store previously encoded numbers
    """

    def __init__(self, length=0) -> None:
        # If length is valid (> 0) then set length and setup memo
        if length:
            self.length = length
            self.encoded_num = [None] * length

    def encode(self, num: int) -> bitarray:
        """
        Encodes a number using Elias omega coding.

        Parameters:
            num (int): The number to encode

        Returns:
            bitarray: The Elias omega encoded representation of the number in bits
        """
        # If the number has previously been encoded then just return it back
        if self.encoded_num[num - 1]:
            return self.encoded_num[num - 1]

        # Convert num into minimal binary representation
        encoded_bin = decimal_to_binary(num)
        # Set it to the final encoded binary
        final_encoded_bin = encoded_bin

        # Loop until length of encoded binary is 1
        while len(encoded_bin) > 1:
            # Encode the length and change first bit in length component to 0
            length_comp = len(encoded_bin) - 1
            encoded_bin = decimal_to_binary(length_comp)
            encoded_bin[0] = 0

            # Add to final encoded binary
            final_encoded_bin = encoded_bin + final_encoded_bin

        # Add result to the cache for later use
        self.encoded_num[num - 1] = final_encoded_bin

        return final_encoded_bin

    def decode(self, binary: bitarray) -> tuple[bitarray, int]:
        """
        Decodes a sequence of bitarray using Elias Omega coding

        The decoding function will stop once it reaches a number component
        regardless of the length of the bitarray given

        Parameters:
            binary (bitarray): The bitarray to decode

        Returns:
            tuple[bitarray, int]: A tuple containing the remaining bitarray and the decoded integer
        """

        # Start from length 1
        length_to_check = 1

        # Loops until number component is found, where first bit is 1
        while not binary[:length_to_check][0]:
            # Get length component based on previous decoded length
            length_comp = binary[:length_to_check]
            # Set first bit to 1
            length_comp[0] = 1
            # Slice the binary to remove decoded length
            binary = binary[length_to_check:]
            # Update length by converting length binary to decimal
            length_to_check = int(length_comp.to01(), 2) + 1

        # Get number component
        num_comp = binary[:length_to_check]

        # Slice binary and convert number component from binary to decimal
        return binary[length_to_check:], int(num_comp.to01(), 2)


class RunlengthEncoder:
    """
    Represents a runlength encoder which utilizes elias and huffman encoding

    Attributes:
        length (int): length of the given string
        bwt_string (str): Burrows-Wheeler transform string
        unique_char_arr (list[char]): List of unique characters in the string
        freq_arr (list[int]): Frequency of each character in the string
        huffman (HuffmanCode): HuffmanCode instance used for encoding
        elias (EliasCode): EliasCode instance used for encoding
    """

    def __init__(self, string: str) -> None:
        self.length = len(string)
        self.bwt_string = self.get_bwt(string)
        self.unique_char_arr, self.freq_arr = self.get_freq_arr()
        self.huffman = HuffmanCode(self.freq_arr)
        self.elias = EliasCode(self.length)

    def get_bwt(self, string: str) -> str:
        """
        Computes the Burrows-Wheeler Transform of the input string

        Parameters:
            string (str): The input string.

        Returns:
            str: The Burrows-Wheeler Transform of the input string.
        """

        # Compute suffix tree using Ukkonens and get suffix array from tree O(n) time
        suffix_tree = SuffixTree(string)
        suffix_arr = suffix_tree.get_suffix_array()

        # Convert suffix array to BWT string
        return "".join([string[(suffix-1) % self.length] for suffix in suffix_arr])

    def get_freq_arr(self) -> tuple[list[str], list[int]]:
        """
        Computes the frequency array and unique character array of the BWT string

        Returns:
            tuple[list[str], list[int]]: A tuple containing the unique character array and the frequency array
        """
        freq_arr = [0] * ASCII_NUM
        unique_char_arr = []
        # Loop for each char in the bwt string
        for char in self.bwt_string:
            # If char has not been seen before then append into unique char array
            if not freq_arr[get_index_from_char(char)]:
                unique_char_arr.append(char)
            # Add 1 to freq arr
            freq_arr[get_index_from_char(char)] += 1

        return unique_char_arr, freq_arr

    def encode_runlength(self, char: str, char_count: int) -> bitarray:
        """
        Encodes a character and its count using Huffman and Elias coding

        Parameters:
            char (str): The character to encode
            char_count (int): The count of the character

        Returns:
            bitarray: The encoded bitarray representing the character and its count
        """
        encoded_char = self.huffman.encode(char)
        encoded_char_count = self.elias.encode(char_count)
        return encoded_char + encoded_char_count

    def encode(self) -> bitarray:
        """
        Encodes the input string using Run-length encoding with Huffman and Elias coding

        Returns:
            bitarray: The encoded bitarray representing the input string
        """

        # Encode the length using Elias
        encoded_length = self.elias.encode(self.length)

        # Create a copy of the encoded length to represent final encoded binary
        final_encoded_bin = encoded_length.copy()

        # Encode unique characters number using Elias
        encoded_uniq_chars = self.elias.encode(len(self.unique_char_arr))

        # Add to final binary
        final_encoded_bin += encoded_uniq_chars

        # Encode each unique character by storing ASCII binary, Elias codelen, and Huffman char
        for char in self.unique_char_arr:
            # Get ascii binary (7 bit)
            ascii_binary = decimal_to_binary(ord(char))
            ascii_binary = bitarray(
                "0") * (7 - len(ascii_binary)) + ascii_binary

            # Encode character using huffman
            char_huffman_encode = self.huffman.encode(char)

            # Encode the code len using Elias
            code_len_encode = self.elias.encode(len(char_huffman_encode))

            # Add to final encoded binary
            final_encoded_bin += ascii_binary + code_len_encode + char_huffman_encode

        # Encode runlength for bwt
        current_char = self.bwt_string[0]
        current_char_count = 1

        # Calculate the runlength of character and encode using Huffman and Elias
        for index in range(1, len(self.bwt_string)):
            # If same character as current char then increment
            if self.bwt_string[index] == current_char:
                current_char_count += 1
            # If character changed then encode run length and char
            else:

                final_encoded_bin += self.encode_runlength(
                    current_char, current_char_count)
                # Change current char
                current_char = self.bwt_string[index]
                current_char_count = 1

        # Add final encoded run length to final encoded binary
        final_encoded_bin += self.encode_runlength(
            current_char, current_char_count)

        # Pad zeroes behind to make it multiple of 8
        final_encoded_bin += bitarray("0") * (-len(final_encoded_bin) % 8)
        return final_encoded_bin


class RunlengthDecoder:
    """
    Represents the runlength decoder that decodes a given binary bitarray that is
    encoded using the runlength encoder

    Attributes:
        binary (bitarray): bitarray for bits that is going to be decoded
        elias (EliasCode): Instance of EliasCode that is used for decoding
        huffman (HuffmanCode): Instance of HuffmanCode that is used for decoding
    """

    def __init__(self, binary: bitarray) -> None:
        self.binary = binary
        self.elias = EliasCode()
        self.huffman = HuffmanCode()

    def get_bwt_rank(self, bwt_string: str) -> list[int]:
        """
        Computes the rank array for the characters in the Burrows-Wheeler Transform string

        Parameters:
            bwt_string (str): The Burrows-Wheeler Transform string

        Returns:
            list[int]: The rank array for the characters in the BWT string
        """

        # Initialize rank array and character count array with a fixed size
        rank = [None] * ASCII_NUM
        char_count = [0] * ASCII_NUM
        # Count the characters in the bwt string
        for char in bwt_string:
            char_count[get_index_from_char(char)] += 1

        prev_count = 0
        prev_rank = 0
        # Compute rank using previous iteration count and rank
        # Already in lexicographic order since it is using ASCII representation
        for index in range(len(char_count)):
            if char_count[index]:
                rank[index] = prev_count + prev_rank
                prev_count = char_count[index]
                prev_rank = rank[index]
        return rank

    def get_bwt_occurrences(self, bwt_string: str) -> list[list[int]]:
        """
        Computes the occurrences array for the characters in the Burrows-Wheeler Transform string

        Parameters:
            bwt_string (str): The Burrows-Wheeler Transform string

        Returns:
            list[list[int]]: The occurrences array for the characters in the BWT string, which contains None or a list
                             containing the occurrence at each index position in BWT string
        """

        # Initialize occurrences array with fixed ascii number size
        occurrences = [None] * ASCII_NUM
        n = len(bwt_string)

        # Get the unique character list from the huffman decoding table values
        unique_char_list = list(self.huffman.decoding_table.values())

        # For each of the characters, create a list of length of bwt string and insert into the occ array
        for char in unique_char_list:
            occurrences[get_index_from_char(char)] = [0] * n

        # Loop for each character in bwt string
        for index, letter in enumerate(bwt_string):
            # Loop in the fixed sized occurrence array
            for occ_index, occ_list in enumerate(occurrences):
                # If occurrence list is present
                if occ_list:
                    # Update the frequency at the index position
                    occ_char = get_char_from_index(occ_index)
                    prev_index = max(0, index-1)
                    add_value = 1 if occ_char == letter else 0
                    occ_list[index] = occ_list[prev_index] + add_value

        return occurrences

    def get_string_from_bwt(self, bwt_string: str) -> str:
        """
        Reconstructs the original string from the Burrows-Wheeler Transform (BWT) string

        Args:
            bwt_string (str): The Burrows-Wheeler Transform (BWT) string

        Returns:
            str: The original string reconstructed from the BWT string
        """
        # Get rank and occurrences array
        bwt_rank = self.get_bwt_rank(bwt_string)
        occurrences = self.get_bwt_occurrences(bwt_string)

        original_string = "$"

        # Start from first character of the bwt string
        current_char = bwt_string[0]
        next_pos = 0

        # Keep looping till character reaches end of string
        while current_char != "$":
            # Add char to the string
            original_string = current_char + original_string

            # Get character index
            char_index = get_index_from_char(current_char)

            # Calculate next position based on rank and occurrences of char from 1 to position
            next_pos = bwt_rank[char_index] + \
                occurrences[char_index][next_pos] - 1
            # Update current character
            current_char = bwt_string[next_pos]

        return original_string

    def decode(self) -> str:
        """
        Decodes the binary string into the original string using Elias coding and Huffman coding

        Returns:
            str: The decoded original string
        """
        # Decode length and number of unique characters using Elias decoding
        self.binary, length = self.elias.decode(self.binary)
        self.binary, num_of_uniq_chars = self.elias.decode(self.binary)

        # Loop all of the unqiue characters
        for _ in range(num_of_uniq_chars):
            # Decode 7 bit ascii, elias code len
            ascii_bin = self.binary[:7]
            ascii_dec = int(ascii_bin.to01(), 2)
            ascii_char = chr(ascii_dec)
            # Slice binary to remove first 7 bits
            self.binary = self.binary[7:]

            # Decode huffman code len using Elias
            self.binary, huffman_code_len = self.elias.decode(self.binary)

            # Get binary representation of character in Huffman encoding
            huffman_char_binary = self.binary[:huffman_code_len]

            self.binary = self.binary[huffman_code_len:]

            # Add to huffman decoder table
            self.huffman.add_to_decoder_table(
                huffman_char_binary.to01(), ascii_char)

        # Get the bwt string from the body of the bit packet
        bwt_string = ""
        huffman_code_count = 0

        # Loop until length reaches 0, all of the character has been decoded
        while length > 0:
            # Increment count
            huffman_code_count += 1
            # Convert to binary string and check if it exists in the huffman decoding table
            huffman_binary_string = self.binary[:huffman_code_count].to01()
            if huffman_binary_string in self.huffman.decoding_table:
                # If exist then remove the number of bits from binary
                self.binary = self.binary[huffman_code_count:]
                # Get the corresponding character
                char = self.huffman.decoding_table[huffman_binary_string]
                # Decode the runlength of the character using Elias
                self.binary, runlength = self.elias.decode(self.binary)
                # Add into the bwt string
                bwt_string += char * runlength

                # Reset count and minus run length from total length
                huffman_code_count = 0
                length -= runlength

        # Get original string from bwt string
        original_string = self.get_string_from_bwt(bwt_string)
        return original_string


def decimal_to_binary(num):
    """
    Converts decimal to binary by using division of 2 and saving
    the remainder
    """
    binary = ""
    # Loop until num reaches 0
    while num > 0:
        remainder = num % 2
        # Save remainder 0 or 1 at the front of binary
        binary = str(remainder) + binary
        num //= 2
    # Convert binary string to bitarray
    return bitarray(binary)


if __name__ == "__main__":
    text = "onceuponatimetherewasalittleboywholivedinalovelyvillagenestledbetweentallmountainsandlushgreenforestshehadafurrycompanionalwaysbyhissideandtogethertheyembarkedoncountlessadventuresexploringthedepthsofthemysteriouswoodsandclimbingthetoweringpeaksonefatefuldaytheydiscoveredasecretcavewhichledtoanenchantedrealmfullofwondersandmysteriesastheylaterexploredthecavetheyencounteredmagicalcreaturesandunearthlybeautiesthatfilledtheirheartswithaweandamazementtheyknewtheyhadfoundaplaceunliketheworldtheyknewandresolvedtovisititagainandagainforitwasadventureawaitingforeachsteptheytook$"
    encoder = RunlengthEncoder(text)
    huff = encoder.huffman
    encoded_text = encoder.encode()

    print(encoded_text)
    decoder = RunlengthDecoder(encoded_text)

    decoded_string = decoder.decode()

    print(decoded_string)
