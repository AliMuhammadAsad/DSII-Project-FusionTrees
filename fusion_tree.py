import hashlib

def compute_hash(book_name):
    hash = int(hashlib.sha256(book_name.encode('utf-8')).hexdigest(), 16) % 10**8
    return hash

class Node:
    """Class for fusion tree node"""
    def __init__(self, max_keys = None):
        # Node Properties
        self.keys = []      # Stores the keys in the node
        self.children = []  # Stores the children of the node
        self.key_count = 0  # Count of number of keys in the Node

        # Fusion Tree Specific Properties
        self.isLeaf = True      # Boolean indicating whether the node is a leaf node or not
        self.m = 0              # Integer repesenting the number of keys in a node
        self.b_bits = []        # List storing the distinguishing bits
        self.m_bits = []        # List storing bits of constant 'm'
        self.gap = 0            # An integer representing the gap between keys
        self.node_sketch = 0    # Integer representing the node sketch
        self.mask_sketch = 0    # Integer representing the mask sketch
        self.mask_q = 0         # Integer used in parallel comparison

        self.mask_b = 0         # Integer for mask_b
        self.mask_bm = 0        # Integer for mask_bm

        self.keys_max = max_keys    # Max keys allowed in a node
        if max_keys != None: # If max_keys are not None, then keys and children are initialized to None values to have space for future operations like splitting
            self.keys = [None for i in range(max_keys + 1)]
            self.children = [None for i in range(max_keys + 2)]

class FusionTree:
    """Fusion tree class. initiateTree is called after all insertions in
    this example. Practically, node is recalculated if its keys are
    modified."""

    def __init__(self, word_len = 64, c = 1/5)-> None:
        ''' Constructor for the Fusion Tree Class.
        Args: 
        - self: mandatory reference to this object
        - word_len : Length of the keys that will be stored in this Tree
        - c : branching factor or parameter used to determine the number of keys each node can hold

        Default Value of word_len is 64 and of c is 1/5 as a Fusion Tree has a branching factor of w^1/5 which gives it a height of O(logw(n)). The default values set max keys allowed in a node to be 2 by the property of B-Trees as a Fusion Tree is essentially a B-Tree

        Returns: None
        '''
        
        self.keys_max = int(pow(word_len, c))   # max keys allowed in a node
        self.keys_max = max(self.keys_max, 2)   # sets max keys to 2 if the max keys are less than 2 - ensures at least 2 keys per node
        self.w = int(pow(self.keys_max, 1/c))   # sets the value of w / word_len
        self.keys_min = self.keys_max // 2      # minimum number of keys allowed in a node

        print("word_len = ", self.w, " max_keys = ", self.keys_max)

        #Initializes the root node of this tree with max number of keys
        self.root = Node(self.keys_max)
        self.root.isLeaf = True
        self.size = 0
        self.keez = []

    def getDiffBits(self, keys) -> list:
        ''' A method that returns a list of of the bits that are different between all pairs of keys given as a list
        Args:
        - self: mandatory reference to this object
        - keys: list of keys to compare

        Returns: a list of different bits        
        '''
        diff_bits = [] # list to store different bits
        bits = 0 # variable to store different bits as bit mask
        for i in range(len(keys)): 
            if keys[i] == None: # break if we encounter a None key
                break
            for j in range(i): # Iterating over previous keys
                w = self.w  #set w as word length
                #Find the position of the first different bit and update the bit mask 
                while (keys[i][0] & 1 << w) == (keys[j][0] & 1 << w) and w >= 0:  
                    w -= 1
                if w >= 0: 
                    bits |= 1 << w
                    # The |= is the in-place OR operator which reassigns the bit value
        i = 0
        while i < self.w:   # Iterate over word length
            if bits & (1 << i) > 0: # if the bit at position i is set, add it to the list
                diff_bits.append(i)
            i += 1
        return diff_bits

    def getConst(self, b_bits) -> tuple:
        ''' A method that calculates the constant 'm' and the corresponding 'm_bits' given the list of distinguishing 'b_bits'
        Args:
        - self: mandatory reference to this object
        - b_bits: the bits that are different between all pairs of keys

        Returns: a tuple containing a list 'm_bits' corresponding to the constant 'm', and the constant 'm'
        '''
        r = len(b_bits) # Total number of different bits
        m_bits = [0 for i in range(r)] # Initializing a list to store m_bits with default values of 0 and length equal to r
        for t in range(r): # iterating over the number of different bits
            mt = 0 # mt which counts the m bits for each iteration
            flag = True # setting a flag
            while flag:
                flag = False
                for i in range(r):
                    if flag:
                        break
                    for j in range(r):
                        if flag:
                            break
                        for k in range(t):
                            # if mt equal the difference between b_bits[i], b_bits[j] plus m_bits[k], set flag to True
                            if mt == b_bits[i] - b_bits[j] + m_bits[k]:
                                flag = True
                                break
                if flag == True: #If flag is true, increment mt
                    mt += 1
            m_bits[t] = mt #set the t-th element of m_bits to mt
        m = 0
        for i in m_bits: # iterate over m_bits
            m |= 1 << i # set the bit at position i in m
        return m_bits, m 
                        
    def getMask(self, mask_bits) -> int:
        ''' A method that returns a mask for a given list of bits.
        The mask is created by setting the bits to 1 at the positions specified in the 'mask_bits' list.
        Args:
        - self: mandatory reference to this object
        - mask_bits: A list of bit positions

        Returns: an integer mask with the specified bit positions set to 1 
        '''
        res = 0 # Mask
        for i in mask_bits:
            res |= 1 << i # Set the bit at position i in the result
        return res

    def initiateNode(self, node) -> None:
        ''' Initializes a given node by calculating and storing different bits, constants, masks, and sketch information. 
        This method should be called once all keys have been inserted
        Args:
        - self: mandatory reference to this object
        - node: a given node

        Returns: None
        '''
        if node.key_count != 0: # If node has keys
            node.b_bits = self.getDiffBits(node.keys) # Calculate the different bits for the node's keys
            node.m_bits, node.m = self.getConst(node.b_bits) # Calculate the constants m_bits and m
            node.mask_b = self.getMask(node.b_bits) # Calculate the mask for b_bits

            temp = [] # Initialize temporary list to store modified b_bits

            # Calculate the position of b[i] after its multiplication with m[i] and store them in temp
            for i in range(len(node.b_bits)):
                temp.append(node.b_bits[i] + node.m_bits[i])
            node.mask_bm = self.getMask(temp) # Calculate the mask for modified b_bits

            # Sketch lengths to maintain node sketch
            r3 = int(pow(node.key_count, 3))

            node.node_sketch = 0 # Initialize node sketch
            sketch_len = r3 + 1 # set sketch length
            node.mask_sketch = 0 # initialize mask_sketch
            node.mask_q = 0 #initialize mask_q

            # Calculate the node sketch, mask_q, and mask_sketch for each key in the node 
            for i in range(node.key_count):
                if node.keys[i] is not None:
                    sketch = self.sketchApprox(node, node.keys[i][0]) # sketch approximation
                    temp = 1 << r3 # temp mask
                    temp |= sketch # add the sketch to the temp mask 
                    node.node_sketch <<= sketch_len # shift node sketch left by sketch_len bits
                    node.node_sketch |= temp # add temporary mask to the node sketch 
                    node.mask_q |= 1 << i * (sketch_len) # Update mask_q
                    node.mask_sketch |= (1 << (sketch_len - 1)) << i * (sketch_len) # Update mask_sketch
        return
    
    def sketchApprox(self, node, x):
        ''' Computes the sketch approximation of a given node and key 'x'. The approximation helps to quickly compare the keys.
        With standard word operations, it is difficult to directly compute the perfect sketch of a key in constant time. So we calculate the approximate sketch which does have all important bits but also some additional useless bits spread out in a predicatable pattern. The ApproximateSketch also preserves the order of the keys
        Args:
        - self: mandatory reference to this object
        - node: node for which we require sketch
        - x : key 'x'

        Returns: 
        '''
        xx = x & node.mask_b # Calculate the intersection of x and the mask for b_bits
        res = xx * node.m # Multiply the intersection by the constant m

        res = res & node.mask_bm # Calculate the intersection of the result and the mask for modified b_bits
        return res # Sketch approximation
    
    def splitChild(self, node, x) -> None:
        ''' Splits the child of a given node at the index 'x'. It is a B-Tree split function, modified for use in Fusion Trees. It ensures that the tree remains balanced during insertions.
        Args:
        - self: mandatory reference to this object
        - node: node which we have to split
        - x: index from which node is being split

        Retuns: None
        '''
        newnode = Node(self.keys_max) # Create a new node with maximum key capacity
        child = node.children[x]    # Child at index from which split occurs

        # Position of the key to propogate
        pos_key = (self.keys_max // 2)

        newnode.key_count = self.keys_max - pos_key - 1 # set the key count for the new node

        # Insert first half keys into z
        for i in range(newnode.key_count):
            newnode.keys[i] = child.keys[pos_key + i + 1]
            child.keys[pos_key + i + 1] = None
        
        # If the child to be split is not a leaf, update the children of the new node
        if not child.isLeaf:
            for i in range(newnode.key_count + 1):
                newnode.children[i] = child.children[pos_key + i + 1]
        
        child.key_count = self.keys_max - newnode.key_count - 1 #Update the key count for the child

        # Insert key into the parent node
        node.keys[x] = child.keys[pos_key]
        
        # Remove the propogated key from the child and add a None value to the end of the key list
        del child.keys[pos_key]
        child.keys.append(None)

        # insert the new node as a child at the x + 1th position
        node.children[x + 1] = newnode

        node.key_count += 1 # Increment the key count of the parent node

    def insertNormal(self, node, key) -> None:
        ''' Inserts a key 'key' into a given node when there is no chance of splitting the root. 
        The method handles two cases:
            (1) When the node is a leaf, the key is simply inserted at the correct position
            (2) When the node is not a leaf, the method finds the appropriate child to insert the key into, calls split if needed, and then recursively inserts the key into the child
        Args:
        - self: mandatory reference to this object
        - node: node which we want to insert the key into
        - key: key to be inserted

        Returns: None
        '''
        # insert key into node when Root can't be split
        if node.isLeaf: # If the node is a leaf
            i = node.key_count # Get the current key count of the node
            # Shift keys to the right until the correct position for key is found
            while i >= 1 and key[0] < node.keys[i - 1][0]: 
                node.keys[i] = node.keys[i - 1]
                i -= 1
            node.keys[i] = key # Insert key in the correct position
            node.key_count += 1 # Increment key count of the node
            return 
        # If the node is not a leaf node:
        i = node.key_count # Get the current key count
        # Find the index of the appropriate child where key should be inserted 
        while i >= 1 and key[0] < node.keys[i - 1][0]:
            i -= 1
        # i is position of appropriate child

        # If the child at index i is full, split the child
        if node.children[i].key_count == self.keys_max:
            self.splitChild(node, i)
            # If key is greater than the key at index i, increment i 
            if key[0] > node.keys[i][0]:
                i += 1
        self.insertNormal(node.children[i], key) # Recursively insert key into the appropriate child

    def insert(self, val) -> None:
        ''' Inserts a new key 'k' into the Tree using the insertNormal method as a helper function. 
        This method handles 2 cases:
            (1) If the root key count is at capacity, then it creates a temporary node and makes it the new root node, then the root temp node is made the new root node, and split is called on the previous root node. The key is then inserted into either one of the new nodes. The insertNormal function is called to find the appropriate node to insert into.
            (2) If root does not need splitting, then it is inserted as normal.
        Args:
        - self: mandatory reference to this object
        - k: the key that has to be inserted

        Returns: None        
        '''
        # k = compute_hash(val[1])
        # t = (k, val[0], val[1], val[2], val[3], val[4])
        # Check if the root node needs splitting due to maximum number of keys
        if self.root.key_count == self.keys_max:
            # Create a new node to become the new root
            temp_node = Node(self.keys_max)
            temp_node.isLeaf = False
            temp_node.key_count = 0
            # Make the current root node the child of the new root node
            temp_node.children[0] = self.root
            # Update the root node to be the new node
            self.root = temp_node
            # Split the child of the new root node (which is the previous root node)
            # and insert the new key into one of the split nodes
            self.splitChild(temp_node, 0)
            self.insertNormal(temp_node, val)
        else:
            # If the root node does not need splitting, just insert the new key normally
            self.insertNormal(self.root, val)      
        self.size += 1
        self.keez.append(val)

    def successorSimple(self, node, k):
        ''' Searches for the position of the key in the current node
        Args:
        - self: mandatory reference to this object
        - node: node in which key is being searched for
        - k: key that we want to find

        Returns: key
        '''

        i = 0
        while i < node.key_count and k > node.keys[i]:
            i += 1
        # If the key is found in the current node, return the next key
        if i < node.key_count and k > node.keys[i]:
            return node.keys[i]
        # If the key is not found in the current node and the node is a leaf, return the key at position i
        elif node.isLeaf:
            return node.keys[i]
        # If the key is not found in the current node and the node is not a leaf, recursively search for the key in the child node at position i
        else:
            return self.successor2(node.children[i], k)
    
    def parallelComp(self, node, k):
        # Calculate the sketch of the key k using the sketchApprox method
        sketch = self.sketchApprox(node, k)
        # Repeat the sketch pattern to allow for comparison in constant time
        sketch_long = sketch * node.mask_q
        # Calculate the difference between the node sketch and the long sketch
        res = node.node_sketch - sketch_long
        # Mask out unimportant bits
        res &= node.mask_sketch
        # Find the leading bit. This will tell the position i such that sketch(key[i-1]) < sketch(k) < sketch(key[i])
        i = 0
        while (1 << i) < res:
            i += 1
        i += 1
        # Calculate the length of the sketch
        sketch_len = int(pow(node.key_count, 3)) + 1
        # Calculate the index of the key such that sketch(key[i-1]) < sketch(k) < sketch(key[i])
        return node.key_count - (i // sketch_len)
    
    def successor(self, k, node = None):
        if node == None:
            node = self.root

        # If the current node is empty and it's a leaf node, return -1 
        # since there is no successor for k in the current leaf node
        if node.key_count == 0:
            if node.isLeaf:
                return -1
            # If the current node is an internal node, continue the search 
            # for the successor in the leftmost child of the node
            else:
                return self.successor(k, node.children[0])
       
        # If k is less than or equal to the smallest key in the node, then 
        # the successor of k is the smallest key in the node or its left child
        if node.keys[0] >= k:
            if not node.isLeaf:
                res = self.successor(k, node.children[0])
                if res == -1:
                    return node.keys[0]
                else:
                    return min(node.keys[0], res)
            else:
                return node.keys[0]
            
        # If k is greater than the largest key in the node, then 
        # the successor of k is in the right child of the node, if it exists
        if node.keys[node.key_count - 1] < k:
            if node.isLeaf:
                return -1
            else:
                return self.successor(k, node.children[node.key_count])

        # Find the position of k in the node by performing parallel comparison
        pos = self.parallelComp(node, k)

        # If pos is out of range, then print an error message and ask for input
        if pos >= node.key_count:
            print(node.keys, pos)
            dump = input()
        
        # If pos is 0, set it to 1 to make sure x is a valid key
        if pos == 0:
            pos += 1
        
        # Set x to be the maximum value among the keys at positions pos-1 and pos
        x = max(node.keys[pos - 1], node.keys[pos])

        # Compute the common prefix between k and x
        common_prefix = 0
        i = self.w
        while i >= 0 and (x & (1 << i)) == (k & (1 << i)):
            common_prefix |= x & (1 << i) 
            i -= 1
        if i == -1:
            return x
        
        # Set temp to be the binary number obtained by setting the bit 
        # at position i to 1 in the common prefix
        temp = common_prefix | (1 << i)

        # Find the position of temp in the node by performing parallel comparison
        pos = self.parallelComp(node, temp)

        # If the current node is a leaf node, then the successor of k is at position pos
        if node.isLeaf:
            return node.keys[pos]
        else:
            # Otherwise, continue the search for the successor in the subtree rooted at the child at position pos
            res = self.successor(k, node.children[pos])
            if res == -1:
                return node.keys[pos]
            else:
                return res

    def predecessor(self, k, node = None):
        if node == None:
            node = self.root

        # If the node is empty, check if it's a leaf node or not
        if node.key_count == 0:
            if node.isLeaf:
                return -1
            else:
                # Traverse to the first child of the current node
                return self.predecessor(k, node.children[0])
       
        # Check if k is smaller than the smallest key in the node
        if node.keys[0] > k:
            if not node.isLeaf:
                 # Traverse to the first child of the current node
                return self.predecessor(k, node.children[0])
            else:
                # k is smaller than the smallest key in the tree
                return -1
        
        # Check if k is larger than or equal to the largest key in the node
        if node.keys[node.key_count - 1] <= k:
            if node.isLeaf:
                # Return the largest key in the current node
                return node.keys[node.key_count - 1]
            else:
                # Traverse to the last child of the current node
                ret =  self.predecessor(k, node.children[node.key_count])
                return max(ret, node.keys[node.key_count - 1])

        # Find the position of k in the current node
        pos = self.parallelComp(node, k)

        # If the position of k is larger than the number of keys in the node, it's an error
        if pos >= node.key_count:
            print(node.keys, pos, "ERROR? pos > key_count")
            dump = input()
        
        # If the position of k is 0, it means k is smaller than the smallest key in the node
        if pos == 0:
            pos += 1
        
        # Find the common prefix between k and the key in the current node at position pos
        x = node.keys[pos]
        common_prefix = 0
        i = self.w
        while i >= 0 and (x & (1 << i)) == (k & (1 << i)):
            common_prefix |= x & (1 << i) 
            i -= 1

        # If x is exactly equal to k, return x
        if i == -1:
            return x
        
        # Find the key with the largest common prefix with k that is smaller than k
        temp = common_prefix | ((1 << i) - 1)
        pos = self.parallelComp(node, temp)
        if pos == 0:
            if node.isLeaf:
                return node.keys[pos]
            res = self.predecessor(k, node.children[1])
            if res == -1:
                return node.keys[pos]
            else:
                return res
                
        if node.isLeaf:
            return node.keys[pos - 1]
        else:
            res = self.predecessor(k, node.children[pos])
            if res == -1:
                return node.keys[pos - 1]
            else:
                return res
            
    def initiate(self, node : Node):
        if node == None:
            node = Node(self.keys_max)
        # Call the initiateNode function to set the node's fields to their default values
        self.initiateNode(node)
        # If the node is not a leaf, then recursively call initiate on its children
        if not node.isLeaf:
            for i in range(node.keys_max + 1):
                self.initiate(node.children[i])
    
    def initiateTree(self):
        # Call initiate function on the root node
        self.initiate(self.root)

    # def mergeNodes(self, parentNode : Node, childIndex : int) -> None:
    #     ''' Method that will be used in the delete function to handle merging of the nodes whenever required
    #     Args:
    #     - self: mandatory reference to this object
    #     - parentNode: the parentNode of the key
    #     - childIndex: index in the child node

    #     Returns: None
    #     '''
    #     # Merge left and right children of the parent node
    #     leftChild = parentNode.children[childIndex]
    #     rightChild = parentNode.children[childIndex + 1]

    #     for i in range(rightChild.key_count):
    #         leftChild.keys[leftChild.key_count] = rightChild.keys[i]
    #         leftChild.children[leftChild.key_count] = rightChild.children[i]
    #         leftChild.key_count += 1
        
    #     leftChild.children[leftChild.key_count] = rightChild.children[rightChild.key_count]

    #     for i in range(childIndex, parentNode.key_count - 1):
    #         parentNode.keys[i] = parentNode.keys[i + 1]
    #         parentNode.children[i + 1] = parentNode.children[i + 2]
        
    #     parentNode.key_count -= 1
    
    # def redestributeNodes(self, parentNode : Node, childIndex : int) -> None:
    #     # Redestribute the keys between the left and right child of the parent Node
    #     leftChild = parentNode.children[childIndex]
    #     rightChild = parentNode.children[childIndex + 1]

    #     if leftChild.key_count < rightChild.key_count:
    #         leftChild.keys[leftChild.key_count] = parentNode.keys[childIndex]
    #         leftChild.children[leftChild.key_count + 1] = rightChild.children[0]
    #         leftChild.key_count += 1

    #         parentNode.keys[childIndex] = rightChild.keys[0]

    #         for i in range(rightChild.key_count - 1):
    #             rightChild.keys[i] = rightChild.keys[i + 1]
    #             rightChild.children[i] = rightChild.children[i + 1]

    #         rightChild.children[rightChild.key_count - 1] = rightChild.children[rightChild.key_count]
    #         rightChild.key_count -= 1
    #     else:
    #         for i in range(rightChild.key_count):
    #             rightChild.keys[rightChild.key_count] = rightChild.keys[rightChild.key_count - 1]
    #             rightChild.children[rightChild.key_count + 1] = rightChild.children[rightChild.key_count]
    #             rightChild.key_count -= 1

    #         rightChild.keys[0] = parentNode.keys[childIndex]
    #         rightChild.children[0] = leftChild.children[leftChild.key_count]

    #         parentNode.keys[childIndex] = leftChild.keys[leftChild.key_count - 1]
    #         leftChild.key_count -= 1
    
    # def deleteAndResolve(self, k, node = None) -> None:
    #     if node is None: node = self.root

    #     # if node is empty, the key is not found
    #     if node.key_count == 0: return 

    #     # find the position of k in the current node
    #     pos = self.parallelComp(node, k)
        
    #     # if the position of k is within the bounds of the keys in the node and the key at the position is equal to k
    #     if pos < node.key_count and node.keys[pos] == k:
    #         # if the node is a leaf, delete the key from the node
    #         if node.isLeaf:
    #             for i in range(pos, node.key_count):
    #                 node.keys[i] = node.keys[i + 1]
    #             node.key_count -= 1
    #             return
        
    #         # If the node is not a leaf, find the predecessor or the successor of the key and replace the key with its predecessor or successor. Then, recursively delete the predecessor or successor from the appropriate subtree.
    #         leftChild = node.children[pos]
    #         rightChild = node.children[pos + 1]

    #         if leftChild.key_count >= (self.keys_max + 1) // 2:
    #             pred = self.predecessor(k, leftChild)
    #             node.keys[pos] = pred
    #             self.deleteAndResolve(pred, leftChild)
    #         else: 
    #             succ = self.successor(k, rightChild)
    #             node.keys[pos] = succ
    #             self.deleteAndResolve(succ, rightChild)
    #     # If key not found in the current node, then continue searching in the child nodes
    #     else:
    #         if node.isLeaf: return
    #         if node.children[pos].key_count < (self.keys_max + 1) // 2:
    #             if pos > 0 and node.children[pos - 1].key_count >= (self.keys_max + 1) // 2:
    #                 self.redestributeNodes(node, pos - 1)
    #             elif pos > 0 and node.children[pos + 1].key_count >= (self.keys_max + 1) // 2:
    #                 self.redestributeNodes(node, pos)
    #             else:
    #                 if pos > 0:
    #                     self.mergeNodes(node, pos - 1); pos -= 1
    #                 else: self.mergeNodes(node, pos)

    #                 if node.key_count == 0 and node == self.root:
    #                     self.root = node.children[0]
    #         self.deleteAndResolve(k, node.children[pos])

    
    # def delete(self, k, node = None)-> None:
    #     ''' Delete method which deletes a key 'k' from a given node
    #     Args:
    #     - self: manadatory reference to this object
    #     - node: node from which key is to be deleted
    #     - k: key that has to be deleted

    #     Returns: None
    #     '''
    #     self.deleteAndResolve(k)

        # if node is None: # if no node is provided, then we start search from the root node 
        #     node = self.root 
        
        # if node.key_count == 0: # if the node is empty, then key does not exist so key not found
        #     return
        
        # # Find the position of k in the current node
        # pos = self.parallelComp(node, k)

        # # If the position of k is within bounds of the key in the node and the key at the position is equal to k
        # if pos < node.key_count and node.keys[pos] == k:
        #     if node.isLeaf: #If node is a leaf then delete the key from the node by shifting the keys forward to the left, and decrement the total key count
        #         for i in range(pos, node.key_count):
        #             node.keys[i] = node.keys[i + 1]
        #         node.key_count -= 1
        #         return
            
        #     #If node is not a leaf then find its predecessor or successor and replace the key with the predecessor or successor
        #     pred = self.predecessor(k, node)
        #     if pred != -1:
        #         node.keys[pos] = pred
        #         self.delete(pred, node.children[pos])
        #     else:
        #         succ = self.successor(k, node)
        #         node.keys[pos] = succ
        #         self.delete(succ, node.children[pos + 1])
        # elif node.isLeaf: return # if node is a leaf, then key not found
        # else: # if key not found in current node, then continue search in the child node at position pos
        #     self.delete(k, node.children[pos])