# Optimisation du Placement d'Antennes

## Problème
Déterminer les positions optimales pour installer un nombre limité d'antennes afin de minimiser les interférences et maximiser la couverture de signal dans une zone donnée.

## Modélisation Mathématique (PLNE)

### Variables
- xⱼ, yⱼ : Coordonnées de l'antenne j
- zⱼ ∈ {0,1} : 1 si l'antenne j est construite, 0 sinon
- cᵢⱼ ∈ {0,1} : 1 si le point i est couvert par l'antenne j

### Objectif
Maximiser: Σᵢ Σⱼ cᵢⱼ

### Contraintes
1. Budget: Σⱼ coûtⱼ·zⱼ ≤ Budget_max
2. Couverture: cᵢⱼ ≤ zⱼ ∀i, j
3. Portée: cᵢⱼ = 0 si distance(i, j) > Portée_max
4. Interférences minimales: Σⱼ connecté à i zⱼ ≤ k_max ∀i

## Données d'Entrée
- **Points de couverture:** Coordonnées géographiques et demande associée
- **Emplacements potentiels:** Coordonnées et coûts d'installation des antennes
- **Portée maximale:** Distance au-delà de laquelle le signal ne peut pas atteindre
- **Budget maximum:** Limite budgétaire totale
- **Interférence maximale:** Nombre maximal d'antennes pouvant couvrir un point

## Solution
Le solveur détermine:
- **Positions optimales:** Où installer les antennes
- **Couverture maximale:** Points couverts avec couverture suffisante
- **Coût total:** Coût d'installation des antennes
- **Interférences:** Niveau d'interférence pour chaque point

## Approche de Résolution
1. **Modèle simplifié:** Utilise une portée maximale pour limiter les connexions possibles
2. **Optimisation:** Maximise la couverture tout en respectant les contraintes budgétaires
3. **Gestion d'interférences:** Limite le nombre d'antennes couvrant chaque point
4. **Résultats garantis:** Retourne toujours une solution faisable

## Exemple d'Application
**Réseau Mobile Urbain:**
- Points de couverture: Quartiers d'une ville
- Emplacements potentiels: Toits d'immeubles, pylônes existants
- Objectif: Maximiser la couverture 5G avec budget limité
- Budget limité et distances réelles prises en compte