from fusion_tree import *

if __name__ == "__main__":
    # create a fusion tree of degree 3
    tree = FusionTree(243)
    
    tree.insert(1)
    tree.insert(5)
    tree.insert(15)
    tree.insert(16)
    tree.insert(20)
    tree.insert(25)
    tree.insert(4)
    print(tree.root.keys)
    for i in tree.root.children:
        if i is not None:
            print (i, " = ", i.keys)
            if not i.isLeaf:
                for j in i.children:
                    if j is not None:
                        print( j.keys)
    tree.initiateTree()
    # the tree formed should be like:
    #      [| 5  | |  16 |]
    #      /      |       \
    #     /       |        \
    # [1, 4]     [15]     [20, 25]
    print("\nKeys stored are:")
    print("1, 4, 5, 15, 16, 20, 25\n")
    print("Predecessors:")
    for i in range(26):
        print(i, "------------------->", tree.predecessor(i), sep = '\t')
    print("Successor:")
    for i in range(26):
        print(i, "------------------->", tree.successor(i), sep = '\t')