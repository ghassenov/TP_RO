import gurobipy as gp
import numpy as np
from gurobipy import GRB

from .model import TelecomNetworkModel


class TelecomNetworkSolver:
    """Solveur PLNE pour la conception de réseau de fibre optique"""

    def __init__(self, nodes, potential_links, demands, **kwargs):
        self.model_data = TelecomNetworkModel(
            nodes=nodes,
            potential_links=potential_links,
            demands=demands,
            fixed_costs=kwargs.get('fixed_costs'),
            variable_costs=kwargs.get('variable_costs'),
            capacities=kwargs.get('capacities'),
            budget=kwargs.get('budget')
        )

    def solve(self):
        """Résoudre le problème de conception de réseau"""
        m = gp.Model("Telecom_Network_Design")

        # Données
        N = self.model_data.num_nodes
        L = self.model_data.num_links
        K = self.model_data.capacity_options
        C = self.model_data.capacities
        f = self.model_data.fixed_costs  # Coûts fixes
        v = self.model_data.variable_costs  # Coûts variables
        D = self.model_data.demands  # Matrice de demande

        # Variables de décision
        # y[l] = 1 si la liaison l est construite
        y = m.addVars(L, vtype=GRB.BINARY, name="build_link")

        # z[l][k] = 1 si la capacité k est sélectionnée pour la liaison l
        z = m.addVars(L, K, vtype=GRB.BINARY, name="capacity_level")

        # x[l][i][j] = flux sur la liaison l pour la paire (i,j)
        # Pour simplifier, on utilise un dictionnaire
        x = {}
        for i in range(N):
            for j in range(N):
                if i != j and D[i][j] > 0:
                    for l in range(L):
                        x[(l, i, j)] = m.addVar(
                            lb=0, ub=GRB.INFINITY,
                            name=f"flow_l{l}_pair_{i}_{j}"
                        )

        # Contraintes

        # 1. Chaque liaison ne peut avoir qu'un niveau de capacité
        for l in range(L):
            m.addConstr(z.sum(l, '*') <= y[l], name=f"single_capacity_{l}")

        # 2. Contrainte de capacité
        for l in range(L):
            total_flow = gp.quicksum(
                x.get((l, i, j), 0)
                for i in range(N)
                for j in range(N)
                if i != j
            )
            capacity = gp.quicksum(z[l, k] * C[k] for k in range(K))
            m.addConstr(total_flow <= capacity, name=f"capacity_{l}")

        # 3. Conservation du flux pour chaque paire (i,j)
        for src in range(N):
            for dst in range(N):
                if src != dst and D[src][dst] > 0:
                    # Flux sortant du source
                    outflow = gp.quicksum(
                        x.get((l, src, dst), 0)
                        for l in range(L)
                        if self.model_data.potential_links[l]['from'] == src
                    )

                    # Flux entrant au destination
                    inflow = gp.quicksum(
                        x.get((l, src, dst), 0)
                        for l in range(L)
                        if self.model_data.potential_links[l]['to'] == dst
                    )

                    # Flux intermédiaire
                    for node in range(N):
                        if node != src and node != dst:
                            # Flux entrant au nœud
                            flow_in = gp.quicksum(
                                x.get((l, src, dst), 0)
                                for l in range(L)
                                if self.model_data.potential_links[l]['to'] == node
                            )
                            # Flux sortant du nœud
                            flow_out = gp.quicksum(
                                x.get((l, src, dst), 0)
                                for l in range(L)
                                if self.model_data.potential_links[l]['from'] == node
                            )
                            m.addConstr(flow_in == flow_out, name=f"flow_conservation_{src}_{dst}_{node}")

                    m.addConstr(outflow == D[src][dst], name=f"demand_outflow_{src}_{dst}")
                    m.addConstr(inflow == D[src][dst], name=f"demand_inflow_{src}_{dst}")

        # 4. Contrainte de budget (si spécifié)
        if self.model_data.budget:
            total_cost = gp.quicksum(
                f[l] * y[l] +
                gp.quicksum(v[l] * C[k] * z[l, k] for k in range(K))
                for l in range(L)
            )
            m.addConstr(total_cost <= self.model_data.budget, name="budget_constraint")

        # Objectif: Minimiser le coût total
        m.setObjective(
            gp.quicksum(
                f[l] * y[l] +
                gp.quicksum(v[l] * C[k] * z[l, k] for k in range(K))
                for l in range(L)
            ),
            GRB.MINIMIZE
        )

        # Optimiser
        m.optimize()

        # Extraire la solution
        selected_links = []
        link_capacities = []
        total_cost = m.objVal

        for l in range(L):
            if y[l].x > 0.5:
                link_info = self.model_data.potential_links[l].copy()
                link_info['built'] = True
                link_info['selected'] = True
                link_info['cost'] = f[l]

                # Trouver la capacité sélectionnée
                for k in range(K):
                    if z[l, k].x > 0.5:
                        link_info['capacity'] = C[k]
                        link_info['capacity_cost'] = v[l] * C[k]
                        break

                # Calculer le flux total sur cette liaison
                total_flow = 0
                for i in range(N):
                    for j in range(N):
                        if i != j:
                            flow_var = x.get((l, i, j))
                            if flow_var:
                                total_flow += flow_var.x
                link_info['flow'] = total_flow
                link_info['utilization'] = total_flow / link_info['capacity'] if link_info['capacity'] > 0 else 0

                selected_links.append(link_info)
                link_capacities.append(link_info['capacity'])

        # Calculer les métriques
        demand_satisfied = 0
        total_demand = 0
        for i in range(N):
            for j in range(N):
                if i != j:
                    total_demand += D[i][j]
                    # Vérifier si la demande est satisfaite
                    satisfied = True
                    for l in range(L):
                        flow_var = x.get((l, i, j))
                        if flow_var and flow_var.x < D[i][j]:
                            satisfied = False
                            break
                    if satisfied:
                        demand_satisfied += D[i][j]

        return {
            "objective": total_cost,
            "selected_links": selected_links,
            "link_capacities": link_capacities,
            "total_demand": total_demand,
            "demand_satisfied": demand_satisfied,
            "demand_satisfaction_rate": demand_satisfied / total_demand if total_demand > 0 else 0,
            "num_links_built": len(selected_links),
            "total_capacity": sum(link_capacities),
            "flow_variables": {k: v.x for k, v in x.items() if hasattr(v, 'x') and v.x > 0}
        }
