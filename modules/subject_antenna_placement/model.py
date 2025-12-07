class AntennaPlacementModel:
    """Modèle pour le placement d'antennes télécom et affectation des utilisateurs"""

    def __init__(self, users, candidate_sites, setup_costs=None, connection_costs=None,
                 capacities=None, coverage_radius=None, max_antennas=None):
        """
        Args:
            users: Liste des utilisateurs [{"id": 0, "x": 1, "y": 2, "demand": 10}]
            candidate_sites: Sites candidats pour antennes [{"id": 0, "x": 1, "y": 2}]
            setup_costs: Coûts d'installation par site
            connection_costs: Matrice coût connexion user-site
            capacities: Capacités des antennes (utilisateurs max)
            coverage_radius: Rayon de couverture maximal
            max_antennas: Nombre maximum d'antennes à installer
        """
        self.users = users
        self.candidate_sites = candidate_sites
        self.num_users = len(users)
        self.num_sites = len(candidate_sites)

        # Coûts par défaut
        self.setup_costs = setup_costs if setup_costs else [
            10000 + 5000 * (i % 3)  # Coûts variables selon le site
            for i in range(self.num_sites)
        ]

        # Capacités par défaut
        self.capacities = capacities if capacities else [
            50, 100, 150, 200  # Capacités disponibles
        ]

        self.coverage_radius = coverage_radius if coverage_radius else 5.0
        self.max_antennas = max_antennas

        # Calculer les distances et coûts de connexion
        self.connection_costs = self._calculate_connection_costs(connection_costs)

    def _calculate_connection_costs(self, provided_costs):
        """Calculer les coûts de connexion basés sur la distance"""
        if provided_costs is not None:
            return provided_costs

        costs = [[0.0] * self.num_sites for _ in range(self.num_users)]

        for i, user in enumerate(self.users):
            for j, site in enumerate(self.candidate_sites):
                # Distance euclidienne
                distance = ((user['x'] - site['x'])**2 + (user['y'] - site['y'])**2) ** 0.5

                # Coût proportionnel à la distance
                if distance <= self.coverage_radius:
                    costs[i][j] = distance * 100  # 100€ par unité de distance
                else:
                    costs[i][j] = float('inf')  # Impossible de connecter

        return costs

    def can_connect(self, user_idx, site_idx):
        """Vérifier si un utilisateur peut se connecter à un site"""
        return self.connection_costs[user_idx][site_idx] < float('inf')

    def get_user_position(self, user_idx):
        user = self.users[user_idx]
        return user['x'], user['y']

    def get_site_position(self, site_idx):
        site = self.candidate_sites[site_idx]
        return site['x'], site['y']
