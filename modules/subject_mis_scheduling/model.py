class MISModel:
    """Modèle pour l'Ensemble Indépendant Maximum (scheduling de tâches)"""

    def __init__(self, tasks, conflicts, weights=None):
        """
        Args:
            tasks: Liste des tâches [{"id": 0, "name": "Task1", "duration": 10, "priority": 2}]
            conflicts: Liste des conflits [(i, j)] où i et j sont incompatibles
            weights: Poids des tâches (par défaut: 1 ou priority)
        """
        self.tasks = tasks
        self.conflicts = conflicts
        self.num_tasks = len(tasks)

        # Créer la matrice d'adjacence
        self.adjacency_matrix = [[0] * self.num_tasks for _ in range(self.num_tasks)]
        for i, j in conflicts:
            if i < self.num_tasks and j < self.num_tasks:
                self.adjacency_matrix[i][j] = 1
                self.adjacency_matrix[j][i] = 1

        # Poids des tâches
        if weights:
            self.weights = weights
        else:
            self.weights = [task.get('priority', 1) for task in tasks]

    def are_conflicting(self, task_i, task_j):
        """Vérifier si deux tâches sont en conflit"""
        return self.adjacency_matrix[task_i][task_j] == 1

    def get_task_conflicts(self, task_id):
        """Obtenir la liste des tâches en conflit avec une tâche donnée"""
        return [j for j in range(self.num_tasks) if self.adjacency_matrix[task_id][j] == 1]

    def get_task_degree(self, task_id):
        """Degré du sommet (nombre de conflits)"""
        return sum(self.adjacency_matrix[task_id])
