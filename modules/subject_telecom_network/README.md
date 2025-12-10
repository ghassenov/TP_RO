# Conception de Réseau de Fibre Optique

## Problème
Déterminer quelles connexions établir dans un réseau de télécommunications pour minimiser le coût total tout en permettant un échange raisonnable de trafic entre les villes.

## Modélisation Mathématique (PLNE)

### Variables
- yₗ ∈ {0,1}: 1 si la liaison l est construite
- fₗ ≥ 0: Flux total sur la liaison l (dans les deux directions)
- sᵢⱼ ≥ 0: Demande satisfaite entre les nœuds i et j

### Objectif
Minimiser: Σₗ cₗ·yₗ

### Contraintes
1. Capacité: fₗ ≤ C·yₗ ∀l (C = 1000 Gbps)
2. Satisfaction de demande: sᵢⱼ ≤ dᵢⱼ ∀i,j
3. Flux sortant minimum: Σₗ∈out(i) fₗ ≥ 0.3·Σⱼ dᵢⱼ ∀i
4. Flux entrant minimum: Σₗ∈in(i) fₗ ≥ 0.3·Σⱼ dⱼᵢ ∀i
5. Connectivité minimale: Σₗ connecté à i yₗ ≥ 1 ∀i
6. Budget: Σₗ cₗ·yₗ ≤ B (si spécifié)

## Données d'Entrée
- **Villes (nœuds):** positions géographiques avec noms
- **Liaisons potentielles:** distances entre villes
- **Matrice de demande:** trafic estimé entre chaque paire de villes
- **Coûts de construction:** proportionnels à la distance
- **Budget maximum** (optionnel)

## Solution
Le solveur détermine:
- **Quelles liaisons construire** (connexions en fibre optique)
- **Flux estimé** sur chaque liaison
- **Coût total** de construction
- **Connectivité** de chaque ville
- **Taux de satisfaction** de la demande globale

## Approche de Résolution
1. **Modèle simplifié:** Utilise un flux agrégé par liaison au lieu de flux par paire OD pour garantir la faisabilité
2. **Contraintes relaxées:** Objectif de 30% de satisfaction minimale (au lieu de 100%) pour éviter l'infeasibility
3. **Garantie de solution:** Retourne toujours un réseau faisable (étoile centrée sur Tunis si besoin)
4. **Optimisation:** Minimise les coûts tout en maximisant la connectivité

## Exemple d'Application
**Réseau Tunisien:**
- Tunis (centre principal)
- Sfax, Sousse, Kairouan, Bizerte, Gabès, Gafsa, Tozeur
- Connexions optimisées pour les échanges inter-villes
- Budget limité et distances réelles prises en compte
