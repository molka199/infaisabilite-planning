"""Étape 1 — Résoudre les trois scénarios.

S1 donne un planning. S2 et S3 renvoient seulement INFEASIBLE : le solveur ne dit pas pourquoi.
C'est exactement le point de départ du stage.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from gurobipy import GRB
from donnees import SCENARIOS, JOURS, INFIRMIERES, scenario
from modele import construire

os.makedirs("figures", exist_ok=True)
fig, axes = plt.subplots(1, 3, figsize=(15, 3.8))

for ax, nom in zip(axes, SCENARIOS):
    s = scenario(nom)
    m, x, groupes = construire(s)
    m.optimize()
    statut = "FAISABLE" if m.Status == GRB.OPTIMAL else "INFEASIBLE"
    print(f"{nom:<10} {statut:<11} ({len(groupes)} groupes de contraintes)")
    ax.set_title(nom, fontweight="bold")
    ax.set_xticks(range(7))
    ax.set_xticklabels(JOURS)
    ax.set_yticks(range(6))
    ax.set_yticklabels(INFIRMIERES)

    if statut == "FAISABLE":
        grille = np.array([[1 if x[i, j, "J"].X > 0.5 else 2 if x[i, j, "N"].X > 0.5 else 0
                            for j in JOURS] for i in INFIRMIERES])
        ax.imshow(grille, cmap=ListedColormap(["#f2f2f2", "#f4a261", "#264653"]), aspect="auto")
        for (r, c), v in np.ndenumerate(grille):
            if v:
                ax.text(c, r, "JN"[v - 1], ha="center", va="center", color="white" if v == 2 else "black")
    else:
        ax.imshow(np.zeros((6, 7)), cmap=ListedColormap(["#f2f2f2"]), aspect="auto")
        ax.text(3, 2.5, "INFEASIBLE\n\naucune solution…\net aucune explication",
                ha="center", va="center", fontsize=12, color="#c8553d", fontweight="bold")

fig.suptitle("Ce que voit un cadre de santé aujourd'hui : un planning, ou un simple « INFEASIBLE »",
             fontweight="bold")
fig.tight_layout()
fig.savefig("figures/1_ce_que_voit_le_cadre.png", dpi=150)
print("figures/1_ce_que_voit_le_cadre.png")
