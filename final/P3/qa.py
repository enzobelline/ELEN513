import json
def scalar_code(ir):
    result=None

    for operation in ir:
        op_name=operation["operation"]
        op_inputs=operation["inputs"]
        op_output=operation["output"]

        if op_name=="add":
            value=op_inputs[0]
            variable=op_inputs[1]
            if result is None:
                result=value + variable
            else:
                result += value + variable
        elif op_name=="multiply":
            value=op_inputs[0]
            variable=op_inputs[1]
            if result is None:
                result=value * variable
            else:
                result *= value * variable
        elif op_name=="subtract":
            value=op_inputs[0]
            variable=op_inputs[1]
            if result is None:
                result=value - variable
            else:
                result -= value - variable
        elif op_name=="divide":
            value=op_inputs[0]
            variable=op_inputs[1]
            if result is None:
                result=value / variable
            else:
                result /= value / variable

    return result

def simulate_backend_code(ir,num_pes,operation_latencies):
    pes=[{"state": None,"execution_time": 0} for _ in range(num_pes)]

    for operation in ir:
        op_name=operation["operation"]
        op_inputs=operation["inputs"]
        op_output=operation["output"]

        min_time=float("inf")
        min_pe=None
        for pe in pes:
            if pe["state"] is None or pe["execution_time"] < min_time:
                min_time=pe["execution_time"]
                min_pe=pe
        min_pe["execution_time"] += operation_latencies[op_name]

        min_pe["state"]={op_output: op_inputs}

    backend_result={}
    for pe in pes:
        if pe["state"] is not None:
            backend_result.update(pe["state"])

    return backend_result

# Example usage
ir=[
    {"operation": "load"    ,"inputs": ["x"]      ,"output": "t1"},  #1 t 1=LOAD( x ) ;
    {"operation": "add"     ,"inputs": ["t1",4]   ,"output": "t2"},  #2 t 2=t 1 +4;
    {"operation": "multiply","inputs": ["t1",8]   ,"output": "t3"},  #3 t 3=t 1 ∗ 8;
    {"operation": "subtract","inputs": ["t1",4]   ,"output": "t4"},  #4 t 4=t1 −4;
    {"operation": "divide"  ,"inputs": ["t1",2]   ,"output": "t5"},  #5 t 5=t 1 / 2;
    {"operation": "multiply","inputs": ["t2","t3"],"output": "t6"},  #6 t 6=t 2 ∗ t 3 ;
    {"operation": "subtract","inputs": ["t4","t5"],"output": "t7"},  #7 t 7=t4−t 5 ;
    {"operation": "multiply","inputs": ["t6","t7"],"output": "t8"},  #8 t 8=t 6 ∗ t 7 ;
    {"operation": "store"   ,"inputs": ["y","t8"] ,"output": "x" }    #9 STORE( y ,t 8 ) ;
    ]

numPEs=4
latency_file="opLat.json"
# generate_backend_code(ir,numPEs,latency_file)

scalar_result=scalar_code(ir)
backend_result=simulate_backend_code(num_pes=4)

# Compare the results
if scalar_result==backend_result:
    print("Results Match!")
else:
    print("Results Do Not Match!")