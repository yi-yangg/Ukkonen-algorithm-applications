MIN_ASCII_CHAR_NO = 36
MAX_ASCII_CHAR_NO = 126

ASCII_NUM = MAX_ASCII_CHAR_NO - MIN_ASCII_CHAR_NO + 1

NAN = -1


def read_file(file_path: str) -> str:
    """
    Given a file path read the contents of a file

    Parameters:
    file_path (str): file path to read the files at

    Returns:
    str: Contents of the file
    """
    f = open(file_path, 'r')
    text = f.read()
    f.close()

    return text


def write_file(file_path: str, content: str) -> None:
    """
    Given file path and the content, write content to the file

    Parameters:
    file_path (str): file path to write the files to
    content (str): Content to write into the file
    """
    f = open(file_path, "w")
    f.write(content)
    f.close()


def get_index_from_char(c: str):
    return ord(c) - MIN_ASCII_CHAR_NO


def get_char_from_index(index):
    return chr(index + MIN_ASCII_CHAR_NO)


def decimal_to_binary(num):
    binary = ""

    while num > 0:
        remainder = num % 2
        binary = str(remainder) + binary
        num //= 2

    return bitarray(binary)
