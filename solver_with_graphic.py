import tkinter as tk
from tkinter import messagebox
import math
import copy
import re

colors = []
moves_number = 0
moves = []
found = False
count = 0

triangle_side_length = 40

COLORS = {
    1: 'blue',
    2: 'red',
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

class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('KAMI2 Solver')
        self.parent.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.parent, height=14*triangle_side_length, width=9*triangle_side_length, bg='white')
        self.canvas.grid(row=0, column=0)
        self.canvas.bind('<Button-1>', on_canvas_click)

        self.triangles = create_triangles(triangle_side_length)

        for item in self.triangles:
            self.canvas.create_polygon(item, fill='white', outline='black', width=1)

        self.frame = tk.Frame(self.parent, bg='black')
        self.frame.grid(row=0, column=1, sticky=tk.N+tk.S+tk.W+tk.E)

        self.label_warning = tk.Label(self.frame, height=3, text='Warning, the level must be a CONNECTED COMPONENT!', bg='white')
        self.label_warning.pack()
        self.blinking()

        self.selected_color = tk.IntVar()

        self.radio_buttons = []

        for key, value in COLORS.items():
            radio_button = tk.Radiobutton(self.frame, text=value.upper(), variable=self.selected_color, value=key, bg=value, indicatoron=0)
            radio_button.pack(fill=tk.X)
            self.radio_buttons.append(radio_button)

        self.label_warning_color = tk.Label(self.frame, height=2, text='The WHITE color means EMPTY CELL', bg='white')
        self.label_warning_color.pack()

        self.entry = tk.Entry(self.frame)
        self.entry.insert(tk.END, 'Insert the number of moves')
        self.entry.pack(fill=tk.X)

        self.button = tk.Button(self.frame, text='Calculate solution')
        self.button.pack()
        self.button.bind('<ButtonRelease-1>', on_button_click)

    def blinking(self):
        current_color = self.label_warning.cget('bg')
        next_color = 'white' if current_color == 'red' else 'red'
        self.label_warning.config(bg=next_color)

        self.parent.after(400, self.blinking)

def on_canvas_click(event):
    value = app.selected_color.get()

    if value in COLORS:
        item = event.widget.find_withtag('current')
        event.widget.itemconfig(item,fill=COLORS[value])

    print ((event.widget.find_withtag('current')[0] - 1))

def on_button_click(event):
    global moves_number
    global moves
    global colors
    global found

    moves = []
    found = False

    res, value = get_moves_number()

    if not res:
        messagebox.showerror(title="ERROR", message='The moves number must be an integer')
        return
    
    if int(value) == 0:
        messagebox.showerror(title="ERROR", message='The moves number must be greater then 0')
        return

    moves_number = int(value)

    graph = create_graph()

    if len(graph) == 0:
        messagebox.showerror(title="ERROR", message='The level must contain at least one piece')
        return

    # print ('graph: ')

    # for node in graph:
    #     print (str(node.id))

    # print()

    res = is_connected_component(graph)

    print ('is connected: ' + str(res))

    if not res:
        messagebox.showerror(title="ERROR", message='The level must be a connected component')
        return

    print ('length before: ' + str(len(graph)))

    unify(graph)

    print ('length after: ' + str(len(graph)))

    colors = list(set([x.color for x in graph]))

    if len(graph) == 1:
        messagebox.showerror(title="ERROR", message='The level is already solved')
        return

    solve(graph)

def test(event):

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

def get_moves_number():
    value = app.entry.get()

    return re.match('^[0-9]+$', value), value

def create_graph():
    graph = []
    items = app.canvas.find_all()

    for item in items:
        node = Node(item - 1, app.canvas.itemcget(item, 'fill'))
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
            else:
                if graph[node.id + 1].color != 'white': 
                    temp.add(graph[node.id + 1])

                if graph[node.id - 1].color != 'white':
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

def depth_first(node, visited):
    for adjacentNode in node.adjacentNodes:
        if adjacentNode.id not in visited:
            visited.append(adjacentNode.id)
            depth_first(adjacentNode, visited)

def depth_first2(node, visited):
    for adjacentNode in node.adjacentNodes:
        if adjacentNode not in visited and node.color == adjacentNode.color:
            visited.append(adjacentNode)
            depth_first2(adjacentNode, visited)

def is_connected_component(graph):
    visited = []

    node = graph[0]
    visited.append(node.id)

    depth_first(node, visited)

    return len(visited) == len(graph)

def find_same_color_node(node):
    result = []

    result.append(node)

    depth_first2(node, result)

    return result

def unify_node(graph, id):
    selected_node = next(x for x in graph if x.id == id)

    to_be_unified = set(find_same_color_node(selected_node))
    to_be_unified.add(selected_node)

    ids = [x.id for x in to_be_unified]

    newNode = Node('[' + '_'.join(str(ids)) + ']', selected_node.color)
    newNode.adjacentNodes = set.union(set([x for y in to_be_unified for x in y.adjacentNodes if x.id not in ids]))

    graph[:] = [x for x in graph if x.id not in ids]

    for node in graph:
        before = len(node.adjacentNodes)
        node.adjacentNodes = set([x for x in node.adjacentNodes if not x.id in ids])
        after = len(node.adjacentNodes)

        if before != after:
            node.adjacentNodes.add(newNode)
    
    graph.append(newNode)

def unify(graph):
    # depth first per trovare gruppo di nodi dello stesso colore ---> unifico
    # ogni volta cerco un nodo con un adiacenza dello stesso colore e scelgo quel nodo per iniziazare la ricerca
    # se non lo trovo ho finito
    unified = False

    while not unified:
        for node in graph:
            if node.color in [x.color for x in node.adjacentNodes]:
                unify_node(graph, node.id)
                break
        else:
            unified = True

def unify_old(graph):
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

    newNode = Node('[' + '_'.join(str(ids)) + ']', color)
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
        for color in list(colors):
            if color != node.color:
                new_graph = copy.deepcopy(graph)
                moves.append((node.id, color))
                move(new_graph, node.id, color)
                solve(new_graph, step + 1)

                if found == True:
                    return

                if len(new_graph) == 1:
                    for id, color in moves:
                        print (str(id) + ": " + color)
                    
                    # print ()
                    # count += 1
                    # moves.pop()
                    found = True
                    return
                else:
                    moves.pop()

    print('no solution can be found with ' + str(moves_number) + ' moves')

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()