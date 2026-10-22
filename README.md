# Initiation — Expliquer l'infaisabilité d'un planning hospitalier

## 1. Ma compréhension du sujet

Un cadre de santé construit un planning sous de nombreuses contraintes: besoins à couvrir, congés,
contrats, repos obligatoires. Quand ces contraintes se contredisent, le solveur répond seulement
« infaisable », sans dire pourquoi. Le sujet pose trois questions:

1. **Où est le conflit?** Trouver automatiquement un petit ensemble de contraintes incompatibles
   (un IIS en programmation linéaire, un MUS en programmation par contraintes).
2. **Comment l'expliquer?** Traduire ce conflit en phrases utiles pour le cadre, et dire quoi changer.
3. **Pourquoi certaines instances sont-elles infaisables?** Relier la faisabilité à des propriétés
   structurelles: effectifs, couverture des besoins, règles.

## 2. Ce que fait cette initiation

Un service fictif: 6 infirmières, 1 semaine, postes Jour et Nuit, modélisé en PLNE avec Gurobi.
Règles: couverture des besoins, un poste par jour, congés, repos le lendemain d'une nuit,
5 jours maximum, 2 nuits maximum. Trois scénarios:

- **S1**: situation normale, le planning existe;
- **S2**: quatre infirmières en congé le même mercredi (manque de ressources);
- **S3**: renfort de 2 agents chaque nuit sans changer la règle des nuits (règles trop restrictives).

| Ordre | Script | Ce qu'il montre |
|---|---|---|
| 1 | `01_resoudre.py` | S1 a un planning, S2 et S3 renvoient seulement « INFEASIBLE ». |
| 2 | `02_expliquer.py` | Le conflit est trouvé de deux façons, traduit en français, avec les leviers pour le résoudre. |
| 3 | `03_etude_structurelle.py` | On fait varier l'effectif et les besoins: le manque de personnel n'explique pas tout. |
| 4 | `04_courbes.py` | Trois courbes simples: effet de l'effectif, effet d'une règle, leviers de correction. |

`donnees.py` contient les scénarios et `modele.py` le modèle. Installation et lancement:

```bash
pip install gurobipy matplotlib numpy
python 01_resoudre.py
python 02_expliquer.py
python 03_etude_structurelle.py
python 04_courbes.py
```

Tout tourne en quelques secondes avec la licence gratuite de Gurobi (le modèle est petit).

## 3. Résultats

**Étape 1** (`figures/1_ce_que_voit_le_cadre.png`). Pour S2 et S3, le cadre n'obtient aucune
information. C'est le point de départ du sujet.

![Ce que voit le cadre](figures/1_ce_que_voit_le_cadre.png)

**Étape 2** (`figures/2_explication_du_conflit.png`). Trois outils complémentaires:

- **IIS de Gurobi** (`computeIIS`): un sous-ensemble irréductible d'inégalités en conflit
  (Chinneck & Dravnieks, 1991).
- **Filtre de suppression sur des groupes métier**: chaque contrainte porte le nom de son groupe
  (« congés d'Amira », « besoin du mercredi en Nuit »). On retire chaque groupe à tour de rôle et on
  le garde seulement s'il est nécessaire au conflit. On obtient un conflit minimal lisible.
  Il coïncide ici avec l'IIS de Gurobi.
- **Leviers** (`feasRelax`): pour chaque type de contrainte, de combien faut-il la relâcher pour
  retrouver un planning.

| Scénario | Conflit minimal | En une phrase | Leviers |
|---|---|---|---|
| S2 | 4 congés + 2 besoins du mercredi | mercredi: 3 agents demandés, 2 présents | baisser le besoin de 1, ou déplacer 1 congé |
| S3 | 7 besoins de nuit + 6 règles « 2 nuits max » | 14 nuits demandées, la règle en autorise 12 | baisser les besoins de 2, ou accorder 2 nuits de plus |

S3 montre une difficulté réelle du sujet: le conflit minimal contient 13 contraintes, trop pour un
cadre. La phrase agrégée est bien plus utile. **Choisir le bon niveau d'explication** est un des
enjeux du stage.

![Explication du conflit](figures/2_explication_du_conflit.png)

**Étape 3** (`figures/3_etude_structurelle.png`). Pour 90 combinaisons (3 à 12 infirmières,
1 à 3 agents de jour et de nuit), on compare le solveur à un simple comptage des capacités.
Presque toujours, le comptage suffit. Mais pour J=2, N=3, il annonce 7 infirmières alors qu'il en
faut 8: les 3 infirmières de la nuit précédente sont au repos, il faut donc 2 + 3 + 3 = 8 agents
chaque jour. Le conflit minimal trouvé par le filtre le confirme: 3 besoins + 7 règles de repos.
C'est une **infaisabilité due à l'interaction des règles**, invisible dans les chiffres
d'effectifs, et c'est exactement ce que la seconde partie du stage veut caractériser.

![Étude structurelle](figures/3_etude_structurelle.png)

**Étape 4** (figures 4 à 6). Le « manque » est le plus petit nombre de postes non couverts,
calculé par `feasRelax`; il vaut 0 quand le planning est faisable.

- `4_manque_selon_effectif.png`: avec 2 agents de jour, le planning devient faisable à partir de
  5, 7 ou 11 infirmières selon le besoin de nuit (1, 2 ou 3). C'est l'impact des **effectifs**.
- `5_manque_selon_regle_nuits.png`: avec 6 infirmières, autoriser 3 nuits au lieu de 2 suffit quand
  il faut 2 agents de nuit. Avec 3 agents de nuit, le manque reste bloqué à 6 quelle que soit la règle:
  il faut du personnel. C'est l'impact des **contraintes réglementaires**, et sa limite.
- `6_leviers.png`: pour S2 et S3, ce que chaque action corrige à elle seule. Cette lecture
  correspond aux explications « que faut-il changer » attendues par un cadre de santé.

![Manque selon l'effectif](figures/4_manque_selon_effectif.png)

![Manque selon la règle des nuits](figures/5_manque_selon_regle_nuits.png)

![Leviers](figures/6_leviers.png)

## 4. Ce que je retiens

- Une explication n'est utile que si elle est exprimée au **niveau métier** (groupes de contraintes),
  pas au niveau des inégalités du modèle.
- Il peut exister **plusieurs conflits minimaux**; savoir lequel montrer, ou comment les résumer,
  est une vraie question.
- Dire *pourquoi* (le conflit) ne suffit pas: le cadre a aussi besoin de *quoi changer* (les leviers).
- Les indicateurs simples d'effectif détectent la plupart des cas, mais pas ceux qui viennent de
  l'interaction des règles: ce sont les plus intéressants à étudier.

## 5. Ce que j'aimerais approfondir pendant le stage

- Tester sur des instances réelles et des benchmarks (INRC-II).
- Comparer le filtre de suppression à QuickXplain (Junker, 2004), plus économe en appels au solveur,
  et énumérer plusieurs conflits avec MARCO (Liffiton et al., 2016).
- Utiliser la programmation par contraintes (OR-Tools CP-SAT), où ces méthodes sont natives.
- Construire des indicateurs structurels plus fins, inspirés de Vanhoucke & Maenhout (2009),
  et étudier l'espace des instances (Smith-Miles & Lopes, 2012).
- Travailler sur la présentation des explications aux utilisateurs (Senthooran et al., 2021).

## 6. Références

1. J. W. Chinneck, E. W. Dravnieks (1991). *Locating Minimal Infeasible Constraint Sets in Linear
   Programs*. ORSA Journal on Computing, 3(2), 157–168.
2. J. W. Chinneck (2008). *Feasibility and Infeasibility in Optimization*. Springer.
3. U. Junker (2004). *QuickXplain: Preferred Explanations and Relaxations for Over-Constrained
   Problems*. AAAI 2004.
4. M. H. Liffiton, A. Previti, A. Malik, J. Marques-Silva (2016). *Fast, flexible MUS enumeration*.
   Constraints, 21(2), 223–250.
5. I. Senthooran et al. (2021). *Human-Centred Feasibility Restoration*. CP 2021, LIPIcs 210.
6. M. Vanhoucke, B. Maenhout (2009). *On the characterization and generation of nurse scheduling
   problem instances*. European Journal of Operational Research, 196(2), 457–467.
7. S. Ceschia, N. Dang, P. De Causmaecker, S. Haspeslagh, A. Schaerf (2019). *The Second International
   Nurse Rostering Competition*. Annals of Operations Research, 274, 171–186.
8. K. Smith-Miles, L. Lopes (2012). *Measuring instance difficulty for combinatorial optimization
   problems*. Computers & Operations Research, 39(5), 875–889.
