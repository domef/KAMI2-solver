import copy
import time

colors = ['red', 'green', 'white']
moves_number = 4
moves = []
found = False
count = 0

class Node:
    def __init__(self, id, color):
        self.id = id
        self.color = color
        self.adjacentNodes = set()

def move(graph, id, color):
    selected_node = next(x for x in graph if x.id == id)

    # for node in graph:
    #     if node.id == id:
    #         node.color = color
    #         break

    selected_node.color = color

    to_be_unified = set()
    to_be_unified.add(selected_node)
    
    # for node in graph:
    #     for adjacentNode in node.adjacentNodes:
    #         if(node.color == adjacentNode.color):
    #             to_be_unified.add(node)
    #             to_be_unified.add(adjacentNode)

    # for node in next(x.adjacentNodes for x in graph if x.id == id):
    #     for adjacentNode in node.adjacentNodes:
    #         if(node.color == adjacentNode.color):
    #             to_be_unified.add(node)
    #             to_be_unified.add(adjacentNode)

    # # the current node can maybe be saved before ---> maybe i can use a list instead of a set
    # to_be_unified = set(next(x.adjacentNodes for x in graph if x.id == id) | set([x for x in graph if x.id == id]))

    for node in next(x.adjacentNodes for x in graph if x.id == id):
        if(node.color == selected_node.color):
            to_be_unified.add(node)

    ids = [x.id for x in to_be_unified]

    newNode = Node('[' + '_'.join(ids) + ']', color)
    newNode.adjacentNodes = set.union(set([x for y in to_be_unified for x in y.adjacentNodes if x.id not in ids]))

    graph[:] = [x for x in graph if x.id not in ids]

    for node in graph:
        before = len(node.adjacentNodes)
        node.adjacentNodes = set([x for x in node.adjacentNodes if not x.id in ids])
        after = len(node.adjacentNodes)

        if before != after:
            node.adjacentNodes.add(newNode)
    
    graph.append(newNode)

def solve(graph, step = 1):
    if step > moves_number:
        return
        
    # if step > moves_number or len(set([x.color for x in graph])) > moves_number - step + 2:
    #     return

    global found
    # global count

    graph.sort(key=lambda x: len(x.adjacentNodes), reverse=True)
    # ordered_colors = colors.copy()

    for node in graph:
        # ordered_colors.sort()
        for color in colors:
            if color != node.color:
                new_graph = copy.deepcopy(graph)
                moves.append((node.id, color))
                move(new_graph, node.id, color)
                solve(new_graph, step + 1)

                if found == True:
                    return

                if len(new_graph) == 1:
                    for id, color in moves:
                        print (id + ": " + color)
                    
                    # print ()
                    # count += 1
                    # moves.pop()
                    found = True
                    return
                else:
                    moves.pop()

# if a node is adjacent to all the nodes of a certain color it should be chosen first

# sort nodes in descending order by number of adjacentNodes ---> OK
# sort colors in descending order by number of adjacentNode with that color

# more: if colors remaining are more then the moves remaining i cannot win ---> MAYBE

# optimize move() ---> ALMOST

# fix naming

if __name__ == '__main__':
    # total_time = 0
    # n = 1

    # for i in range(0, n):
    #     colors = ['red', 'yellow', 'blue']
    #     moves_number = 3
    #     moves = []
    #     found = False

    #     node1 = Node("1", "blue")
    #     node2 = Node("2", "red")
    #     node3 = Node("3", "yellow")
    #     node4 = Node("4", "blue")
    #     node5 = Node("5", "yellow")
    #     node6 = Node("6", "red")
    #     node7 = Node("7", "blue")

    #     node1.adjacentNodes = {node2}
    #     node2.adjacentNodes = {node1, node3, node4, node5}
    #     node3.adjacentNodes = {node2, node4, node6}
    #     node4.adjacentNodes = {node2, node3, node5, node6}
    #     node5.adjacentNodes = {node2, node4, node6}
    #     node6.adjacentNodes = {node3, node4, node5, node7}
    #     node7.adjacentNodes = {node6}

    #     graph = [node1, node2, node3, node4, node5, node6, node7]

    #     time1 = time.time()

    #     solve(graph)

    #     time2 = time.time()

    #     total_time += time2 - time1

    # print (total_time / n)

    # node1 = Node("1", "blue")
    # node2 = Node("2", "red")
    # node3 = Node("3", "yellow")
    # node4 = Node("4", "blue")
    # node5 = Node("5", "yellow")
    # node6 = Node("6", "red")
    # node7 = Node("7", "blue")

    # node1.adjacentNodes = {node2}
    # node2.adjacentNodes = {node1, node3, node4, node5}
    # node3.adjacentNodes = {node2, node4, node6}
    # node4.adjacentNodes = {node2, node3, node5, node6}
    # node5.adjacentNodes = {node2, node4, node6}
    # node6.adjacentNodes = {node3, node4, node5, node7}
    # node7.adjacentNodes = {node6}

    # graph = [node1, node2, node3, node4, node5, node6, node7]

    # solve(graph)

    # print (count)

    node1 = Node("1", "red")
    node2 = Node("2", "green")
    node3 = Node("3", "white")
    node4 = Node("4", "green")
    node5 = Node("5", "red")
    node6 = Node("6", "green")
    node7 = Node("7", "white")
    node8 = Node("8", "green")

    node1.adjacentNodes = {node2}
    node2.adjacentNodes = {node1, node3}
    node3.adjacentNodes = {node2, node4}
    node4.adjacentNodes = {node3, node5}
    node5.adjacentNodes = {node4, node6, node7}
    node6.adjacentNodes = {node5}
    node7.adjacentNodes = {node5, node8}
    node8.adjacentNodes = {node7}

    graph = [node1, node2, node3, node4, node5, node6, node7, node8]

    solve(graph)

    # print (count)