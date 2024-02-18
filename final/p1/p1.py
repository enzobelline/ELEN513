import re
import graphviz as gv
import json

#filenames
# iList='instructionListp1.txt'
# outputJsonFilename = "ir1.json"
iList='instructionListp1.1.txt'
outputJsonFilename = "ir1.1.json"


# Open and read the file
with open(iList, 'r') as f:
    data = f.readlines()

# Initialize empty list for Intermediate Representation
ir = []

# Define regular expressions
pattern_assign = re.compile(r'(t\d+)\s*=\s*(t.+);')
pattern_bin_op = re.compile(r'(t\d+)\s*([\+\-\*\^\/])\s*(t\d+)')
pattern_bin_intOp = re.compile(r'(t\d+)\s*([\+\-\*\^\/])\s*(\d+)')
# pattern_bin_add = re.compile(r'(t\d+)\s*([\+])\s*(t\d+)')
# pattern_bin_sub = re.compile(r'(t\d+)\s*([\-])\s*(t\d+)')
# pattern_bin_mult = re.compile(r'(t\d+)\s*([\*])\s*(t\d+)')
# pattern_bin_div = re.compile(r'(t\d+)\s*([\/])\s*(t\d+)')
# pattern_bin_sqrt = re.compile(r'(t\d+)\s*([\^])\s*(t\d+)')
# pattern_bin_addInt = re.compile(r'(t\d+)\s*([\+])\s*(-?\d+)')
# pattern_bin_subInt = re.compile(r'(t\d+)\s*([\-])\s*(-?\d+)')
# pattern_bin_multInt = re.compile(r'(t\d+)\s*([\*])\s*(-?\d+)')
# pattern_bin_divInt = re.compile(r'(t\d+)\s*([\/])\s*(-?\d+)')
# pattern_bin_sqrtInt = re.compile(r'(t\d+)\s*([\^])\s*(\d+)')
pattern_load = re.compile(r'(t\d+)\s*=\s*LOAD\((.+)\);')
pattern_store = re.compile(r'STORE\((.+),\s*(t\d+)\);')

# Intermediate Representation Generation
for index,line in enumerate(data):
    match_assign = pattern_assign.match(line.strip())
    if match_assign:
        rd, expr = match_assign.groups()
        match_bin_op = pattern_bin_op.match(expr)
        match_bin_intOp = pattern_bin_intOp.match(expr)

        if match_bin_op:
            rs, op, rt = match_bin_op.groups()
            ir.append((index, op, rs, rt, rd))
        elif match_bin_intOp:
            rs, op, rt = match_bin_intOp.groups()
            ir.append((index, op, rs, rt, rd))
    else:
        match_load = pattern_load.match(line.strip())
        if match_load:
            t,expr = match_load.groups()
            ir.append((index, 'LOAD', expr, '', t))
        match_store = pattern_store.match(line.strip())
        if match_store:
            dest, src = match_store.groups()
            ir.append((index, 'STORE', src, '', dest))

# Print Intermediate Representation
for instruction in ir:
    print(instruction)

# # Write Intermediate Representation to the JSON file
with open(outputJsonFilename, 'w') as irjson:
    json.dump(ir, irjson)

#DFG Graph
# Define the Data-Flow-Graph
dfg = gv.Digraph(format='png')

numOfOperations = [1] * 7
numOfOperationsPointer = 0
numNodes=1
# DFG generation with dependancy 
for i in range(0, len(ir)):
    current_instruction = ir[i]
    currOp = current_instruction[1]
    # print(i)
    dfg.node(f"{i}", data[i])
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
# Render DFG
dfg.render(filename='dfgDependency', view=True)  # Creates a 'dfg.png' file


# print(numNodes)
# typesofOp = {
#     "LOAD": (numOfOperations[0] + 1, 0),
#     "STORE": (numOfOperations[1] + 1, 1),
#     "+": (numOfOperations[2] + 1, 2),
#     "-": (numOfOperations[3] + 1, 3),
#     "*": (numOfOperations[4] + 1, 4),
#     "/": (numOfOperations[5] + 1, 5),
#     "^": (numOfOperations[6] + 1, 6),
# }

