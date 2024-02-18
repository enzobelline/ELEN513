import re
import graphviz as gv

# Open and read the file
with open('instructionList.txt', 'r') as f:
    data = f.readlines()

# Define the Data-Flow-Graph
dfg = gv.Digraph(format='png')

# Initialize empty list for Intermediate Representation
ir = []

numLd=1
numSt=1
numAdd=1
numSub=1
numMult=1
numDiv=1
numSqrt=1

# Define regular expressions
pattern_assign = re.compile(r'(t\d+)\s=\s(.+);')
pattern_bin_add = re.compile(r'(t\d+)\s([\+])\s(t\d+)')
pattern_bin_sub = re.compile(r'(t\d+)\s([\-])\s(t\d+)')
pattern_bin_mult = re.compile(r'(t\d+)\s([\*])\s(t\d+)')
pattern_bin_div = re.compile(r'(t\d+)\s([\/])\s(t\d+)')
pattern_bin_sqrt = re.compile(r'(t\d+)\s([\^])\s(t\d+)')
pattern_bin_addInt = re.compile(r'(t\d+)\s([\+])\s(-?\d+)')
pattern_bin_subInt = re.compile(r'(t\d+)\s([\-])\s(-?\d+)')
pattern_bin_multInt = re.compile(r'(t\d+)\s([\*])\s(-?\d+)')
pattern_bin_divInt = re.compile(r'(t\d+)\s([\/])\s(-?\d+)')
pattern_bin_sqrtInt = re.compile(r'(t\d+)\s([\^])\s(\d+)')
pattern_load = re.compile(r't\d+\s=\sLOAD\((.+)\);')
pattern_store = re.compile(r'STORE\((.+),\s(t\d+)\);')

pattern_bin_op    = re.compile(r'(rd\d+)\s([\+\-\*\^\/])\s(t\d+)')
pattern_bin_intOp = re.compile(r'(rd\d+)\s([\+\-\*\^\/])\s(\d+)')

# Parse and generate
for line in data:
    match_assign = pattern_assign.match(line.strip())

    if match_assign:
        rd, expr = match_assign.groups()

        match_bin_add = pattern_bin_add.match(expr)
        match_bin_sub = pattern_bin_sub.match(expr)
        match_bin_mult = pattern_bin_mult.match(expr)
        match_bin_div = pattern_bin_div.match(expr)
        match_bin_sqrt = pattern_bin_sqrt.match(expr)
        match_bin_addInt = pattern_bin_addInt.match(expr)
        match_bin_subInt = pattern_bin_subInt.match(expr)
        match_bin_multInt = pattern_bin_multInt.match(expr)
        match_bin_divInt = pattern_bin_divInt.match(expr)
        match_bin_sqrtInt = pattern_bin_sqrtInt.match(expr)

        match_bin_op = pattern_bin_op.match(expr)
        match_bin_intOp = pattern_bin_intOp.match(expr)

        if match_bin_op:
            if match_bin_add:
                dfg.node(f"add{numAdd}", label=f"{rd} = {expr}")
                rs, op, rt = match_bin_add.groups()
                ir.append(("add{numAdd}",op, rs, rt, rd))
            
            dfg.edge(rs, rd)
            dfg.edge(rt, rd)

        elif match_bin_intOp:
            rs, op, rt = match_bin_intOp.groups()
            ir.append((op, rs, rt, rd))
            dfg.edge(rs, rd)
        else:
            ir.append(('LOAD' if 'LOAD' in expr else 'STORE', expr.replace('LOAD(', '').replace('STORE(', '').replace(')', ''), '', rd))
    else:
        match_load = pattern_load.match(line.strip())
        if match_load:
            t,expr = match_load.groups()
            ir.append(('LOAD', expr, '', t))
            dfg.node(t, label=f"{t} = LOAD({expr})")

        match_store = pattern_store.match(line.strip())
        if match_store:
            dest, src = match_store.groups()
            t = 't' + str(len(ir) + 1)  # Generate a unique temporary variable name
            ir.append(('STORE', dest, '', src))
            dfg.node(t, label=f"STORE({dest}, {src})")
            dfg.edge(src, t)

# Render DFG
dfg.render(filename='dfg', view=True)  # Creates a 'dfg.png' file

# Print Intermediate Representation
for instruction in ir:
    print(instruction)
