import numpy as np


class TelecomNetworkModel:
    """Modèle pour la conception de réseau de fibre optique (PLNE)"""

    def __init__(self, nodes, potential_links, demands,
                 fixed_costs=None, variable_costs=None,
                 capacities=None, budget=None):
        """
        Args:
            nodes: Liste des nœuds du réseau [{"id": 0, "name": "A", "x": 0, "y": 0}]
            potential_links: Liste des liaisons potentielles [{"from": 0, "to": 1, "distance": 10}]
            demands: Matrice de demande entre paires de nœuds
            fixed_costs: Coûts fixes d'installation par liaison
            variable_costs: Coûts variables par unité de capacité
            capacities: Capacités disponibles pour chaque liaison
            budget: Budget total disponible
        """
        self.nodes = nodes
        self.potential_links = potential_links
        self.demands = demands
        self.num_nodes = len(nodes)
        self.num_links = len(potential_links)

        # Coûts par défaut
        self.fixed_costs = fixed_costs if fixed_costs else [
            1000 + 500 * link.get('distance', 1) / 10
            for link in potential_links
        ]

        self.variable_costs = variable_costs if variable_costs else [
            50 * link.get('distance', 1) / 10
            for link in potential_links
        ]

        self.capacities = capacities if capacities else [
            100, 200, 500, 1000  # Capacités disponibles (Gbps)
        ]

        self.budget = budget
        self.capacity_options = len(self.capacities)

    def get_node_position(self, node_id):
        """Retourne les coordonnées d'un nœud"""
        for node in self.nodes:
            if node['id'] == node_id:
                return node['x'], node['y']
        return 0, 0

    def calculate_distance(self, node1_id, node2_id):
        """Calcule la distance euclidienne entre deux nœuds"""
        x1, y1 = self.get_node_position(node1_id)
        x2, y2 = self.get_node_position(node2_id)
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def get_demand(self, source, destination):
        """Retourne la demande entre deux nœuds"""
        if source < self.num_nodes and destination < self.num_nodes:
            return self.demands[source][destination]
        return 0
