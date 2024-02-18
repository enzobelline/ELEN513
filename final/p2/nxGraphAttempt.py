import json
import graphviz as gv
from collections import defaultdict
import re

import networkx as nx
import matplotlib.pyplot as plt

jsonFilePaths = ['opLat.json', 'ir1.json', 'ir1.1.json']
iListFileName='instructionListp1.txt'
# iListFileName='instructionListp1.1.txt'

numPEs=4
pes_tasks = [[] for _ in range(numPEs)]


# jsonData={}
# for file_path in jsonFilePaths:
#     with open(file_path) as json_file:
#         data = json.load(json_file)
#         jsonData[file_path] = data

with open('opLat.json') as f:
    opLat = json.load(f)

with open(iListFileName, 'r') as f:
    iList = f.readlines()

with open('ir1.json') as f:
    ir = json.load(f)
print(opLat)

latencyIR=[]

for instr in ir:
    latency = opLat[instr[1]]  # Get the latency value based on the operation
    instr.append(latency)  # Append the latency to the original tuple
    latencyIR.append(instr)  # Add the modified tuple to the new IR list
# print(latencyIR)

# Initialize the graph
graph = defaultdict(list)

# Initialize the operations dict
operations = {}

# Regular expressions
pattern_assign = re.compile(r'(t\d+)\s=\s(.+);')
pattern_bin_op = re.compile(r'(t\d+)\s([\+\-\*\/])\s(t\d+)')
pattern_load = re.compile(r'LOAD\((.+)\);')
pattern_store = re.compile(r'STORE\((.+),\s(t\d+)\);')

#DFG Graph
# Define the Data-Flow-Graph
dfg = nx.DiGraph()
numNodes=0
# DFG generation with dependancy 
for i in range(0, len(ir)):
    current_instruction = ir[i]
    currOp = current_instruction[1]
    # print(i)
    dfg.add_node(f"{i}", value=iList[i])
    rsMatch, rtMatch = False, False
    numNodes+=1
    for j in range(i-1, -1, -1): # traverse backwards from most recent to oldest instruction
        previous_instruction = ir[j]
        # and checks if the rs register has dependency this handles using the most recent destination register
        if current_instruction[2] == previous_instruction[4] and not rsMatch:
            dfg.add_edge(f"{j}",f"{i}")
            rsMatch = True
        # and checks if the rt register has dependency this handles using the most recent destination register
        if current_instruction[3] == previous_instruction[4] and not rtMatch:
            dfg.add_edge(f"{j}",f"{i}")
            rtMatch = True
        if rsMatch and rtMatch:
            break
        if rsMatch and currOp=="STORE": #this handles multiple register usage and uses most recent register to store
            break
        # print(f"{current_instruction}{i}")
# Visualize the graph
# Get the number of nodes and edges in the graph
num_nodes = dfg.number_of_nodes()
num_edges = dfg.number_of_edges()
print("Number of nodes:", num_nodes)
print("Number of edges:", num_edges)

labels = {node: dfg.nodes[node]['value'] for node in dfg.nodes}

nx.draw(dfg, with_labels=True)
nx.draw_networkx_labels(dfg, pos=nx.spring_layout(dfg), labels=labels)
plt.show()

# Render DFG
# dfg.render(filename='dfgDependency', view=True)  # Creates a 'dfg.png' file

leafNodes = []
nodes=dfg.nodes[1]
for node in nodes:
    if not any(node in dfg.successors(n) for n in nodes):
        leafNodes.append(node)

# Print the leaf nodes
print("Leaf nodes:")
for leafNode in leafNodes:
    print(leafNode)
# for i in range(0, len(ir)):
#     if ()
