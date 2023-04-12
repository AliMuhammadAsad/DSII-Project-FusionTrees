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
                while (keys[i] & 1 << w) == (keys[j] & 1 << w) and w >= 0:  
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
                sketch = self.sketchApprox(node, node.keys[i]) # sketch approximation
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
            for i in range(z.key_count + 1):
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
            while i >= 1 and key < node.keys[i - 1]: 
                node.keys[i] = node.keys[i - 1]
                i -= 1
            node.keys[i] = key # Insert key in the correct position
            node.key_count += 1 # Increment key count of the node
            return 
        # If the node is not a leaf node:
        i = node.key_count # Get the current key count
        # Find the index of the appropriate child where key should be inserted 
        while i >= 1 and key < node.keys[i - 1]:
            i -= 1
        # i is position of appropriate child

        # If the child at index i is full, split the child
        if node.children[i].key_count == self.keys_max:
            self.splitChild(node, i)
            # If key is greater than the key at index i, increment i 
            if key > node.keys[i]:
                i += 1
        self.insertNormal(node.children[i], key) # Recursively insert key into the appropriate child

## IQRA KA PART TO COMMENT BELOW THIS _ ALI KA PART ABOVE THIS ##

    def insert(self, k):
        # This insert checks if splitting is needed
        # then it splits and calls normalInsert

        # if root needs splitting, a new node is assigned as root
        # with split nodes as children
        if self.root.key_count == self.keys_max:
            temp_node = Node(self.keys_max)
            temp_node.isLeaf = False
            temp_node.key_count = 0
            temp_node.children[0] = self.root
            self.root = temp_node
            self.splitChild(temp_node, 0)
            self.insertNormal(temp_node, k)
        else:
            self.insertNormal(self.root, k)

    def successorSimple(self, node, k):
        i = 0
        while i < node.key_count and k > node.keys[i]:
            i += 1
        if i < node.key_count and k > node.keys[i]:
            return node.keys[i]
        elif node.isLeaf:
            return node.keys[i]
        else:
            return self.successor2(node.children[i], k)
    
    def parallelComp(self, node, k):
        # this function should basically give the index such
        # that sketch of k lies between 2 sketches
        sketch = self.sketchApprox(node, k)
        # This will give repeated sketch patterns to allow for comparison
        # in const time
        sketch_long = sketch * node.mask_q

        res = node.node_sketch - sketch_long

        # mask out unimportant bits
        res &= node.mask_sketch

        # find the leading bit. This leading bit will tell position i of
        # such that sketch(keyi-1) < sketch(k) < sketch(keyi)
        i = 0
        while (1 << i) < res:
            i += 1
        i += 1
        sketch_len = int(pow(node.key_count, 3)) + 1
        
        return node.key_count - (i // sketch_len)

    def successor(self, k, node = None):
        if node == None:
            node = self.root

        if node.key_count == 0:
            if node.isLeaf:
                return -1
            else:
                return self.successor(k, node.children[0])
       
        # the corner cases are not concretely defined.
        # other alternative to handle these would be to have
        # -inf and inf at corners of keys array
        if node.keys[0] >= k:
            if not node.isLeaf:
                res = self.successor(k, node.children[0])
                if res == -1:
                    return node.keys[0]
                else:
                    return min(node.keys[0], res)
            else:
                return node.keys[0]
        
        if node.keys[node.key_count - 1] < k:
            if node.isLeaf:
                return -1
            else:
                return self.successor(k, node.children[node.key_count])

        pos = self.parallelComp(node, k)
        # print("pos = ", pos)

        if pos >= node.key_count:
            print(node.keys, pos)
            dump = input()
        
        if pos == 0:
            pos += 1
            # x = node.keys[pos]
        
        # find the common prefix
        # it can be guranteed that successor of k is successor
        # of next smallest element in subtree
        x = max(node.keys[pos - 1], node.keys[pos])
        # print("x = ", x)
        common_prefix = 0
        i = self.w
        while i >= 0 and (x & (1 << i)) == (k & (1 << i)):
            # print(i)
            common_prefix |= x & (1 << i) 
            i -= 1
        if i == -1:
            return x
        
        temp = common_prefix | (1 << i)

        pos = self.parallelComp(node, temp)
        # if pos == 0:
        # possible error?
        #     pos += 1
        # print("pos = ", pos, bin(temp))
        if node.isLeaf:
            return node.keys[pos]
        else:
            res = self.successor(k, node.children[pos])
            if res == -1:
                return node.keys[pos]
            else:
                return res

    def predecessor(self, k, node = None):
        if node == None:
            node = self.root

        if node.key_count == 0:
            if node.isLeaf:
                return -1
            else:
                return self.predecessor(k, node.children[0])
       
        # the corner cases are not concretely defined.
        # other alternative to handle these would be to have
        # 0 and inf at corners of keys array
        if node.keys[0] > k:
            if not node.isLeaf:
                return self.predecessor(k, node.children[0])
            else:
                return -1
        
        if node.keys[node.key_count - 1] <= k:
            if node.isLeaf:
                return node.keys[node.key_count - 1]
            else:
                ret =  self.predecessor(k, node.children[node.key_count])
                return max(ret, node.keys[node.key_count - 1])

        pos = self.parallelComp(node, k)

        if pos >= node.key_count:
            print(node.keys, pos, "ERROR? pos > key_count")
            dump = input()
        
        if pos == 0:
            pos += 1
        
        # find the common prefix
        # it can be guranteed that successor of k is successor
        # of next smallest element in subtree
        x = node.keys[pos]
        common_prefix = 0
        i = self.w
        while i >= 0 and (x & (1 << i)) == (k & (1 << i)):
            common_prefix |= x & (1 << i) 
            i -= 1
        if i == -1:     # i.e. if x is exactly equal to k
            return x
        
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

    def initiate(self, node):
        if node == None:
            node = Node(self.keys_max)
        self.initiateNode(node)
        if not node.isLeaf:
            for i in range(node.keys_max + 1):
                self.initiate(node.children[i])
    
    def initiateTree(self):
        self.initiate(self.root)