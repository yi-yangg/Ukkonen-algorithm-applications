import sys
from tools import read_file, write_file, ASCII_NUM, NAN, get_index_from_char


global_end = float("inf")


class Node:
    def __init__(self):
        self.children = [None] * ASCII_NUM
        self.leaf_num = NAN
        self.suffix_link = None


class Edge:
    def __init__(self, start, end):
        self.start_point = start
        self.end_point = end
        self.child_node = None


class SuffixTree:
    def __init__(self, string):
        self.string = string
        self.root = Node()
        self.active_node = None
        self.remainder_start = 0
        self.remainder_end = -1
        self.last_j = -1
        self.prev_added_node = None

        self.add_string()

    def get_remainder_length(self):
        return self.remainder_end - self.remainder_start + 1

    def get_edge_length(self, edge: Edge, phase: int):
        end_point = edge.end_point
        # If the child code of the edge is a leaf then end point is your phase
        if edge.child_node.leaf_num != NAN:
            end_point = phase

        return end_point - edge.start_point + 1

    def skip_count(self, phase):
        # Perform skip count, get length of remainder
        remainder_length = self.get_remainder_length()

        # If remainder is valid only skip count
        if remainder_length > 0:
            # Get the next edge from the active node using remainder start
            while True:
                next_edge_index = get_index_from_char(
                    self.string[self.remainder_start])
                next_edge = self.active_node.children[next_edge_index]
                # If next edge is None then break
                if not next_edge:
                    break

                # Get edge length and compare with remainder length
                next_edge_length = self.get_edge_length(next_edge, phase)

                # Check if remainder length is greater than edge length, if greater than can traverse deeper
                if remainder_length >= next_edge_length:
                    # Minus of the edge length from remainder length
                    remainder_length -= next_edge_length
                    # Check if remainder length is not zero then traverse down the tree
                    if remainder_length:
                        self.remainder_start += next_edge_length
                    # If remainder length is zero then set start to the current phase character
                    else:
                        self.remainder_start = phase
                    # Traverse down by setting active node to child of edge
                    self.active_node = next_edge.child_node
                else:
                    break
        # If remainder is less than or equal 0
        else:
            # Then just get the edge by using the current phase character
            next_edge_index = get_index_from_char(
                self.string[phase])
            next_edge = self.active_node.children[next_edge_index]

        return next_edge_index, next_edge

    def suffix_extension(self, phase, j, next_edge_index, next_edge):
        # If edge doesn't exist then create edge on existing node rule 2 case 1
        if not next_edge:
            # Rule 2 case 1 (create edge and leaf)
            new_leaf = Node()
            new_edge = Edge(phase, global_end)
            new_edge.child_node = new_leaf
            new_leaf.leaf_num = j

            self.active_node.children[next_edge_index] = new_edge

            # Since current j extension in phase i uses case 2, this means j extension in phase i+1 must use rule 1
            self.last_j += 1

            # Resolve any suffix link for previous created node, set to active node
            if self.prev_added_node:
                self.prev_added_node.suffix_link = self.active_node
                self.prev_added_node = None

        # If edge connecting the active node already exists, check if the current phase char exists or not
        else:
            # Get remainder length, 0 when the end is lesser than start, else just use function to get length
            len_remainder = 0 if self.remainder_end < self.remainder_start else self.get_remainder_length()
            char_to_check_index = next_edge.start_point + len_remainder
            # Rule 3 where the character already exist in the edge
            if self.string[char_to_check_index] == self.string[phase]:
                # Update remainder to the matched string
                self.remainder_start = next_edge.start_point
                self.remainder_end = char_to_check_index
                # Resolve any suffix link, set to active node
                if self.prev_added_node:
                    self.prev_added_node = self.active_node
                return True

            # Rule 2 Case 2 where character doesn't match character in edge
            else:
                # Create internal node, new extended edge, new leaf edge and node
                new_internal_node = Node()
                # Set suffix link to root
                new_internal_node.suffix_link = self.root
                # Add new extended edge
                # Set start point to the mismatched pos and end to the existing branch end
                new_extended_edge = Edge(
                    char_to_check_index, next_edge.end_point)

                new_extended_edge.child_node = next_edge.child_node

                # Update existing edge
                next_edge.end_point = char_to_check_index - 1
                next_edge.child_node = new_internal_node

                # Create new branch for char with leaf node
                new_leaf_node = Node()
                new_branch_edge = Edge(phase, global_end)

                new_leaf_node.leaf_num = j

                new_branch_edge.child_node = new_leaf_node

                # Set internal node children to be the new extended edge and new leaf edge
                new_internal_node.children[get_index_from_char(
                    self.string[char_to_check_index])] = new_extended_edge
                new_internal_node.children[get_index_from_char(
                    self.string[phase])] = new_branch_edge

                # Resolve suffix link for previous added internal node and link to newly created internal node
                if self.prev_added_node:
                    self.prev_added_node.suffix_link = new_internal_node

                # Set previous added internal node to the newly created node
                self.prev_added_node = new_internal_node

                # Increment last j since we used rule 2, next j of phase i + 1 will use rule 1
                self.last_j += 1

        return False

    def suffix_link_jump(self):
        # Moving to next extension
        if self.active_node == self.root and self.get_remainder_length() > 0:
            self.remainder_start += 1

        elif self.active_node != self.root:
            self.active_node = self.active_node.suffix_link

    def add_string(self):
        n = len(self.string)
        self.active_node = self.root

        # For each phase add the phase character
        for i in range(n):
            self.add_char(i)

    def add_char(self, phase: int):
        self.prev_added_node = None

        for j in range(self.last_j + 1, phase + 1):
            # Get next edge and next edge index by skip counting
            next_edge_index, next_edge = self.skip_count(phase)

            # perform suffix extension (rule 2 or 3 only), if suffix extension is rule 3 then break
            if self.suffix_extension(phase, j, next_edge_index, next_edge):
                break

            # perform suffix link jump at the end of extension
            self.suffix_link_jump()

    def dfs(self, node, suffix_array, depth=0, verbosity=0):
        for child in node.children:
            if child:
                if verbosity:
                    print(
                        "|- " * depth + self.string[child.start_point: min(child.end_point, len(self.string)-1) + 1])
                if child.child_node.leaf_num != NAN:
                    suffix_array.append(child.child_node.leaf_num)
                self.dfs(child.child_node, suffix_array, depth+1, verbosity)

    def get_suffix_array(self):
        suffix_array = []
        self.dfs(self.root, suffix_array)
        return suffix_array


def get_rank_from_position(suffix_array, position_list):
    rank_arr = []
    for p in position_list:
        rank_arr.append(suffix_array.index(p - 1) + 1)

    return rank_arr


if __name__ == "__main__":
    _, string_file, position_file = sys.argv

    text = read_file(string_file)

    position = read_file(position_file)

    position_list = [int(pos) for pos in position.split("\n")]

    suffix_tree = SuffixTree(text)

    suffix_array = suffix_tree.get_suffix_array()

    rank_arr = get_rank_from_position(suffix_array, position_list)

    rank_str = "\n".join(map(str, rank_arr))

    write_file("output_ukkonen.txt", rank_str)
