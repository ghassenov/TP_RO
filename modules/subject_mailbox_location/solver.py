import gurobipy as gp
from gurobipy import GRB
from math import sqrt
from shared.gurobi_utils import create_model
from shared.validation import validate_mailbox_input
from .model import MailboxLocationModel

class MailboxLocationSolver:
    def __init__(self, demand_points, facilities, radius, num_mailboxes):
        validate_mailbox_input(demand_points, num_mailboxes, radius)
        self.model_data = MailboxLocationModel(
            demand_points, facilities, radius, num_mailboxes
        )

    def solve(self):
        m = create_model("mailbox_location")
        dp = self.model_data.demand_points
        fac = self.model_data.facilities
        R = self.model_data.radius
        K = self.model_data.num_mailboxes

        x = m.addVars(len(fac), vtype=GRB.BINARY, name="open")
        y = m.addVars(len(dp), vtype=GRB.BINARY, name="covered")

        covers = {}
        for i, p in enumerate(dp):
            for j, f in enumerate(fac):
                d = sqrt((p["x"]-f["x"])**2 + (p["y"]-f["y"])**2)
                covers[(i, j)] = 1 if d <= R else 0

        m.addConstr(x.sum() == K)

        for i in range(len(dp)):
            m.addConstr(
                y[i] <= gp.quicksum(x[j] * covers[(i, j)] for j in range(len(fac)))
            )

        m.setObjective(
            gp.quicksum(y[i] * dp[i]["population"] for i in range(len(dp))),
            GRB.MAXIMIZE
        )

        m.optimize()

        chosen = [j for j in range(len(fac)) if x[j].x > 0.5]

        return {
            "objective": m.objVal,
            "chosen_facilities": chosen,
            "covered_points": [
                i for i in range(len(dp)) if y[i].x > 0.5
            ]
        }
