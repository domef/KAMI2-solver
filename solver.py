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
import string
import timeit
import numpy as np

# - code refactor
# - put callbacks in MainApp
# - ids naming (a part from the firsts)
# - printing 'no solution' not in solve()
# - switch on_click to command?
# - color by moving
# - GUI fix all shit
# - save/load name filter
# - global vars?
# - save/load if file exist and others
# - put global vars in dict
# - create function to reset all global
# - create graph class
# - reorder in solve?
# - process/thread for executing solve
# - find new hash, new structure to make calculation more efficient
# - solve: refactor anche per non usare found globale
# - calcolare meglio explored nodes

# - se sposto dfs sotto non va
# - spostare anche counter degli stati?



#############################################
# - usare history anche nell'if iniziale? - #
#############################################

# - getstate and save/load and other ---> same method for current state

colors_in_graph = []
moves_number = 0
solution_steps = []
current_step = 0
found = False
explored_states = 0
history_dictionary = dict()
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
        self.adjacent_nodes = set()
        self.original_nodes = set()

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

    # print ((event.widget.find_withtag('current')[0] - 1))

# @ profile
def on_solution_button_click(event):
    global moves_number
    global moves
    global colors_in_graph
    global found
    global solution_steps
    global explored_states
    global current_step
    global history_dictionary

    moves = []
    solution_steps = []
    found = False
    explored_states = 0
    current_step = 0
    history_dictionary = dict()

    app.previous_button.config(state=tk.DISABLED)
    app.next_button.config(state=tk.DISABLED)

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

    res = is_connected_component(graph)

    if not res:
        messagebox.showerror(title="ERROR", message='The level must be a connected component')
        return

    print('nodes before: ' + str(len(graph)))

    fix_single_nodes(graph)

    unify(graph)

    print('nodes after: ' + str(len(graph)))

    colors_in_graph = list(set([x.color for x in graph]))

    print('moves: ' + str(moves_number))
    print('colors: ' + str(len(colors_in_graph)))

    if len(graph) == 1:
        messagebox.showerror(title="ERROR", message='The level is already solved')
        return

    # for _ in range(100):
    #     test(graph)

    # print('hash: ' + str(calc_hash(graph)))

    # t1 = time.time()
    # for _ in range(10):
    #     h = calc_hash(graph)
    #     # state_hash(graph)
    # t2 = time.time()
    # print('hash: ' + str(h))
    # print('time hash: ' + str((t2 - t1) * 1000 / 10))

    # for _ in range(100):
    #     get_state(graph)
    #     get_state2(graph)
    #     get_state3(graph)

    # solution_steps.append(get_state(graph))

    t1 = time.time()

    solve2_dfs(graph)
    

    t2 = time.time()

    if len(solution_steps) == 0:
        messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')
    else:
        solution_steps.insert(0, get_state(graph))
        app.next_button.config(state=tk.NORMAL)

    if explored_states != 0:
        print('explored nodes: ' + str(explored_states))
        print('time per node: ' + str(((t2 - t1) / explored_states) * 1000))
    # else:
    #     print('explored nodes: 0')

    print()
    print(len(history_dictionary))
    
def on_reset_button_click(event):    
    global current_step
    global solution_steps
    global history_dictionary

    solution_steps = []
    current_step = 0
    history_dictionary = dict()

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

    file_name = tk.simpledialog.askstring('Save', 'Insert the level name')

    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + os.sep + 'levels' + os.sep + file_name, 'w') as f:
        f.writelines('%s %s\n' % x for x in current_state)

def on_load_button_click(event):
    global solution_steps
    global current_step
    global history_dictionary

    solution_steps = []
    current_step = 0
    history_dictionary = dict()

    app.previous_button.config(state=tk.DISABLED)
    app.next_button.config(state=tk.DISABLED)

    file_name = tk.simpledialog.askstring('Load', 'Insert the level name')

    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + os.sep + 'levels' + os.sep + file_name, 'r') as f:
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

            node.adjacent_nodes = temp

    graph = [x for x in graph if x.color != 'white']

    return graph

def depth_first(node, visited):
    for adjacent_node in node.adjacent_nodes:
        if adjacent_node.id not in visited:
            visited.append(adjacent_node.id)
            depth_first(adjacent_node, visited)

def depth_first2(node, visited):
    for adjacent_node in node.adjacent_nodes:
        if adjacent_node not in visited and node.color == adjacent_node.color:
            visited.append(adjacent_node)
            depth_first2(adjacent_node, visited)

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

#OPTIMIZE like move()
def unify_node(graph, id):
    selected_node = next(x for x in graph if x.id == id)

    to_be_unified = set(find_same_color_node(selected_node))
    to_be_unified.add(selected_node)

    ids = [x.id for x in to_be_unified]

    newNode = Node(min(ids), selected_node.color)
    newNode.adjacent_nodes = set.union(set([x for y in to_be_unified for x in y.adjacent_nodes if x.id not in ids]))
    newNode.original_nodes = set(ids)

    graph[:] = [x for x in graph if x.id not in ids]

    for node in graph:
        before = len(node.adjacent_nodes)
        node.adjacent_nodes = set([x for x in node.adjacent_nodes if not x.id in ids])
        after = len(node.adjacent_nodes)

        if before != after:
            node.adjacent_nodes.add(newNode)
    
    graph.append(newNode)

#SORT GRAPH?
def unify(graph):
    unified = False

    while not unified:
        for node in graph:
            if node.color in [x.color for x in node.adjacent_nodes]:
                unify_node(graph, node.id)
                break
        else:
            unified = True

# # @ profile
# def get_state(graph):
#     state = ['white'] * 290

#     for item in graph:
#         for index in item.original_nodes:
#             state[index] = item.color

#     return state

# # @ profile
# def get_state2(graph):
#     temp = {j:i.color for i in graph for j in i.original_nodes}
#     return [temp.get(i, 'white') for i in range(290)]

# # @ profile
# def get_state3(graph):
#     x = np.empty(290, dtype='<U6')
#     x.fill('white')
#     for item in graph:
#         x[list(item.original_nodes)] = item.color
#     return x.tolist()

# @ profile
def get_state(graph):
    temp = {x: y.color for y in graph for x in y.original_nodes}
    return [temp.get(x, 'white') for x in range(290)]

def fix_single_nodes(graph):
    for node in graph:
        if node.color not in [x.color for x in node.adjacent_nodes]:
            node.original_nodes.add(node.id)

# @ profile
def move(graph, selected_node, color):
    to_be_unified = {x for x in selected_node.adjacent_nodes if x.color == color} | {selected_node}
    ids = [x.id for x in to_be_unified]

    new_node = Node(min(ids), color)
    new_node.adjacent_nodes = {x for y in to_be_unified for x in y.adjacent_nodes if x.id not in ids}
    new_node.original_nodes = {x for y in to_be_unified for x in y.original_nodes}

    # graph = list(filter(lambda x: x.id not in ids, graph))
    graph[:] = [x for x in graph if x.id not in ids]
    graph.append(new_node)

    for node in new_node.adjacent_nodes:
        node.adjacent_nodes = {x for x in node.adjacent_nodes if not x.id in ids} | {new_node}    

    return to_be_unified, new_node

# @ profile
def unmove(graph, old_nodes, new_node):
    graph.remove(new_node)
    graph.extend(old_nodes)

    old_adjacent_nodes = {x for y in old_nodes for x in y.adjacent_nodes if x.id not in [x.id for x in old_nodes]}

    for node in old_adjacent_nodes:
        node.adjacent_nodes.remove(new_node)
        node.adjacent_nodes |= {x for x in old_nodes if node in x.adjacent_nodes}

# @ profile
def is_color_single_node(colors):
    colors_counter = collections.Counter(colors)

    return any(x == 1 for x in colors_counter.values())

# @profile
def state_hash(graph):
    # state = get_state(graph)

    # mystr = ''.join(state)

    # return hash(mystr)

    return hash(''.join(get_state(graph)))

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

    sh = state_hash(graph)

    if sh in history_dictionary and step >= history_dictionary[sh]:
        return

    global found
    global explored_states

    graph.sort(key=lambda x: len(x.adjacent_nodes), reverse=True)



    # graph.sort(key=lambda x: collections.Counter([adj.color for adj in x.adjacent_nodes]).most_common(1)[0][1], reverse=True)



    # graph_color_counter = collections.Counter([x.color for x in graph])

    # for item in graph:
    #     adjacent_color_counter = collections.Counter([x.color for x in item.adjacent_nodes])
    #     collapsible = set(graph_color_counter.items()) & set(adjacent_color_counter.items())

    #     if len(collapsible) > 0:
    #         graph.pop(graph.index(item))
    #         graph.insert(0, item)
    #         break

    for node in graph:
        ordered_colors = {x.color for x in node.adjacent_nodes if x.color != node.color}



        # ordered_colors = [x.color for x in node.adjacent_nodes]
        # ordered_colors.sort(key=lambda x: collections.Counter([adj.color for adj in node.adjacent_nodes])[x], reverse=True)

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

                

    if sh in history_dictionary:
        # maybe is not necessary to check <
        if step < history_dictionary[sh]:
            history_dictionary[sh] = step
    else:
        history_dictionary[sh] = step

    if step == 1:
        messagebox.showerror(title="ERROR", message='no solution can be found with ' + str(moves_number) + ' move(s)')

# @ profile
def solve2_dfs(graph, step = 1):
    colors = [x.color for x in graph]
    colors_number = len(set(colors))
    # sh = state_hash(graph)
    if step > moves_number or colors_number > moves_number - step + 2 or (colors_number == moves_number - step + 2 and not is_color_single_node(colors)):
        # if sh in history_dictionary:
        #     if step < history_dictionary[sh]:
        #         history_dictionary[sh] = step
        # else:
        #     history_dictionary[sh] = step
        return
    
    sh = state_hash(graph)
    # sh = calc_hash(graph)


    # use get() method -> h_d.get(sh, 0)
    if sh in history_dictionary and step >= history_dictionary[sh]:
        return

    global found
    global explored_states

    # pairs = list(itertools.product(graph, {x.color for x in graph}))
    # pairs = [(x, y) for x, y in pairs if y in {z.color for z in x.adjacent_nodes}]
    # pairs = list(filter(lambda x: x[1] in {z.color for z in x[0].adjacent_nodes}, pairs))

    pairs = [(x, y) for x in graph for y in {z.color for z in x.adjacent_nodes}]
    # pairs.sort(key=lambda x: len([y.color for y in x[0].adjacent_nodes if y.color == x[1]]), reverse=True)

    # remove if z.id != x[0].id
    pairs.sort(key=lambda x: len([z.color for y in x[0].adjacent_nodes for z in y.adjacent_nodes if z.id != y.id if y.color == x[1]]), reverse=True)

    # pairs.sort(key=lambda x: (len([y.color for y in x[0].adjacent_nodes if y.color == x[1]]),len([z.color for y in x[0].adjacent_nodes for z in y.adjacent_nodes if z.id != y.id if y.color == x[1]])), reverse=True)
    # pairs.sort(key=lambda x: (len([z.color for y in x[0].adjacent_nodes for z in y.adjacent_nodes if z.id != y.id if y.color == x[1]]),len([y.color for y in x[0].adjacent_nodes if y.color == x[1]])), reverse=True)

    graph_color_counter = collections.Counter([x.color for x in graph])

    for node, color in pairs:
        if len([x.color for x in node.adjacent_nodes if x.color == color]) == graph_color_counter[color]:
            pairs.remove((node, color))
            pairs.insert(0, (node, color))
            break

    for pair in pairs:
        old_nodes, new_node = move(graph, pair[0], pair[1])
        explored_states += 1
        solve2_dfs(graph, step + 1)

        if found:
            # print(str(pairs.index(pair)) + ' / ' + str(len(pairs)))            
            solution_steps.insert(0, get_state(graph))
            unmove(graph, old_nodes, new_node)
            return

        if len(graph) == 1:
            solution_steps.insert(0, get_state(graph))
            unmove(graph, old_nodes, new_node)            
            found = True
            return
        
        # solve2_dfs(graph, step + 1)
        unmove(graph, old_nodes, new_node)

    # maybe is not necessary to check <
    if sh in history_dictionary:
        if step < history_dictionary[sh]:
            history_dictionary[sh] = step
    else:
        history_dictionary[sh] = step

def test(graph):
    # copy.deepcopy(graph)

    # g = create_graph2(get_state(graph))

    # fix_single_nodes(g)

    # unify(g)

    pairs = list(itertools.product(graph, {x.color for x in graph}))

    pairs = [(x, y) for (x, y) in pairs if y in [z.color for z in x.adjacent_nodes]]

    pairs = [(x, y) for x in graph for y in {x.color for x in graph} if y in [z.color for z in x.adjacent_nodes]]

def calc_hash(graph):
    # permutations version
    base_hash = new_hash(graph)
    hash_list = []

    for color, value in zip(colors_in_graph, string.ascii_lowercase[:len(colors_in_graph)]):
        base_hash = base_hash.replace(color, value)

    for perm in itertools.permutations(colors_in_graph, len(colors_in_graph)):
        temp_hash = base_hash

        for key, color in zip(string.ascii_lowercase[:len(colors_in_graph)], perm):
            temp_hash = temp_hash.replace(key, color)

        hash_list.append(temp_hash)

    return hash(max(hash_list))

    # classic version
    # return hash(new_hash(graph))

def new_hash(graph, queue=[]):
    if not queue: # first call: find the root of the tree
        graph.sort(key = lambda x: (len(x.adjacent_nodes), x.color), reverse=True)
        groups = itertools.groupby(graph, key = lambda x: (len(x.adjacent_nodes), x.color))
        roots = []
        result_hash = ''

        for _, group in groups:
            roots  = [x for x in group]
            break
                
        temp_hashes = []

        for node in roots:
            temp_queue = [node.id]
            temp_hash = node.color + str(len(node.adjacent_nodes)) + str(temp_queue.index(node.id))
            temp_hash += new_hash(list(node.adjacent_nodes), temp_queue)
            temp_hashes.append((node, temp_hash, temp_queue))
        
        temp_hashes.sort(key = lambda x: x[1], reverse=True)
        queue = temp_hashes[0][2]        
        result_hash += temp_hashes[0][1]
        # maybe is not necessary
        result_hash += new_hash(list(temp_hashes[0][0].adjacent_nodes), queue=queue)
    else:
        graph.sort(key = lambda x: (len(x.adjacent_nodes), x.color), reverse=True)
        groups = itertools.groupby(graph, key = lambda x: (len(x.adjacent_nodes), x.color))
        grouped_nodes = []
        result_hash = ''

        for _, group in groups:
            grouped_nodes.append([x for x in group])

        for group in grouped_nodes:
            while len(group) > 0:
                temp_hashes = []

                for node in group:
                    if node.id in queue:
                        temp_hash = node.color + str(len(node.adjacent_nodes)) + str(queue.index(node.id))
                        temp_hashes.append((node, temp_hash, queue))
                    else:
                        # temp_queue = copy.deepcopy(queue)
                        temp_queue = queue[:]
                        temp_queue.append(node.id)
                        temp_hash = node.color + str(len(node.adjacent_nodes)) + str(temp_queue.index(node.id))
                        temp_hash += new_hash(list(node.adjacent_nodes), queue=temp_queue)
                        temp_hashes.append((node, temp_hash, temp_queue))
                    
                temp_hashes.sort(key = lambda x: x[1], reverse=True)
                queue = temp_hashes[0][2]
                result_hash += temp_hashes[0][1]
                group.remove(temp_hashes[0][0])

    return result_hash

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

    # node1 = Node('1', 'blue')
    # node2 = Node('2', 'yellow')
    # node3 = Node('3', 'yellow')
    # node4 = Node('4', 'yellow')
    # node5 = Node('5', 'blue')

    # node1.adjacent_nodes = {node2, node3, node4}
    # node2.adjacent_nodes = {node1, node5}
    # node3.adjacent_nodes = {node1, node5}
    # node4.adjacent_nodes = {node1, node5}
    # node5.adjacent_nodes = {node2, node3, node4}

    # graph = [node1, node2, node3, node4, node5]
    # graph.sort(key = lambda x: (len(x.adjacent_nodes), x.color), reverse=True)

    # it = itertools.groupby(graph, key = lambda x: (len(x.adjacent_nodes), x.color))

    # result = []

    # for key, group in it:
    #     temp = []
    #     for item in group:
    #         temp.append(item)
    #     result.append(temp)

    # print(result)

    # it = itertools.groupby(graph, key = lambda x: (len(x.adjacent_nodes), x.color))

    # result = []

    # for _, group in it:
    #     result.append([x for x in group])

    # print(result)

    # node1 = Node(1, 'yellow')
    # node2 = Node(2, 'blue')
    # node3 = Node(3, 'blue')
    # node4 = Node(4, 'red')

    # node1.adjacent_nodes = {node2, node3}
    # node2.adjacent_nodes = {node1, node4}
    # node3.adjacent_nodes = {node1, node4}
    # node4.adjacent_nodes = {node2, node3}

    # graph = [node1, node2,  node3, node4]

    # node1 = Node(1, 'yellow')
    # node2 = Node(2, 'blue')
    # node3 = Node(3, 'blue')

    # node1.adjacent_nodes = {node2, node3}
    # node2.adjacent_nodes = {node1}
    # node3.adjacent_nodes = {node1}

    # graph = [node1, node2,  node3]

    # my_hash = new_hash(graph)
    # print(my_hash)