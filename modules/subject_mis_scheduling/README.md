# Optimisation de Planification MIS (Ensemble Indépendant Maximum)

## Problème
Sélectionner le maximum d'activités ou de tâches à planifier de manière à minimiser les conflits, en utilisant la théorie des ensembles indépendants maximaux.

## Modélisation Mathématique (PLNE)

### Variables
- xᵢ ∈ {0,1} : 1 si la tâche i est planifiée, 0 sinon
- conflitᵢⱼ ∈ {0,1} : 1 si les tâches i et j sont en conflit

### Objectif
Maximiser: Σᵢ xᵢ

### Contraintes
1. Conflits: xᵢ + xⱼ ≤ 1 si conflitᵢⱼ = 1 ∀i, j
2. Ressources: Σᵢ ressourceᵢ·xᵢ ≤ Ressources_max
3. Dépendances: xᵢ ≤ Σⱼ∈prédécesseurs xⱼ
4. Fenêtres temporelles: tᵢ_début ≥ t_global_min et tᵢ_fin ≤ t_global_max

## Données d'Entrée
- **Tâches:** Liste des tâches avec durées, ressources et contraintes
- **Matrice de conflits:** Indiquant les conflits entre tâches
- **Dépendances:** Relations de précédence entre tâches
- **Ressources disponibles:** Limite totale des ressources
- **Fenêtre temporelle:** Plage de temps pour la planification

## Solution
Le solveur détermine:
- **Tâches planifiées:** Liste des tâches sélectionnées
- **Conflits évités:** Nombre total de conflits supprimés
- **Utilisation des ressources:** Ressources totales utilisées
- **Efficacité:** Taux d'utilisation des ressources

## Approche de Résolution
1. **Modèle simplifié:** Utilise une matrice de conflits pour éviter les chevauchements
2. **Optimisation:** Maximise le nombre de tâches planifiées tout en respectant les contraintes
3. **Gestion des dépendances:** Respecte les relations de précédence entre tâches
4. **Résultats garantis:** Retourne toujours une solution faisable

## Exemple d'Application
**Planification de Conférences:**
- Tâches: Sessions de conférence avec horaires fixes
- Conflits: Sessions ayant des intervenants ou des publics communs
- Objectif: Maximiser le nombre de sessions sans chevauchement

**Planification Industrielle:**
- Tâches: Opérations de production avec durées variables
- Conflits: Opérations nécessitant les mêmes machines
- Objectif: Maximiser la production tout en respectant les ressources