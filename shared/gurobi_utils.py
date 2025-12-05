import gurobipy as gp

def create_model(name="optimization_model"):
    return gp.Model(name)

def suppress_gurobi_output(model):
    model.setParam("OutputFlag", 0)
