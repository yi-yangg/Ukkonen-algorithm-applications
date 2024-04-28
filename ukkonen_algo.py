MIN_ASCII_CHAR_NO = 36
MAX_ASCII_CHAR_NO = 126

ASCII_NUM = MAX_ASCII_CHAR_NO - MIN_ASCII_CHAR_NO + 1
NAN = -1


class Node:
    def __init__(self):
        self.children = [None] * ASCII_NUM
        self.parent_edge = None
        self.leaf_num = NAN


class Edge:
    def __init__(self, start, end):
        self.start_point = start
        self.end_point = end
        self.parent_node = None
        self.child_node = None


class SuffixTree:
    def __init__(self):
        self.root = Node()

    def add_string(self, string: str):
        n = len(string)
        # For each phase add the phase character
        for i in range(n):
            self.add_char(string, i)

    def add_char(self, string: str, phase: int):
        char = string[phase]
        # extension starts from 0 to i
        for j in range(phase + 1):
            current_path = string[j:phase]
            current_node = self.root
            length_of_path = len(current_path)

            # if there exist a path, traverse down the path
            if current_path:
                current_char = string[j]
                # traversing down path
                while current_node:
                    current_edge = current_node.children[get_index_from_char(
                        current_char)]
                    if not current_edge:
                        break

                    # get length of edge
                    length_of_edge = current_edge.end_point - current_edge.start_point + 1
                    # leads to the leaf, set current node to leaf node
                    if length_of_edge == length_of_path:
                        length_of_path -= length_of_edge
                        current_node = current_edge.child_node
                        break
                    # if the traversed path is contained inside the edge
                    elif length_of_edge > length_of_path:
                        break
                    # if path is more than the length of the edge, traverse down further
                    else:
                        length_of_path -= length_of_edge
                        current_node = current_edge.child_node
                        current_char = current_path[len(
                            current_path) - length_of_path]

            # check if current node is a leaf, if it is then perform rule 1 extension
            if current_node.leaf_num != NAN:
                current_node.parent_edge.end_point += 1

            else:
                # if length of path is left with 0
                if not length_of_path:
                    # check if extended char is a child of current_node
                    extended_edge = current_node.children[get_index_from_char(
                        char)]
                    # If theres an edge under that already exists, then rule 3
                    if extended_edge:
                        return
                    # If theres no edge, then rule 2 case 1, create new leaf and edge
                    else:
                        new_node = Node()
                        new_edge = Edge(phase, phase)

                        new_node.leaf_num = j
                        new_node.parent_edge = new_edge

                        new_edge.parent_node = current_node
                        new_edge.child_node = new_node
                        current_node.children[get_index_from_char(
                            char)] = new_edge
                # If theres still remaining path, go to the end of the path
                else:
                    branch_char = current_path[
                        len(current_path) - length_of_path]
                    branch_edge = current_node.children[get_index_from_char(
                        branch_char)]

                    char_to_check_index = branch_edge.start_point + length_of_path
                    char_to_check = string[char_to_check_index]
                    # If next char in existing path is not the same as string[phase], rule 2 case 2
                    if char_to_check != char:
                        # Add new internal node
                        new_internal_node = Node()
                        new_internal_node.parent_edge = branch_edge

                        # Add new extended edge
                        # Set start point to the mismatched pos and end to the existing branch end
                        new_extended_edge = Edge(
                            char_to_check_index, branch_edge.end_point)
                        new_extended_edge.parent_node = new_internal_node
                        new_extended_edge.child_node = branch_edge.child_node

                        # Updating leaf node parent edge
                        branch_edge.child_node.parent_edge = new_extended_edge

                        # Update existing edge
                        branch_edge.end_point = branch_edge.start_point + length_of_path - 1
                        branch_edge.child_node = new_internal_node

                        # Create new branch for char with leaf node
                        new_leaf_node = Node()
                        new_branch_edge = Edge(phase, phase)

                        new_leaf_node.parent_edge = new_branch_edge
                        new_leaf_node.leaf_num = j

                        new_branch_edge.parent_node = new_internal_node
                        new_branch_edge.child_node = new_leaf_node

                        new_internal_node.children[get_index_from_char(
                            char_to_check)] = new_extended_edge
                        new_internal_node.children[get_index_from_char(
                            char)] = new_branch_edge

                    else:
                        return

    def dfs(self, node, string):
        for child in node.children:

            if child:
                print(string[child.start_point:child.end_point+1])
                self.dfs(child.child_node, string)


def get_index_from_char(c: str):
    return ord(c) - MIN_ASCII_CHAR_NO


if __name__ == "__main__":
    suffix_tree = SuffixTree()
    string = "abacabad"
    suffix_tree.add_string(string)

    current_node = suffix_tree.root

    suffix_tree.dfs(current_node, string)
