# Optimisation de Localisation des Boîtes aux Lettres

## Problème
Déterminer les emplacements optimaux pour installer un nombre limité de boîtes aux lettres afin de maximiser la couverture de la population tout en respectant les contraintes budgétaires et opérationnelles.

## Modélisation Mathématique (PLNE)

### Variables
- xⱼ, yⱼ : Coordonnées de la boîte aux lettres j
- zⱼ ∈ {0,1} : 1 si une boîte est installée à l'emplacement j, 0 sinon
- cᵢⱼ ∈ {0,1} : 1 si le point de demande i est couvert par la boîte j

### Objectif
Maximiser: Σᵢ Σⱼ cᵢⱼ·populationᵢ

### Contraintes
1. Budget: Σⱼ coûtⱼ·zⱼ ≤ Budget_max
2. Couverture: cᵢⱼ ≤ zⱼ ∀i, j
3. Distance maximale: cᵢⱼ = 0 si distance(i, j) > D_max
4. Capacité: Σᵢ demande_i·cᵢⱼ ≤ capacité_j·zⱼ ∀j

## Données d'Entrée
- **Points de demande:** Coordonnées géographiques et population associée
- **Emplacements potentiels:** Coordonnées et coûts d'installation
- **Distance maximale:** Distance au-delà de laquelle un point n'est pas couvert
- **Budget:** Limite budgétaire totale
- **Capacité:** Capacité de chaque boîte aux lettres

## Solution
Le solveur détermine:
- **Emplacements optimaux:** Où installer les boîtes aux lettres
- **Couverture maximale:** Population totale couverte
- **Coût total:** Coût d'installation des boîtes
- **Accessibilité:** Distance moyenne de la population aux boîtes

## Approche de Résolution
1. **Modèle simplifié:** Utilise une distance maximale pour limiter les connexions possibles
2. **Optimisation:** Maximise la couverture tout en respectant les contraintes budgétaires et de capacité
3. **Résultats garantis:** Retourne toujours une solution faisable (même si sous-optimale)

## Exemple d'Application
**Services Postaux Urbains:**
- Points de demande: Quartiers d'une ville
- Emplacements potentiels: Intersections principales
- Objectif: Maximiser la couverture des habitants avec budget limité

**Services Publics Ruraux:**
- Points de demande: Villages isolés
- Emplacements potentiels: Centres communautaires
- Objectif: Assurer un accès minimal à tous les habitants