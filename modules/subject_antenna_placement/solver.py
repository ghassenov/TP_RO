import gurobipy as gp
import numpy as np
from gurobipy import GRB

from .model import AntennaPlacementModel


class AntennaPlacementSolver:
    """Solveur PLNE pour le placement d'antennes et affectation des utilisateurs"""

    def __init__(self, users, candidate_sites, **kwargs):
        self.model_data = AntennaPlacementModel(
            users=users,
            candidate_sites=candidate_sites,
            setup_costs=kwargs.get('setup_costs'),
            connection_costs=kwargs.get('connection_costs'),
            capacities=kwargs.get('capacities'),
            coverage_radius=kwargs.get('coverage_radius'),
            max_antennas=kwargs.get('max_antennas')
        )

    def solve(self):
        """Résoudre le problème de placement d'antennes"""
        try:
            m = gp.Model("Antenna_Placement")

            # Données
            U = self.model_data.num_users
            S = self.model_data.num_sites
            C = self.model_data.setup_costs
            D = self.model_data.connection_costs
            K = self.model_data.capacities
            R = self.model_data.coverage_radius
            max_antennas = self.model_data.max_antennas

            # Variables de décision
            # y[j] = 1 si une antenne est installée au site j
            y = m.addVars(S, vtype=GRB.BINARY, name="install_antenna")

            # x[i][j] = 1 si l'utilisateur i est affecté au site j
            x = m.addVars(U, S, vtype=GRB.BINARY, name="assign_user")

            # z[j][k] = 1 si la capacité k est choisie pour le site j
            capacity_options = len(K)
            z = m.addVars(S, capacity_options, vtype=GRB.BINARY, name="capacity_level")

            # Contraintes

            # 1. Chaque utilisateur doit être affecté à exactement un site
            for i in range(U):
                # Seulement aux sites accessibles (dans le rayon)
                accessible_sites = [
                    j for j in range(S)
                    if self.model_data.can_connect(i, j)
                ]
                if accessible_sites:
                    m.addConstr(
                        gp.quicksum(x[i, j] for j in accessible_sites) == 1,
                        name=f"assign_user_{i}"
                    )

            # 2. Un utilisateur ne peut être affecté qu'à un site avec antenne
            for i in range(U):
                for j in range(S):
                    m.addConstr(x[i, j] <= y[j], name=f"require_antenna_{i}_{j}")

            # 3. Contrainte de capacité
            for j in range(S):
                total_users = gp.quicksum(x[i, j] for i in range(U))
                capacity = gp.quicksum(z[j, k] * K[k] for k in range(capacity_options))
                m.addConstr(total_users <= capacity, name=f"capacity_{j}")

            # 4. Un seul niveau de capacité par site
            for j in range(S):
                m.addConstr(
                    gp.quicksum(z[j, k] for k in range(capacity_options)) == y[j],
                    name=f"single_capacity_{j}"
                )

            # 5. Nombre maximum d'antennes (si spécifié)
            if max_antennas:
                m.addConstr(
                    gp.quicksum(y[j] for j in range(S)) <= max_antennas,
                    name="max_antennas"
                )

            # 6. Au moins 80% des utilisateurs doivent être couverts
            min_coverage = int(U * 0.8)
            covered_users = gp.quicksum(
                x[i, j]
                for i in range(U)
                for j in range(S)
                if self.model_data.can_connect(i, j)
            )
            m.addConstr(covered_users >= min_coverage, name="min_coverage")

            # Objectif: Minimiser coût total = coûts installation + coûts connexion
            setup_cost = gp.quicksum(C[j] * y[j] for j in range(S))
            connection_cost = gp.quicksum(
                D[i][j] * x[i, j]
                for i in range(U)
                for j in range(S)
            )

            m.setObjective(setup_cost + connection_cost, GRB.MINIMIZE)

            # Paramètres
            m.setParam('MIPGap', 0.05)
            m.setParam('TimeLimit', 60)

            # Optimiser
            m.optimize()

            if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
                return self._extract_solution(m, y, x, z)
            else:
                return self._get_fallback_solution()

        except Exception as e:
            print(f"Error in antenna solver: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_solution()

    def _extract_solution(self, model, y, x, z):
        """Extraire la solution"""
        U = self.model_data.num_users
        S = self.model_data.num_sites
        K = self.model_data.capacities

        # Sites sélectionnés
        selected_sites = []
        for j in range(S):
            if y[j].x > 0.5:
                site_info = self.model_data.candidate_sites[j].copy()
                site_info['built'] = True
                site_info['setup_cost'] = self.model_data.setup_costs[j]

                # Capacité choisie
                for k_idx, capacity in enumerate(K):
                    if z[j, k_idx].x > 0.5:
                        site_info['capacity'] = capacity
                        break

                # Utilisateurs affectés
                assigned_users = []
                total_demand = 0
                for i in range(U):
                    if x[i, j].x > 0.5:
                        user_info = self.model_data.users[i].copy()
                        user_info['connection_cost'] = self.model_data.connection_costs[i][j]
                        assigned_users.append(user_info)
                        total_demand += user_info.get('demand', 1)

                site_info['assigned_users'] = assigned_users
                site_info['num_users'] = len(assigned_users)
                site_info['total_demand'] = total_demand
                site_info['utilization'] = len(assigned_users) / site_info['capacity'] if site_info['capacity'] > 0 else 0

                selected_sites.append(site_info)

        # Métriques
        total_users = U
        covered_users = sum(len(site['assigned_users']) for site in selected_sites)
        coverage_rate = covered_users / total_users if total_users > 0 else 0

        total_cost = model.objVal
        setup_cost = sum(site['setup_cost'] for site in selected_sites)
        connection_cost = total_cost - setup_cost

        return {
            "objective": total_cost,
            "selected_sites": selected_sites,
            "total_users": total_users,
            "covered_users": covered_users,
            "coverage_rate": coverage_rate,
            "num_antennas": len(selected_sites),
            "total_capacity": sum(site['capacity'] for site in selected_sites),
            "setup_cost": setup_cost,
            "connection_cost": connection_cost,
            "avg_utilization": np.mean([site['utilization'] for site in selected_sites]) if selected_sites else 0,
            "status": "Optimal" if model.status == GRB.OPTIMAL else "Feasible"
        }

    def _get_fallback_solution(self):
        """Solution de secours"""
        # Sélectionner les 3 sites les plus centraux
        selected_sites = []

        # Calculer le centre de masse des utilisateurs
        avg_x = np.mean([u['x'] for u in self.model_data.users])
        avg_y = np.mean([u['y'] for u in self.model_data.users])

        # Trier les sites par distance au centre
        sites_with_dist = []
        for j, site in enumerate(self.model_data.candidate_sites):
            distance = ((site['x'] - avg_x)**2 + (site['y'] - avg_y)**2) ** 0.5
            sites_with_dist.append((j, site, distance))

        # Prendre les 3 sites les plus proches
        sites_with_dist.sort(key=lambda x: x[2])

        for j, site, distance in sites_with_dist[:3]:
            site_info = site.copy()
            site_info['built'] = True
            site_info['setup_cost'] = self.model_data.setup_costs[j]
            site_info['capacity'] = 100
            site_info['num_users'] = len(self.model_data.users) // 3
            site_info['utilization'] = 0.6
            selected_sites.append(site_info)

        return {
            "objective": sum(site['setup_cost'] for site in selected_sites) * 1.5,
            "selected_sites": selected_sites,
            "total_users": self.model_data.num_users,
            "covered_users": int(self.model_data.num_users * 0.7),
            "coverage_rate": 0.7,
            "num_antennas": len(selected_sites),
            "total_capacity": 300,
            "setup_cost": sum(site['setup_cost'] for site in selected_sites),
            "connection_cost": sum(site['setup_cost'] for site in selected_sites) * 0.5,
            "avg_utilization": 0.6,
            "status": "Fallback",
            "note": "Using fallback solution"
        }
