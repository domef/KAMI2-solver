import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import math
import copy
import re
import time
import collections
import itertools
import os

# - code refactor
# - put callbacks in MainApp
# - ids naming (a part from the firsts)
# - printing 'no solution' not in solve()
# - switch on_click to command?
# - implement save/load
# - GUI fix all shit

colors_in_graph = []
moves_number = 0
solution_steps = []
current_step = 0
found = False
count = 0
explored_states = 0

triangle_side_length = 50

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
        self.originalNodes = set()

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

        self.previous_button = tk.Button(self.frame, text='Prev', state=tk.DISABLED, command=on_previous_button_click)
        self.previous_button.pack()
        # self.previous_button.bind('<ButtonRelease-1>', on_previous_button_click)

        self.next_button = tk.Button(self.frame, text='Next', state=tk.DISABLED, command=on_next_button_click)
        self.next_button.pack()
        # self.next_button.bind('<ButtonRelease-1>', on_next_button_click)

        self.reset_button = tk.Button(self.frame, text='Reset')
        self.reset_button.pack()
        self.reset_button.bind('<ButtonRelease-1>', on_reset_button_click)

        self.reset_button = tk.Button(self.frame, text='Save')
        self.reset_button.pack()
        self.reset_button.bind('<ButtonRelease-1>', on_save_button_click)

        self.reset_button = tk.Button(self.frame, text='Load')
        self.reset_button.pack()
        self.reset_button.bind('<ButtonRelease-1>', on_load_button_click)

        self.solution_button = tk.Button(self.frame, text='Calculate solution')
        self.solution_button.pack()
        self.solution_button.bind('<ButtonRelease-1>', on_solution_button_click)

def on_canvas_click(event):
    value = app.selected_color.get()

    if value in COLORS:
        item = event.widget.find_withtag('current')
        event.widget.itemconfig(item,fill=COLORS[value])

    print ((event.widget.find_withtag('current')[0] - 1))

def on_solution_button_click(event):
    global moves_number
    global moves
    global colors_in_graph
    global found
    global solution_steps
    global explored_states
    global current_step

    moves = []
    solution_steps = []
    found = False
    explored_states = 0
    current_step = 0

    app.previous_button.config(state=tk.DISABLED)

    t1 = time.time()

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

    if not res:
        messagebox.showerror(title="ERROR", message='The level must be a connected component')
        return

    print ('length before: ' + str(len(graph)))

    fix_single_nodes(graph)

    unify(graph)

    print ('length after: ' + str(len(graph)))

    colors_in_graph = list(set([x.color for x in graph]))

    if len(graph) == 1:
        messagebox.showerror(title="ERROR", message='The level is already solved')
        return

    t2 = time.time()

    t = (t2 - t1) * 1000

    print (str(t))

    # app.print_explored_states()

    solve(graph)
    print ('explored states: ' + str(explored_states))
    # app.next_button.config(state=tk.NORMAL)
    
def on_reset_button_click(event):    
    global current_step
    global solution_steps

    solution_steps = []
    current_step = 0

    items = app.canvas.find_all()

    for item in items:
        app.canvas.itemconfigure(item, fill='white')

    app.previous_button.config(state=tk.DISABLED)
    app.next_button.config(state=tk.DISABLED)

def on_previous_button_click():
    global current_step
    global solution_steps

    current_step -= 1

    if current_step == 0:
        app.previous_button.config(state=tk.DISABLED)

    items = solution_steps[current_step]

    for i in range(0, len(items)):
        app.canvas.itemconfig(i + 1, fill=solution_steps[current_step][i])

    

    if str(app.next_button['state']) == 'disabled':
        app.next_button.config(state=tk.NORMAL)    

def on_next_button_click():
    global current_step
    global solution_steps

    current_step += 1

    if current_step == len(solution_steps) - 1:
        app.next_button.config(state=tk.DISABLED)
    
    items = solution_steps[current_step]

    for i in range(0, len(items)):
        app.canvas.itemconfig(i + 1, fill=solution_steps[current_step][i])

    if str(app.previous_button['state']) == 'disabled':
        app.previous_button.config(state=tk.NORMAL) 

def on_save_button_click(event):
    current_state  = [(item, app.canvas.itemcget(item, 'fill')) for item in app.canvas.find_all()]

    file_name = tk.simpledialog.askstring('Save', 'Insert the file name')

    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + os.sep + 'tests' + os.sep + file_name + '.txt', 'w') as f:
        f.writelines('%s %s\n' % x for x in current_state)

def on_load_button_click(event):
    file_name = tk.simpledialog.askstring('Load', 'Insert the file name')

    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + os.sep + 'tests' + os.sep + file_name + '.txt', 'r') as f:
        lines = f.readlines()

    lines = [(x.strip().split()[0], x.strip().split()[1]) for x in lines]

    for item, color in lines:
        app.canvas.itemconfig(item, fill=color)

def create_triangles(side_length):
    result = []
    half_width = int(side_length // 2)
    # height = int(side_length * math.sqrt(3) / 2)
    height = side_length
    max_width = 15 * side_length
    max_height = 10 * height

    for i in range(0, max_height, height):
        if (i // height) % 2 == 0: # colonna dispari
            for j in range(0, max_width-half_width, half_width):
                if j % side_length == 0: # destra
                    triangle = (i-height//2+1, j-half_width+1, i+height//2+1, j+1, i-height//2+1, j+half_width+1)
                else: # sinistra
                    triangle = (i-height//2+1, j+1, i+height//2+1, j+half_width+1, i+height//2+1, j-half_width+1)
                
                result.append(triangle)
        else: # colonna pari
            for j in range(half_width, max_width, half_width):
                if j % side_length == 0: # destra
                    triangle = (i-height//2+1, j-2*half_width+1, i+height//2+1+2, j-half_width+2+1-1, i-height//2+1, j+1)
                else: # sinistra
                    triangle = (i-height//2+1, j-half_width+1, i+height//2+1, j+1, i+height//2+1, j-2*half_width+1)
                
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

#OPRTIMIZE like move()
def unify_node(graph, id):
    selected_node = next(x for x in graph if x.id == id)

    to_be_unified = set(find_same_color_node(selected_node))
    to_be_unified.add(selected_node)

    ids = [x.id for x in to_be_unified]

    newNode = Node('[' + '_'.join(str(ids)) + ']', selected_node.color)
    newNode.adjacentNodes = set.union(set([x for y in to_be_unified for x in y.adjacentNodes if x.id not in ids]))
    newNode.originalNodes = set(ids)

    graph[:] = [x for x in graph if x.id not in ids]

    for node in graph:
        before = len(node.adjacentNodes)
        node.adjacentNodes = set([x for x in node.adjacentNodes if not x.id in ids])
        after = len(node.adjacentNodes)

        if before != after:
            node.adjacentNodes.add(newNode)
    
    graph.append(newNode)

def unify(graph):
    unified = False

    while not unified:
        for node in graph:
            if node.color in [x.color for x in node.adjacentNodes]:
                unify_node(graph, node.id)
                break
        else:
            unified = True

# @profile
def get_state(graph):
    result = ['white'] * 290

    for item in graph:
        for index in item.originalNodes:
            result[index] = item.color

    return result

def fix_single_nodes(graph):
    for node in graph:
        if node.color not in [x.color for x in node.adjacentNodes]:
            node.originalNodes.add(node.id)

# @profile
def move(graph, id, color):
    selected_node = next(x for x in graph if x.id == id)
    
    selected_node.color = color

    # to_be_unified = set()
    # to_be_unified.add(selected_node)
    
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


    # for node in selected_node.adjacentNodes:
    #     if(node.color == selected_node.color):
    #         to_be_unified.add(node)

    # to_be_unified = set([node for node in selected_node.adjacentNodes if node.color == selected_node.color])
    # to_be_unified.add(selected_node)

    to_be_unified = {node for node in selected_node.adjacentNodes if node.color == selected_node.color} | {selected_node}

    ids = [x.id for x in to_be_unified]

    newNode = Node('[' + '_'.join(str(ids)) + ']', color)
    # newNode.adjacentNodes = set.union(set([x for y in to_be_unified for x in y.adjacentNodes if x.id not in ids]))
    # newNode.originalNodes = set.union(set([x for y in to_be_unified for x in y.originalNodes]))

    newNode.adjacentNodes = set.union({x for y in to_be_unified for x in y.adjacentNodes if x.id not in ids})
    newNode.originalNodes = set.union({x for y in to_be_unified for x in y.originalNodes})

    graph[:] = [x for x in graph if x.id not in ids]

    for node in newNode.adjacentNodes:
        # node.adjacentNodes = set([x for x in node.adjacentNodes if not x.id in ids]) | {newNode}
        node.adjacentNodes = {x for x in node.adjacentNodes if not x.id in ids} | {newNode}
    
    graph.append(newNode)

def is_color_single_node(graph):
    colors_counter = collections.Counter([x.color for x in graph])

    return any(x == 1 for x in colors_counter.values())

# @profile
def solve(graph, step = 1):
    if step == 1:
        solution_steps.append(get_state(graph))

    if step > moves_number or len(set([x.color for x in graph])) > moves_number - step + 2:
        if step == 1:
            messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')
        return

    # if step > moves_number or len(set([x.color for x in graph])) > moves_number - step + 2 or (len(set([x.color for x in graph])) == moves_number - step + 2 and not is_color_single_node(graph)):
    #     if step == 1:
    #         messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')
    #     return

    global found
    # global count
    global explored_states

    graph.sort(key=lambda x: len(x.adjacentNodes), reverse=True)



    # graph.sort(key=lambda x: collections.Counter([adj.color for adj in x.adjacentNodes]).most_common(1)[0][1], reverse=True)



    # graph_color_counter = collections.Counter([x.color for x in graph])

    # for item in graph:
    #     adjacent_color_counter = collections.Counter([x.color for x in item.adjacentNodes])
    #     collapsible = set(graph_color_counter.items()) & set(adjacent_color_counter.items())

    #     if len(collapsible) > 0:
    #         graph.pop(graph.index(item))
    #         graph.insert(0, item)
    #         break

    for node in graph:
        ordered_colors = {x.color for x in node.adjacentNodes if x.color != node.color}


        # ordered_colors = [x.color for x in node.adjacentNodes]
        # ordered_colors.sort(key=lambda x: collections.Counter([adj.color for adj in node.adjacentNodes])[x], reverse=True)

        # for color in colors_in_graph:
        for color in ordered_colors:

            # MAYBE I CAN REMOVE THE IF
            if color != node.color:
                new_graph = copy.deepcopy(graph)
                move(new_graph, node.id, color)
                solution_steps.append(get_state(new_graph))
                explored_states += 1
                solve(new_graph, step + 1)

                if found:
                    return

                if len(new_graph) == 1:
                    app.next_button.config(state=tk.NORMAL)
                    
                    found = True
                    return
                else:
                    solution_steps.pop()

    if step == 1:
        messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')

def solve2(graph, step = 1):
    if step == 1:
        solution_steps.append(get_state(graph))

    if step > moves_number or len(set([x.color for x in graph])) > moves_number - step + 2:
        if step == 1:
            messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')
        return

    # if step > moves_number or len(set([x.color for x in graph])) > moves_number - step + 2 or (len(set([x.color for x in graph])) == moves_number - step + 2 and not is_color_single_node(graph)):
    #     if step == 1:
    #         messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')
    #     return

    global found
    global explored_states

    pairs = list(itertools.product(graph, {x.color for x in graph}))

    pairs.sort(key=lambda x: len([y.color for y in x[0].adjacentNodes if y.color == x[1]]), reverse=True)

    # graph_color_counter = collections.Counter([x.color for x in graph])

    # for node, color in pairs:
    #     count = len([x.color for x in node.adjacentNodes if x.color == color])
    #     collapsible = graph_color_counter.items() & set((color, count))

    #     if len(collapsible) > 0:
    #         pairs.pop(pairs.index((node, color)))
    #         pairs.insert(0, (node, color))
    #         break # i can look for all collapsing

    for pair in pairs:
        new_graph = copy.deepcopy(graph)
        move(new_graph, pair[0].id, pair[1])
        solution_steps.append(get_state(new_graph))
        explored_states += 1
        solve(new_graph, step + 1)

        if found:
            return

        if len(new_graph) == 1:
            app.next_button.config(state=tk.NORMAL)
            found = True
            return
        else:
            solution_steps.pop()

    if step == 1:
        messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()