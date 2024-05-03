from tools import ASCII_NUM, NAN, get_index_from_char

global_end = float("inf")


class Node:
    """
    Represents a node in a Suffix Tree data structure

    Each node contains a fixed size list of children representing the edges connecting
    children to current node
    If the node is a leaf, then leaf number will be set to the suffix position, else it
    will be defaulted to NAN. NAN means that node is not a leaf
    Each internal node will have a suffix link from current node to the jump node 

    Attributes:
        children (list[Edge]): A list representing child edges
        leaf_num (int): Leaf number representing the suffix position
        suffix_link (Node): References to the node to jump to
    """

    def __init__(self) -> None:
        self.children = [None] * ASCII_NUM
        self.leaf_num = NAN
        self.suffix_link = None


class Edge:
    """
    Represents an edge in a Suffix Tree that connects 2 nodes

    Each edge will store the start point and end point of the string and the
    child node that the edge is connecting to

    Attributes:
        start_point (int): The starting index of the string for the edge
        end_point (int): The end index of the string for the edge
        child_node (Node): The node that the edge is connecting to
    """

    def __init__(self, start: int, end: int) -> None:
        self.start_point = start
        self.end_point = end
        self.child_node = None


class SuffixTree:
    """
    Represents a Suffix Tree that utilizes Ukkonen's algorithm to achieve
    O(n) linear time Suffix tree construction

    Attributes:
        string (str): The input string that the suffix tree will be constructed with
        root (Node): Root node of the tree
        active_node (Node): Current active node during construction, to perform tricks
        remainder_start (int): Start point of the remainder string
        remainder_end (int): End point of the remainder string
        last_j (int): Pointer for extension to skip rule 1s in rapid leaf extension
        prev_added_node (Node): Internal node that was previously added in rule 2 case 2 
                                and waiting for suffix link
    """

    def __init__(self, string):
        self.string = string
        self.root = Node()
        # Root suffix link is itself
        self.root.suffix_link = self.root
        self.active_node = None
        self.remainder_start = 0
        self.remainder_end = -1
        self.last_j = -1
        self.prev_added_node = None

        # Build suffix tree
        self.add_string()

    def get_remainder_length(self) -> int:
        """
        Returns the length of the remainder substring

        Returns:
            int: The length of the current remainder substring
        """
        return self.remainder_end - self.remainder_start + 1

    def get_edge_length(self, edge: Edge, phase: int) -> int:
        """
        Returns the length of the edge that was passed in

        Parameters:
            edge (Edge): Edge to compute length with
            phase (int): Current phase number to override if global_end is used

        Returns:
            int: Length of the edge
        """
        # If the child code of the edge is a leaf then end point is the current phase
        end_point = phase if edge.child_node.leaf_num != NAN else edge.end_point
        return end_point - edge.start_point + 1

    def skip_count(self, phase: int) -> tuple[int, Edge]:
        """
        Performs skip counting operation during suffix tree construction

        Check if there's a remainder from previous phase (rule 3) then skip count
        down to the node that holds the remainder_end, while changing active node
        if there's an internal node in the middle of the skip count
        During skip counting, if remainder length == edge length then take the 
        phase character for the remainder start instead

        If there's no remainder, then take the current phase character and the 
        corresponding edge for the character from the active node

        Parameters:
            phase (int): Current phase during suffix tree construction

        Returns:
            tuple(int, edge): The decimal representation of ascii character and
                              the child edge for the ascii character
        """
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

    def suffix_extension(self, phase: int, j: int, next_edge_index: int, next_edge: Edge) -> bool:
        """
        Extends the suffix tree at a given phase and j extension

        If there is no next edge then create an edge and leaf node (rule 2 case 1)
        Any rule 2 will increment last j which will skip this extension at the following
        phase
        Else it will check if the phase character is matching with the character in the
        corresponding character to check
        If it already exist then rule 3, and break out of the loop
        If not then rule 2 case 2, create new internal node

        Parameters:
            phase (int): Current phase number
            j (int): Current extension in the phase
            next_edge_index (int): next edge index from the active node
            next_edge (Edge): Current edge that we are looking at

        Returns:
            bool: True if should break out of phase, false otherwise
        """
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
                    self.prev_added_node.suffix_link = self.active_node

                # Case 3, break out of loop
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

    def suffix_link_jump(self) -> None:
        """
        Moves to next extension through suffix link or decrement remainder length
        """
        # If active node is root and there's remainder, then remove the first character in remainder
        if self.active_node == self.root and self.get_remainder_length() > 0:
            self.remainder_start += 1
        # If active node is not the root then move through suffix link to the next node (Every internal node will have a link)
        elif self.active_node != self.root:
            self.active_node = self.active_node.suffix_link

    def add_string(self) -> None:
        """
        Construct suffix tree using the given string
        """
        n = len(self.string)
        self.active_node = self.root

        # For each phase add the phase character
        for i in range(n):
            self.add_char(i)

    def add_char(self, phase: int) -> None:
        """
        Perform extension for the given phase

        First, perform skip counting to get the edge.
        Then, perform suffix extension with the given edge and resolve any suffix links
        Finally, perform suffix link jumps at the end of each extension

        Parameters:
            phase (int): Current phase number
        """
        self.prev_added_node = None

        for j in range(self.last_j + 1, phase + 1):
            # Get next edge and next edge index by skip counting
            next_edge_index, next_edge = self.skip_count(phase)

            # perform suffix extension (rule 2 or 3 only), if suffix extension is rule 3 then break
            if self.suffix_extension(phase, j, next_edge_index, next_edge):
                break

            # perform suffix link jump at the end of extension
            self.suffix_link_jump()

    def dfs(self, node: Node, suffix_array: list[int], depth: int = 0, verbosity: int = 0) -> None:
        """
        Perform depth first search through the tree going from left to right, since we are
        using a fixed children array size and this array will give us the lexicographic order, 
        thus we can construct our suffix array.

        Parameters:
            node (Node): The current node that is being traversed
            suffix_array (list[int]): Suffix array that will contain all the suffix numbers at the end
            depth (int): Depth of the tree that we're traversing, used for logging
            verbosity (int): Determines whether to display the tree or not
        """
        # Loops through each children in current node and checks if there's an edge or not
        for child in node.children:
            # If there's an edge then check if it a leaf or not
            if child:
                if verbosity:
                    print(
                        "|- " * depth + self.string[child.start_point: min(child.end_point, len(self.string)-1) + 1])
                # If it is a leaf then append into the suffix array
                if child.child_node.leaf_num != NAN:
                    suffix_array.append(child.child_node.leaf_num)
                # Depth first search through the child node
                self.dfs(child.child_node, suffix_array, depth+1, verbosity)

    def get_suffix_array(self) -> None:
        """
        Gets the suffix array using depth first search starting from the root

        Returns:
            list[int] : Returns the suffix array for the suffix tree in O(n) time
        """
        suffix_array = []
        # Perform dfs starting from the root
        self.dfs(self.root, suffix_array, verbosity=1)
        return suffix_array


def get_rank_from_position(suffix_array: list[int], position_list: list[int]) -> list[int]:
    """
    Gets the ranks of the suffixes given the position in the position list

    Parameters:
        suffix_array (list[int]): Contains the suffix array for the string
        position_list (list[int]): List of positions for suffixes

    Returns:
        list[int]: List containing all the ranks of the positions of the suffix
    """
    rank_arr = []
    # For each of the position get the index of position in the suffix array and add by 1 to
    # make it 1 base
    for p in position_list:
        rank_arr.append(suffix_array.index(p - 1) + 1)

    return rank_arr


if __name__ == "__main__":
    text = "onceuponatimetherewasalittleboywholivedinalovelyvillagenestledbetweentallmountainsandlushgreenforestshehadafurrycompanionalwaysbyhissideandtogethertheyembarkedoncountlessadventuresexploringthedepthsofthemysteriouswoodsandclimbingthetoweringpeaksonefatefuldaytheydiscoveredasecretcavewhichledtoanenchantedrealmfullofwondersandmysteriesastheylaterexploredthecavetheyencounteredmagicalcreaturesandunearthlybeautiesthatfilledtheirheartswithaweandamazementtheyknewtheyhadfoundaplaceunliketheworldtheyknewandresolvedtovisititagainandagainforitwasadventureawaitingforeachsteptheytook$"
    suffix_tree = SuffixTree(text)

    suffix_array = suffix_tree.get_suffix_array()

    print(suffix_array)

    position = []

    ranks = get_rank_from_position(suffix_array, position)
    print(ranks)
