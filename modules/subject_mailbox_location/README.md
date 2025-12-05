# Optimisation de Localisation des Boîtes aux Lettres

## Description du Problème et Application

---

### Contexte et Application Réelle
Ce module résout un problème d'optimisation de localisation des boîtes aux lettres (MCLP - Maximal Covering Location Problem) adapté aux besoins des services postaux. L'objectif est de déterminer les positions optimales pour installer un nombre limité de boîtes aux lettres afin de maximiser la population couverte tout en respectant des contraintes budgétaires et opérationnelles.

### Applications pratiques:
- Planification des services postaux en zones urbaines et rurales

- Optimisation des infrastructures de collecte du courrier

- Allocation des ressources dans les services publics

- Amélioration de l'accessibilité aux services postaux

### Problématique

Étant donné une population distribuée géographiquement avec différents besoins (demande), un budget limité et des contraintes de capacité, il faut :

1- Déterminer où placer les boîtes aux lettres

2- Déterminer combien de boîtes installer

3- Maximiser la population couverte

4- Minimiser les coûts totaux

5- Respecter les contraintes techniques et budgétaires

---

## Modélisation Mathématique
---

### Variables de Décision
- xⱼ, yⱼ : Coordonnées de la boîte aux lettres j (variables continues)

- zⱼ ∈ {0,1} : 1 si la boîte j est construite, 0 sinon

- uᵢⱼ ∈ {0,1} : 1 si le point de demande i est couvert par la boîte j

- cᵢ ∈ ℤ⁺ : Niveau de couverture du point i (0 à L_max)

### Paramètres
- I : Ensemble des points de demande (i = 1...n)

- J : Ensemble des boîtes aux lettres potentielles (j = 1...m)

- pᵢ : Population au point i

- dᵢ : Demande au point i

- R : Rayon de couverture maximal

- B : Budget total disponible

- Cⱼ : Coût d'installation de la boîte j

- Qⱼ : Capacité maximale de la boîte j

- L_max : Niveau maximal de couverture autorisé

### Fonction Objective
Maximiser la population couverte pondérée par les niveaux de couverture:
- Max ∑ᵢ (pᵢ × cᵢ)

### Contraintes
1- 1. Contrainte de Distance
Un point i est couvert par une boîte j seulement si la distance est inférieure au rayon R :

- (xᵢ - xⱼ)² + (yᵢ - yⱼ)² ≤ R² + M(1 - uᵢⱼ)   ∀i,∀j
- (xᵢ - xⱼ)² + (yᵢ - yⱼ)² ≥ R²(1 - uᵢⱼ)        ∀i,∀j

où M est une constante suffisamment grande.

2- Contrainte du Niveau de Couverture

- cᵢ = ∑ⱼ uᵢⱼ   ∀i
- 0 ≤ cᵢ ≤ L_max   ∀i

3- Contrainte de Capacité:
La demande totale affectée à une boîte ne peut dépasser sa capacité :

- ∑ᵢ (uᵢⱼ × dᵢ) ≤ Qⱼ × zⱼ   ∀j

4- Contrainte Budgétaire
- ∑ⱼ (Cⱼ × zⱼ) ≤ B

5- Contrainte du Nombre de Boites:
- ∑ⱼ zⱼ = m   (ou ≤ m selon la formulation)

## Composants de l'interface
1- 1. Panneau de Paramètres (Gauche)
Paramètres de base :

- Nombre de boîtes aux lettres

- Rayon de couverture

- Budget total disponible

- Niveau maximal de couverture

Tableaux de données :
- Points de demande : Coordonnées (x,y), population, demande, priorité

- Paramètres des boîtes : Coût, capacité, coût fixe

Boutons d'action :
- Ajout/suppression de lignes

- Lancement de l'optimisation

2. Panneau de Résultats (Droite)
Zone textuelle :

- Valeur objective optimale

- Positions des boîtes sélectionnées

- Statistiques de couverture

- Détails des variables de décision

Visualisation graphique :

- Carte interactive des positions

- Cercles de couverture

- Points colorés selon l'état de couverture

- Lignes de connexion boîtes→points

- Légende et statistiques intégrées