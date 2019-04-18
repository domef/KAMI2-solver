import tkinter as tk
import math
import copy
import re

colors = ['red', 'green', 'white']
moves_number = 4
moves = []
found = False
count = 0

COLORS = {
    1: 'red',
    2: 'blue',
    3: 'yellow',
    4: 'green',
    5: 'orange',
    6: 'white',
}

class Node:
    def __init__(self, id, color):
        self.id = id
        self.color = color
        self.adjacentNodes = set()

def on_canvas_click(event):
    value = selected_color.get()

    if value in COLORS:
        item = event.widget.find_withtag('current')
        event.widget.itemconfig(item,fill=COLORS[value])

    print ((event.widget.find_withtag('current')[0] - 1))

# def on_motion(event):
#     print (event.widget.find_withtag('current'))

def test(event):
    # item1 = event.widget.find_withtag('t1')

    # print (event.widget.itemcget(item1, option='fill'))

    # item2 = event.widget.find_withtag('t2')

    # print (item2)

    # for triangle in triangles:
    #     print (triangle)
    #     print (event.widget.itemcget(triangle, 'tag'))

    # item = event.widget.find_withtag('current')
    # print (event.widget.itemcget(item, 'fill'))

    # items = canvas.find_all()

    # for item in items:
    #     print (type(item))
    #     print (canvas.itemcget(item, 'fill'))

    # print ((event.widget.find_withtag('current')[0] - 1))

    graph = create_graph()

    for node in graph:
        print (node.id)
        temp = ''

        for adj in node.adjacentNodes:
            if hasattr(adj, 'id'):
                temp += str(adj.id)
                temp += ' '
            else:
                temp += '_ '

        print (temp)
        print ()

        # print (len(node.adjacentNodes))

def blinking():
    current_color = label_warning.cget('bg')
    next_color = 'white' if current_color == 'red' else 'red'
    label_warning.config(bg=next_color)

    root.after(400, blinking)

# FIX DOUBLE LINE
def create_triangles(side_length):
    result = []
    half_width = int(side_length / 2)
    # height = int(side_length * math.sqrt(3) / 2)
    height = side_length
    max_width = 15 * side_length
    max_height = 10 * height

    for i in range(0, max_height, height):
        if (i / height) % 2 == 0: # colonna dispari
            for j in range(0, max_width-half_width, half_width):
                if j % side_length == 0: # destra
                    triangle = (i-height/2+1, j-half_width+1, i+height/2+1, j+1, i-height/2+1, j+half_width+1)
                else: # sinistra
                    triangle = (i-height/2+1, j+1, i+height/2+1, j+half_width+1, i+height/2+1, j-half_width+1)
                
                result.append(triangle)
        else: # colonna pari
            for j in range(half_width, max_width, half_width):
                if j % side_length == 0: # destra
                    #
                    # PROBLEM
                    #
                    triangle = (i-height/2+1, j-2*half_width+1, i+height/2+1, j-half_width+2+1, i-height/2+1, j+1)
                else: # sinistra
                    triangle = (i-height/2+1, j-half_width+1, i+height/2+1, j+1, i+height/2+1, j-2*half_width+1)
                
                result.append(triangle)

    return result

def get_moves_number(text_box):
    value = text_box.get('1.0', tk.END)

    if re.match('^[0-9]+$', value):
        return value

def on_button_click(event):
    # check text moves number
    # create graph
    # is connected component
    # unify
    # solve
    pass

def create_graph():
    graph = []
    items = canvas.find_all()

    for item in items:
        node = Node(item - 1, canvas.itemcget(item, 'fill'))
        graph.append(node)

    for node in graph:
        if node.color != 'white':
            temp = set()

            col = node.id // 29
            n = node.id % 29

            if n == 0 and graph[node.id + 1].color != 'white':
                temp.add(graph[node.id + 1])
            elif n == 28 and graph[node.id - 1].color != 'white':
                temp.add(graph[node.id - 1])
            elif graph[node.id + 1].color != 'white' and graph[node.id - 1].color != 'white':
                temp.add(graph[node.id + 1])
                temp.add(graph[node.id - 1])

            if col % 2 == 0: #prima
                if n % 2 == 0: # pari -29
                    if node.id - 29 >= 0 and graph[node.id - 29].color != 'white':
                        temp.add(graph[node.id - 29])
                else: # +29
                    if node.id + 29 <= 289 and graph[node.id + 29].color != 'white':
                        temp.add(graph[node.id + 29])
            else: # seconda
                if n % 2 == 0: # pari +29
                    if node.id + 29 <= 289 and graph[node.id + 29].color != 'white':
                        temp.add(graph[node.id + 29])
                else: # -29
                    if node.id - 29 >= 0 and graph[node.id - 29].color != 'white':
                        temp.add(graph[node.id - 29])

            node.adjacentNodes = temp

    graph = [x for x in graph if x.color != 'white']

    return graph

visited = []

def depth_first(node):
    for adjacentNode in node.adjacentNodes:
        if adjacentNode.id not in visited:
            visited.append(adjacentNode.id)
            depth_first(adjacentNode)

# in teoria posso chiamare solo con un nodo se è un connected component
def is_connected_component(graph):    
    for node in graph:
        if node.id not in visited:
            visited.append(node.id)
            depth_first(node)

    return visited == len(graph)

# utilizzare sempre move?
def unify(graph):
    length = -1

    while length != len(graph):
        length = len(graph)

        for node in graph:
            move(graph, node.id, node.color)
            
            if length != len(graph):
                break

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
        for color in list(COLORS.values()):
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

if __name__ == "__main__":
    root = tk.Tk()
    root.title('KAMI2 Solver')

    # canvas = tk.Canvas(root, height=(15-1)*40, width=(10-1)*int(40*math.sqrt(3)/2), bg='white')
    canvas = tk.Canvas(root, height=(15-1)*40, width=(10-1)*40, bg='white')
    canvas.grid(row=0, column=0)
    canvas.bind('<Button-1>', on_canvas_click)

    # button = tk.Button(root, text='click')
    # button.grid(column=2, row=0)

    frame = tk.Frame(root, bg='black')
    frame.grid(row=0, column=1, sticky=tk.N+tk.S+tk.W+tk.E)
    # frame.pack()

    label_warning = tk.Label(frame, height=3, text='Warning, the level must be a CONNECTED COMPONENT!', bg='white')
    label_warning.pack()

    selected_color = tk.IntVar()
    radio_buttons = []

    for key, value in COLORS.items():
        radio_button = tk.Radiobutton(frame, text=value.upper(), variable=selected_color, value=key, bg=value, indicatoron=0)
        radio_button.pack(fill=tk.X)
        radio_buttons.append(radio_button)

    label_warning_color = tk.Label(frame, height=2, text='The WHITE color means EMPTY CELL', bg='white')
    label_warning_color.pack()

    entry = tk.Entry(frame)
    entry.insert(tk.END, 'Insert the number of moves')
    entry.pack(fill=tk.X)

    button = tk.Button(frame, text='Calculate solution')
    button.pack()
    button.bind('<Button-1>', on_button_click)

    # color1 = tk.Radiobutton(frame, text='RED', variable=selectedColor, value=1, indicatoron=0)
    # color2 = tk.Radiobutton(frame, text='BLUE', variable=selectedColor, value=2, indicatoron=0)
    # color3 = tk.Radiobutton(frame, text='YELLOW', variable=selectedColor, value=3, indicatoron=0)
    # color4 = tk.Radiobutton(frame, text='GREEN', variable=selectedColor, value=4, indicatoron=0)
    # color5 = tk.Radiobutton(frame, text='ORANGE', variable=selectedColor, value=5, indicatoron=0)
    # color6 = tk.Radiobutton(frame, text='EMPTY', variable=selectedColor, value=6, indicatoron=0)

    # color1.grid(column=0, row=0, sticky=tk.W+tk.E)
    # color2.grid(column=1, row=0, sticky=tk.W+tk.E)
    # color3.grid(column=0, row=1, sticky=tk.W+tk.E)
    # color4.grid(column=1, row=1, sticky=tk.W+tk.E)
    # color5.grid(column=0, row=2, sticky=tk.W+tk.E)
    # color6.grid(column=1, row=2, sticky=tk.W+tk.E)

    # color1.pack(fill=tk.X)
    # color2.pack(fill=tk.X)
    # color3.pack(fill=tk.X)
    # color4.pack(fill=tk.X)
    # color5.pack(fill=tk.X)
    # color6.pack(fill=tk.X)    

    # triangle1 = canvas.create_polygon(5,5,100,5,5,100, fill='blue', outline='black', width=2, tag='t1')
    # triangle2 = canvas.create_polygon(105,5,200,5,105,100, fill='green', tag='t2')
    
    # triangles.append(triangle1)
    # triangles.append(triangle2)

    triangles = create_triangles(40)

    for item in triangles:
        canvas.create_polygon(item, fill='white', outline='black', width=1)

    
    # canvas.bind('<B1-Motion>', on_motion)

    canvas.bind('<Button-3>', test)

    blinking()

    root.mainloop()