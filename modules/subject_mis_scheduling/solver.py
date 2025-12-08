import gurobipy as gp
from gurobipy import GRB

from .model import MISModel


class MISSolver:
    """Solveur PLNE pour l'Ensemble Indépendant Maximum"""

    def __init__(self, tasks, conflicts, **kwargs):
        self.model_data = MISModel(
            tasks=tasks,
            conflicts=conflicts,
            weights=kwargs.get('weights')
        )

    def solve(self):
        """Résoudre le problème d'Ensemble Indépendant Maximum"""
        try:
            m = gp.Model("Maximum_Independent_Set")

            # Données
            n = self.model_data.num_tasks
            weights = self.model_data.weights

            # Variables de décision
            x = m.addVars(n, vtype=GRB.BINARY, name="select_task")

            # Contraintes : pour chaque conflit, au plus une tâche peut être sélectionnée
            for i in range(n):
                for j in range(i + 1, n):
                    if self.model_data.adjacency_matrix[i][j] == 1:
                        m.addConstr(x[i] + x[j] <= 1, name=f"conflict_{i}_{j}")

            # Objectif : maximiser la somme des poids des tâches sélectionnées
            m.setObjective(
                gp.quicksum(weights[i] * x[i] for i in range(n)),
                GRB.MAXIMIZE
            )

            # Paramètres
            m.setParam('MIPGap', 0.01)  # 1% optimality gap
            m.setParam('TimeLimit', 30)  # 30 secondes max

            # Optimiser
            m.optimize()

            if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
                return self._extract_solution(m, x)
            else:
                return self._get_fallback_solution()

        except Exception as e:
            print(f"Error in MIS solver: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_solution()

    def _extract_solution(self, model, x):
        """Extraire la solution"""
        n = self.model_data.num_tasks

        # Tâches sélectionnées
        selected_tasks = []
        for i in range(n):
            if x[i].x > 0.5:  # Tâche sélectionnée
                task_info = self.model_data.tasks[i].copy()
                task_info['selected'] = True
                task_info['weight'] = self.model_data.weights[i]

                # Trouver les conflits de cette tâche
                conflicts = self.model_data.get_task_conflicts(i)
                task_info['conflicting_tasks'] = conflicts
                task_info['num_conflicts'] = len(conflicts)

                selected_tasks.append(task_info)

        # Métriques
        total_weight = sum(task['weight'] for task in selected_tasks)
        total_tasks = len(selected_tasks)

        # Vérifier la validité (aucun conflit dans l'ensemble sélectionné)
        valid = True
        for i, task1 in enumerate(selected_tasks):
            for task2 in selected_tasks[i + 1:]:
                if self.model_data.are_conflicting(task1['id'], task2['id']):
                    valid = False
                    break
            if not valid:
                break

        return {
            "objective": model.objVal,
            "selected_tasks": selected_tasks,
            "total_tasks": total_tasks,
            "total_weight": total_weight,
            "is_valid": valid,
            "total_possible_tasks": n,
            "selection_ratio": total_tasks / n if n > 0 else 0,
            "status": "Optimal" if model.status == GRB.OPTIMAL else "Feasible"
        }

    def _get_fallback_solution(self):
        """Solution de secours : algorithme glouton"""
        n = self.model_data.num_tasks
        weights = self.model_data.weights

        # Algorithme glouton : sélectionner les tâches avec le plus petit degré d'abord
        selected = []
        remaining = list(range(n))

        # Trier par degré (nombre de conflits) croissant
        task_degrees = [(i, self.model_data.get_task_degree(i)) for i in range(n)]
        task_degrees.sort(key=lambda x: x[1])  # Plus petit degré d'abord

        selected_indices = []

        for task_id, _ in task_degrees:
            # Vérifier si la tâche peut être ajoutée (pas de conflit avec les déjà sélectionnées)
            can_add = True
            for selected_id in selected_indices:
                if self.model_data.adjacency_matrix[task_id][selected_id] == 1:
                    can_add = False
                    break

            if can_add:
                selected_indices.append(task_id)

        # Construire la solution
        selected_tasks = []
        for task_id in selected_indices:
            task_info = self.model_data.tasks[task_id].copy()
            task_info['selected'] = True
            task_info['weight'] = weights[task_id]
            task_info['conflicting_tasks'] = self.model_data.get_task_conflicts(task_id)
            task_info['num_conflicts'] = len(task_info['conflicting_tasks'])
            selected_tasks.append(task_info)

        total_weight = sum(weights[i] for i in selected_indices)

        return {
            "objective": total_weight,
            "selected_tasks": selected_tasks,
            "total_tasks": len(selected_tasks),
            "total_weight": total_weight,
            "is_valid": True,  # Garanti par l'algorithme
            "total_possible_tasks": n,
            "selection_ratio": len(selected_tasks) / n if n > 0 else 0,
            "status": "Fallback (Greedy)",
            "note": "Using greedy algorithm as fallback"
        }
