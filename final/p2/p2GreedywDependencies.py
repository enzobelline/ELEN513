import json

def generate_backend_code(ir, num_pes, operation_latencies):
    # Initialize PEs and their states
    pes = [{"state": None, "execution_time": 0} for _ in range(num_pes)]

    # Create a dictionary to store operation completion times
    completion_times = {}

    # Iterate through the operations in the IR
    for operation in ir:
        op_name = operation["operation"]
        op_inputs = operation["inputs"]
        op_output = operation["output"]

        # Check if the operation has any dependencies
        dependencies = [completion_times[input_var] for input_var in op_inputs if input_var in completion_times]

        if dependencies:
            # Find the maximum completion time among the dependencies
            max_dependency_time = max(dependencies)

            # Find the PE with the earliest available time after the dependencies
            min_time = float("inf")
            min_pe = None
            for pe in pes:
                if pe["state"] is None or pe["execution_time"] > max_dependency_time:
                    if pe["execution_time"] < min_time:
                        min_time = pe["execution_time"]
                        min_pe = pe

        else:
            # Find the PE with the earliest available time
            min_time = float("inf")
            min_pe = None
            for pe in pes:
                if pe["state"] is None or pe["execution_time"] < min_time:
                    min_time = pe["execution_time"]
                    min_pe = pe

        # Update the execution time of the selected PE
        min_pe["execution_time"] += operation_latencies[op_name]

        # Assign the operation to the selected PE
        min_pe["state"] = {op_output: op_inputs}

        # Store the completion time of the operation
        completion_times[op_output] = min_pe["execution_time"]

    # Generate the output code for each PE
    output_code = {}
    for i, pe in enumerate(pes):
        if pe["state"] is not None:
            output_code[f"PE{i+1}"] = pe["state"]

    return output_code

def get_operation_latency(operation, latency_data):
    op_name = operation["operation"]
    return latency_data.get(op_name, 0)  # Return 0 if operation latency not found

def get_next_pe_with_minimum_latency(pe_assignments, operation, latency_data):
    min_latency = float('inf')
    min_latency_pe_id = 0

    for pe_id, pe_operations in enumerate(pe_assignments):
        pe_latency = sum(get_operation_latency(op, latency_data) for op in pe_operations)
        pe_latency += get_operation_latency(operation, latency_data)

        if pe_latency < min_latency:
            min_latency = pe_latency
            min_latency_pe_id = pe_id
    return min_latency_pe_id


def generate_code_for_operation(operation):
    op_name   = operation["operation"]
    op_inputs = operation["inputs"]
    op_output = operation["output"]

    if op_name == "load":
        memory_address = op_inputs[0]
        code = f"{op_output} = load({memory_address})"
    elif op_name == "store":
        memory_address = op_inputs[0]
        value = op_inputs[1]
        code = f"store({value}, {memory_address})"
    elif op_name == "add" and isinstance(op_inputs[1], int):
        variable = op_inputs[0]
        value = op_inputs[1]
        code = f"{op_output} = {value} + {variable}"
    elif op_name == "subtract" and isinstance(op_inputs[1], int):
        variable = op_inputs[0]
        value = op_inputs[1]
        code = f"{op_output} = {variable} - {value}"
    elif op_name == "multiply" and isinstance(op_inputs[1], int):
        variable = op_inputs[0]
        value = op_inputs[1]
        code = f"{op_output} = {value} * {variable}"    
    elif op_name == "divide" and isinstance(op_inputs[1], int):
        variable = op_inputs[0]
        value = op_inputs[1]
        code = f"{op_output} = {variable} / {value}"
    else:
        code = f"{op_output} = {op_name}("
        code += ", ".join(op_inputs)
        code += ")"
    return code

# Example usage
ir = [
    {"operation": "load"    , "inputs": ["x"]      , "output": "t1"},   #1 t1=LOAD( x ) ;
    {"operation": "add"     , "inputs": ["t1",4]   , "output": "t2"},   #2 t2=t1 +4;
    {"operation": "multiply", "inputs": ["t1",8]   , "output": "t3"},   #3 t3=t1 ∗ 8;
    {"operation": "subtract", "inputs": ["t1",4]   , "output": "t4"},   #4 t4=t1 −4;
    {"operation": "divide"  , "inputs": ["t1",2]   , "output": "t5"},   #5 t5=t1 / 2;
    {"operation": "multiply", "inputs": ["t2","t3"], "output": "t6"},   #6 t6=t2 ∗ t3 ;
    {"operation": "subtract", "inputs": ["t4","t5"], "output": "t7"},   #7 t7=t4−t5 ;
    {"operation": "multiply", "inputs": ["t6","t7"], "output": "t8"},   #8 t8=t6 ∗ t7 ;
    {"operation": "store"   , "inputs": ["y","t8"] , "output": "x" }    #9 STORE( y , t8 ) ;
    ]

numPEs = 4
latency_file = "opLat.json"
generate_backend_code(ir, numPEs, latency_file)