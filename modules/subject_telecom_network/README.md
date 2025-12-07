# Conception de Réseau de Fibre Optique

## Problème
Déterminer quelles connexions établir dans un réseau de télécommunications et avec quelle capacité pour minimiser le coût total tout en supportant le flux requis entre les nœuds.

## Modélisation Mathématique (PLNE)

### Variables
- yₗ ∈ {0,1}: 1 si la liaison l est construite
- zₗₖ ∈ {0,1}: 1 si la capacité k est choisie pour la liaison l
- xₗᵢⱼ ≥ 0: Flux sur la liaison l pour la paire (i,j)

### Objectif
Minimiser: Σₗ (fₗ·yₗ + Σₖ vₗ·Cₖ·zₗₖ)

### Contraintes
1. Sélection de capacité unique: Σₖ zₗₖ ≤ yₗ ∀l
2. Capacité: ΣᵢΣⱼ xₗᵢⱼ ≤ Σₖ Cₖ·zₗₖ ∀l
3. Conservation de flux: Σₗ∈δ⁺(v) xₗᵢⱼ - Σₗ∈δ⁻(v) xₗᵢⱼ = {dᵢⱼ si v=i; -dᵢⱼ si v=j; 0 sinon} ∀i,j,v
4. Budget: Σₗ (fₗ·yₗ + Σₖ vₗ·Cₖ·zₗₖ) ≤ B

## Données d'Entrée
- Nœuds: positions géographiques
- Liaisons potentielles: distances entre nœuds
- Demandes: matrice de trafic entre paires
- Coûts: fixes (installation) + variables (par capacité)
- Capacités disponibles: options de débit
- Budget (optionnel)

## Solution
Le solveur détermine:
- Quelles liaisons construire
- Quelle capacité attribuer à chaque liaison
- Comment router le trafic
- Coût total minimal
