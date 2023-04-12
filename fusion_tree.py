class Node:
    """Class for fusion tree node"""
    def __init__(self, max_keys = None):
        # Node Properties
        self.keys = []      # Stores the keys in the node
        self.children = []  # Stores the children of the node
        self.key_count = 0  # Count of number of keys in the Node

        # Fusion Tree Specific Properties
        self.isLeaf = True
        self.m = 0
        self.b_bits = []    # distinguishing bits
        self.m_bits = []    # bits of constant m
        self.gap = 0
        self.node_sketch = 0
        self.mask_sketch = 0
        self.mask_q = 0     # used in parallel comparison

        self.mask_b = 0
        self.mask_bm = 0

        self.keys_max = max_keys
        if max_keys != None:
            # an extra space is assigned so that splitting can be
            # done easily
            self.keys = [None for i in range(max_keys + 1)]
            self.children = [None for i in range(max_keys + 2)]

class FusionTree:
    """Fusion tree class. initiateTree is called after all insertions in
    this example. Practically, node is recalculated if its keys are
    modified."""

    def __init__(self, word_len = 64, c = 1/5):
        self.keys_max = int(pow(word_len, c))
        self.keys_max = max(self.keys_max, 2)
        self.w = int(pow(self.keys_max, 1/c))
        self.keys_min = self.keys_max // 2

        print("word_len = ", self.w, " max_keys = ", self.keys_max)

        self.root = Node(self.keys_max)
        self.root.isLeaf = True

    def getDiffBits(self, keys):
        res = []

        bits = 0
        for i in range(len(keys)):
            if keys[i] == None:
                break
            for j in range(i):
                w = self.w
                
                while (keys[i] & 1 << w) == (keys[j] & 1 << w) and w >= 0:
                    w -= 1
                if w >= 0:
                    bits |= 1 << w
        
        i = 0
        while i < self.w:
            if bits & (1 << i) > 0:
                res.append(i)
            i += 1
        return res

    def getConst(self, b_bits):
        r = len(b_bits)
        m_bits = [0 for i in range(r)]
        for t in range(r):
            mt = 0
            flag = True
            while flag:
                flag = False
                for i in range(r):
                    if flag:
                        break
                    for j in range(r):
                        if flag:
                            break
                        for k in range(t):
                            if mt == b_bits[i] - b_bits[j] + m_bits[k]:
                                flag = True
                                break
                if flag == True:
                    mt += 1
            m_bits[t] = mt
        
        m = 0
        for i in m_bits:
            m |= 1 << i
        return m_bits, m
                        
    def getMask(self, mask_bits):
        res = 0
        for i in mask_bits:
            res |= 1 << i
        return res

    def initiateNode(self, node):
        if node.key_count != 0:
            node.b_bits = self.getDiffBits(node.keys)
            node.m_bits, node.m = self.getConst(node.b_bits)
            node.mask_b = self.getMask(node.b_bits)

            temp = []
            # bm[i] will be position of b[i] after its multiplication
            # with m[i]. mask_bm will isolate these bits.
            for i in range(len(node.b_bits)):
                temp.append(node.b_bits[i] + node.m_bits[i])
            node.mask_bm = self.getMask(temp)

            # used to maintain sketch lengths
            r3 = int(pow(node.key_count, 3))

            node.node_sketch = 0
            sketch_len = r3 + 1
            node.mask_sketch = 0
            node.mask_q = 0
            for i in range(node.key_count):
                sketch = self.sketchApprox(node, node.keys[i])
                temp = 1 << r3
                temp |= sketch
                node.node_sketch <<= sketch_len
                node.node_sketch |= temp
                node.mask_q |= 1 << i * (sketch_len)
                node.mask_sketch |= (1 << (sketch_len - 1)) << i * (sketch_len)
        return
    
    def sketchApprox(self, node, x):
        xx = x & node.mask_b
        res = xx * node.m

        res = res & node.mask_bm
        return res
    
    def splitChild(self, node, x):
        # a b-tree split function. Splits child of node at x index
        z = Node(self.keys_max)
        y = node.children[x]   # y is to be split

        # pos of key to propagate
        pos_key = (self.keys_max // 2)

        z.key_count = self.keys_max - pos_key - 1

        # insert first half keys into z
        for i in range(z.key_count):
            z.keys[i] = y.keys[pos_key + i + 1]
            y.keys[pos_key + i + 1] = None
        
        if not y.isLeaf:
            for i in range(z.key_count + 1):
                z.children[i] = y.children[pos_key + i + 1]
        
        y.key_count = self.keys_max - z.key_count - 1

        # insert key into node
        node.keys[x] = y.keys[pos_key]
        
        # same effect as shifting all keys after setting pos_key
        # to None
        del y.keys[pos_key]
        y.keys.append(None)

        # insert z as child at x + 1th pos
        node.children[x + 1] = z

        node.key_count += 1

    def insertNormal(self, node, k):
        # print(node, node.keys,'\n', node.key_count)
        # insert k into node when no chance of splitting the root
        if node.isLeaf:
            i = node.key_count
            while i >= 1 and k < node.keys[i - 1]:
                node.keys[i] = node.keys[i - 1]
                i -= 1
            node.keys[i] = k
            node.key_count += 1
            return
        else:
            i = node.key_count
            while i >= 1 and k < node.keys[i - 1]:
                i -= 1
            # i = position of appropriate child

            if node.children[i].key_count == self.keys_max:
                self.splitChild(node, i)
                if k > node.keys[i]:
                    i += 1
            self.insertNormal(node.children[i], k)

## IQRA KA PART TO COMMENT BELOW THIS _ ALI KA PART ABOVE THIS ##

    def insert(self, k):
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
            self.insertNormal(temp_node, k)
        else:
            # If the root node does not need splitting, just insert the new key normally
            self.insertNormal(self.root, k)      

    def successorSimple(self, node, k):
        # Search for the position of the key in the current node
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
            
    def initiate(self, node):
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
