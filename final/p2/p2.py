import json
import graphviz as gv
from collections import defaultdict
import re

jsonFilePaths = ['opLat.json', 'ir1.json', 'ir1.1.json']
iListFileName='instructionListp1.txt'
irJsonFileName = "ir1.json"
# iListFileName='instructionListp1.1.txt'
# irJsonFileName="ir1.1.json"
numPEs=4
pes_tasks = [[] for _ in range(numPEs)]
print(pes_tasks)
# jsonData={}
# for file_path in jsonFilePaths:
#     with open(file_path) as json_file:
#         data = json.load(json_file)
#         jsonData[file_path] = data

with open('opLat.json') as f:
    opLat = json.load(f)

with open(iListFileName, 'r') as f:
    iList = f.readlines()

with open(irJsonFileName) as f:
    ir = json.load(f)
print(opLat)

latencyIR=[]
totalLat=0
for instr in ir:
    latency = opLat[instr[1]]  # Get the latency value based on the operation
    instr.append(latency)  # Append the latency to the original tuple
    latencyIR.append(instr)  # Add the modified tuple to the new IR list
    totalLat+=latency
print(totalLat)
# print(latencyIR)



nodes=[]
edges=[]

numNodes=1
for i in range(0, len(ir)):
    nodes.append(latencyIR[i])
    current_instruction = latencyIR[i]
    currOp = latencyIR[1]    
    rsMatch, rtMatch = False, False
    numNodes+=1    
    for j in range(i-1, -1, -1): # traverse backwards from most recent to oldest instruction
        previous_instruction = ir[j]
        # and checks if the rs register has dependency this handles using the most recent destination register
        if current_instruction[2] == previous_instruction[4] and not rsMatch:
            edges.append([j,i])
            rsMatch = True
        # and checks if the rt register has dependency this handles using the most recent destination register
        if current_instruction[3] == previous_instruction[4] and not rtMatch:
            edges.append([j,i])
            rtMatch = True
        if rsMatch and rtMatch:
            break
        if rsMatch and currOp=="STORE": #this handles multiple register usage and uses most recent register to store
            break
        # print(f"{current_instruction}{i}")

print(edges)
#here i have the sorted notes by lowest opLatency to largest
sortedNodes = sorted(nodes, key=lambda node: node[5])
print(sortedNodes)
# #prune=outside in
# while len(nodes) != numPEs:
#     pruneCounter=len(nodes)
#     for edge in edges:
#         if nodes[pruneCounter][0]==edge[0]:
#             break
#         else:

currentMerge={"shortest","middle","longest"}
typeMergeCounter=0
timesMerging=len(nodes)-numPEs

def findNodeBasedOninstructionnumber(iNum,nodes):
    for node in nodes:
        if iNum==node[0]:
            return node


for i in range(0,timesMerging):#do this as many merges as you need to reduce the number of nodes down to pes
    sortedNodes = sorted(nodes, key=lambda node: node[5])
    print(sortedNodes)
    currentMergingNode1=sortedNodes[0]
    for edge in edges:# we are going to join it with another node that has it as its dependancy
        if currentMergingNode1[0]==edge[0]:
            currentMergingNode2 = findNodeBasedOninstructionnumber(edge[1],nodes)
            # for node1object,node2object in currentMergingNode1,currentMergingNode2:
            print(f"NODES TO MERGE{currentMergingNode1}ANDDDDDDDD{currentMergingNode2}\n")

            newNode=[]
            newNode.append(currentMergingNode1[0]) #lets keep just one iNum value
            newNode.append([currentMergingNode1[1],currentMergingNode2[1]]) #here on we can keep both
            newNode.append([currentMergingNode1[2],currentMergingNode2[2]])
            newNode.append([currentMergingNode1[3],currentMergingNode2[3]])
            newNode.append([currentMergingNode1[4],currentMergingNode2[4]]) 
            newNode.append(currentMergingNode1[5]+currentMergingNode2[5])#except this add latencies
            break
    #now that we have this newNode that is merged, lets reconnect all the edges to this new node
    for edge in edges:
        if edge[0]==currentMergingNode2[1]:
            edge[0]=newNode[0]
            break
    #now lets remove the old nodes and add this new one
    for i in range(0,len(nodes)):
        print(nodes[i])
        print(len(nodes))
        compareNode=nodes[i][0]
        if currentMergingNode1[0]==compareNode:
            nodes[i]=newNode
        if currentMergingNode2[0]==nodes[i][0]:
            # print("REMOVING===============================")
            nodes.remove(currentMergingNode2)
            break
    edgeList  = list(set(tuple(edges) for edges in edges))
    edges=edgeList
    print(f"NEWMERGEDNODE{newNode}\nREMOVED{currentMergingNode2}\nCURRENTNODESLIST{nodes}**************************************\n")



# Regular expressions
pattern_assign = re.compile(r'(t\d+)\s=\s(.+);')
pattern_bin_op = re.compile(r'(t\d+)\s([\+\-\*\/])\s(t\d+)')
pattern_load = re.compile(r'LOAD\((.+)\);')
pattern_store = re.compile(r'STORE\((.+),\s(t\d+)\);')

#DFG Graph
# Define the Data-Flow-Graph
dfg = gv.Digraph(format='png')
numNodes=1
# DFG generation with dependancy 
for i in range(0, len(ir)):
    current_instruction = ir[i]
    currOp = current_instruction[1]
    # print(i)
    dfg.node(f"{i}", iList[i])
    rsMatch, rtMatch = False, False
    numNodes+=1
    for j in range(i-1, -1, -1): # traverse backwards from most recent to oldest instruction
        previous_instruction = ir[j]
        # and checks if the rs register has dependency this handles using the most recent destination register
        if current_instruction[2] == previous_instruction[4] and not rsMatch:
            dfg.edge(f"{j}",f"{i}")
            rsMatch = True
        # and checks if the rt register has dependency this handles using the most recent destination register
        if current_instruction[3] == previous_instruction[4] and not rtMatch:
            dfg.edge(f"{j}",f"{i}")
            rtMatch = True
        if rsMatch and rtMatch:
            break
        if rsMatch and currOp=="STORE": #this handles multiple register usage and uses most recent register to store
            break
        # print(f"{current_instruction}{i}")

print(nodes)
# Render DFG
dfg.render(filename='dfgDependency', view=True)  # Creates a 'dfg.png' file

# leafNodes = []
# nodes=dfg.nodes[1]
# for node in nodes:
#     if not any(node in dfg.successors(n) for n in nodes):
#         leafNodes.append(node)

# # Print the leaf nodes
# print("Leaf nodes:")
# for leafNode in leafNodes:
#     print(leafNode)
# for i in range(0, len(ir)):
#     if ()
1