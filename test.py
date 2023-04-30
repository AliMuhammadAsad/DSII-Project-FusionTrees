from fusion_tree import *

# if __name__ == "__main__":
#     # create a fusion tree of degree 3
#     tree = FusionTree(243)
    
#     tree.insert(1)
#     tree.insert(5)
#     tree.insert(15)
#     tree.insert(16)
#     tree.insert(20)
#     tree.insert(25)
#     tree.insert(4)
#     tree.insert(14)

#     # tree.insert((1, "A"))
#     # tree.insert((5, "E"))
#     # tree.insert((15, "O"))
#     # tree.insert((16, "P"))
#     # tree.insert((20, "T"))
#     # tree.insert((25, "Y"))
#     # tree.insert((4, "D"))
#     # tree.insert((14, "N"))
#     tree.initiateTree()
#     # the tree formed should be like:
#     #      [| 5  | |  16 |]
#     #      /      |       \
#     #     /       |        \
#     # [1, 4]   [14,15]     [20, 25])

#     for i in tree.root.children:
#         if i is not None:
#             print (i, " = ", i.keys)
#             if not i.isLeaf:
#                 for j in i.children:
#                     if j is not None:
#                         print( j.keys)

#     print("\nKeys stored are:")
#     # print("1, 4, 5, 14, 15, 16, 20, 25\n")
#     print(sorted(tree.keez))
#     print("Predecessors:")
#     for i in range(26):
#         print(i, "------------------->", tree.predecessor(i), sep = '\t')
#     print("Successor:")
#     for i in range(26):
#         print(i, "------------------->", tree.successor(i), sep = '\t')

#     print(f"Length of tree is {tree.size}")

#     # print(tree.root.children[0].key_count)
#     # print(tree.root.children[0].isLeaf)
#     # tree.delete(4)
#     # tree.delete(20)
#     # the tree formed should be like:
#     #      [| 5  | |  16 |]
#     #      /      |       \
#     #     /       |        \
#     #  [1]       [15]      [25]

# if __name__ == "__main__":
#     tree = FusionTree(243)
#     lst = [['PS1000', 'Animal Farm', 'Roman A clef', '8390.53', '3963'], ['PC1001', 'A Clockwork Orange', 'Science Fiction', '4053.65', '11223'], ['MC1002', 'The Plague', 'Existentialism', '2741.57', '5958'], ['TC1003', 'A Fire Upon the Deep', 'Hard science fiction', '913.34', '344']]

#     for i in lst:
#         tree.insert(i)
#     tree.initiateTree()
    
#     for i in tree.root.children:
#         if i is not None:
#             print (i, " = ", i.keys)
#             if not i.isLeaf:
#                 for j in i.children:
#                     if j is not None:
#                         print( j.keys)
    
#     print(f"Tree size is {tree.size}")
#     print(tree.keez)
#     sorted_keez = sorted(tree.keez, key = lambda x: x[0])
#     print(f"Sorted keys are : {sorted_keez}")


if __name__ == "__main__":
    tree = FusionTree(243)
    book_lst = []
    f = open("Books_Data.csv", encoding="utf8")
    # f = open("books.csv", encoding="utf8")
    f.readline()
    count = 0
    for i in f:
        i = i.split(",")
        lst = [word.strip() for word in i]
        lst = [int(lst[0])] + lst[1:]
        # title = lst[1]
        # ascii_list = [ord(char) for char in title]
        # s = ""
        # for i in ascii_list:
        #     s += str(i)
        # s = int(s)
        # lst.insert(0, s)
        # print(lst)
        # hval = compute_hash(lst[1])
        # newlst = [hval] + lst
        # t = (newlst[0], newlst[1], newlst[2], newlst[3], newlst[4], newlst[5])
        book_lst.append(lst)
        # book_lst.append(t)
        count += 1
        # if count == 9: break
        # tree.insert(lst)
    f.close()
    # print(book_lst)
    for book in book_lst:
        print(book)
        tree.insert(book)
    tree.initiateTree()
    print(f"The tree is of size {tree.size}")
    # print(f"They tree has elements {sorted(tree.keez, key = lambda x: x[0])}")

    for i in tree.root.children:
        if i is not None:
            print(i, " has keys: ", i.keys)
            if not i.isLeaf:
                for j in i.children:
                    if j is not None:
                        print(j, " has keys :", j.keys)
