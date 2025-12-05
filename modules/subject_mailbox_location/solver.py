import gurobipy as gp
from gurobipy import GRB
import numpy as np
from shared.gurobi_utils import create_model
from .model import MailboxLocationModel

class MailboxLocationSolver:
    def __init__(self, demand_points, num_mailboxes, radius, 
                 costs=None, budgets=None, capacities=None, 
                 mailbox_bounds=None, max_coverage_level=1):
        
        self.model_data = MailboxLocationModel(
            demand_points, num_mailboxes, radius, costs, budgets, capacities
        )
        self.mailbox_bounds = mailbox_bounds if mailbox_bounds else {
            'x_min': -10, 'x_max': 10, 'y_min': -10, 'y_max': 10
        }
        self.max_coverage_level = max_coverage_level

    def solve(self):
        m = create_model("advanced_mailbox_location")
        dp = self.model_data.demand_points
        K = self.model_data.num_mailboxes
        R = self.model_data.radius
        
        # Decision variables for mailbox coordinates
        x = m.addVars(K, lb=self.mailbox_bounds['x_min'], 
                      ub=self.mailbox_bounds['x_max'], 
                      name="mailbox_x")
        y = m.addVars(K, lb=self.mailbox_bounds['y_min'], 
                      ub=self.mailbox_bounds['y_max'], 
                      name="mailbox_y")
        
        # Coverage variables
        z = m.addVars(len(dp), K, vtype=GRB.BINARY, name="cover")
        
        # Binary variable for whether mailbox is built
        built = m.addVars(K, vtype=GRB.BINARY, name="built")
        
        # Coverage level variable
        coverage = m.addVars(len(dp), lb=0, ub=self.max_coverage_level, 
                            vtype=GRB.INTEGER, name="coverage_level")
        
        # Big M for distance constraint
        M = 1000
        
        # Distance constraints
        for i in range(len(dp)):
            for k in range(K):
                dist_expr = (dp[i]['x'] - x[k])**2 + (dp[i]['y'] - y[k])**2
                m.addConstr(dist_expr <= R**2 + M * (1 - z[i, k]))
                m.addConstr(dist_expr >= R**2 * (1 - z[i, k]))
                m.addConstr(z[i, k] <= built[k])
        
        # Coverage level calculation
        for i in range(len(dp)):
            m.addConstr(coverage[i] == gp.quicksum(z[i, k] for k in range(K)))
        
        # Capacity constraints
        if self.model_data.capacities:
            for k in range(K):
                m.addConstr(gp.quicksum(z[i, k] * dp[i].get('demand', 1) 
                          for i in range(len(dp))) <= self.model_data.capacities[k])
        
        # Budget constraint
        if self.model_data.budgets:
            total_cost = gp.quicksum(built[k] * self.model_data.costs[k] for k in range(K))
            m.addConstr(total_cost <= self.model_data.budgets)
        
        # Force exact number of mailboxes if specified
        if K > 0:
            m.addConstr(gp.quicksum(built[k] for k in range(K)) == K)
        
        # Objective: maximize weighted coverage
        m.setObjective(
            gp.quicksum(coverage[i] * dp[i].get('population', 1) 
                       for i in range(len(dp))),
            GRB.MAXIMIZE
        )
        
        m.optimize()
        
        # Extract solution
        mailbox_locations = []
        for k in range(K):
            if built[k].x > 0.5:
                mailbox_locations.append({
                    'x': x[k].x,
                    'y': y[k].x,
                    'built': True
                })
        
        coverage_info = []
        for i in range(len(dp)):
            coverage_info.append({
                'point': i,
                'coverage_level': coverage[i].x,
                'served_by': [k for k in range(K) if z[i, k].x > 0.5]
            })
        
        return {
            "objective": m.objVal,
            "mailbox_locations": mailbox_locations,
            "coverage_info": coverage_info,
            "total_built": sum(1 for loc in mailbox_locations if loc['built'])
        }