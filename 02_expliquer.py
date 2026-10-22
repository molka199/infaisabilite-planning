"""Étape 2 — Expliquer l'infaisabilité de S2 et S3, de trois façons complémentaires.

a) IIS de Gurobi (computeIIS) : sous-système d'inégalités irréductible (Chinneck & Dravnieks, 1991).
b) Filtre de suppression (modele.py) sur les GROUPES métier : on retire chaque groupe à tour de rôle et on le garde
   seulement si le retirer rend le problème faisable. Résultat : un MUS lisible par un cadre de santé.
c) Leviers (feasRelax) : pour chaque type de contrainte négociable, de combien faut-il la relâcher ?
"""
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from donnees import JOURS, POSTES, INFIRMIERES, scenario, besoin
from modele import construire, phrase, filtre_suppression, manque_minimal

LEVIERS = {"couverture": "baisser les besoins", "max_nuits": "autoriser des nuits en plus",
           "conges": "déplacer des congés", "max_jours": "faire travailler plus de jours"}


def iis_gurobi(s):
    m = construire(s)[0]
    m.optimize()
    m.computeIIS()
    noms = [c.ConstrName.split("#")[0] for c in m.getConstrs() if c.IISConstr]
    return len(noms), sorted({n for n in noms if not n.startswith("structurel")})


def leviers(s):
    return {texte: manque_minimal(s, t) for t, texte in LEVIERS.items()
            if any(g.startswith(t + "|") for g in construire(s)[2])}


def resume(s, mus):
    """Explication agrégée : une phrase au lieu d'une liste (granularité de l'explication)."""
    couv = [g.split("|")[1:] for g in mus if g.startswith("couverture")]
    demande = sum(besoin(s, j, p) for j, p in couv)
    if any(g.startswith("conges") for g in mus):
        jours = sorted({j for j, _ in couv})
        presents = len(INFIRMIERES) - sum(g.startswith("conges") for g in mus)
        return f"{', '.join(jours)} : {demande} agents demandés, {presents} présents."
    capa = sum(s["max_nuits"] for g in mus if g.startswith("max_nuits"))
    return f"{demande} nuits demandées sur la semaine, la règle en autorise {capa}."


def carte(ax, s, mus):
    grille = np.zeros((len(INFIRMIERES) + 2, 7))
    for r, p in enumerate(POSTES):
        for c, j in enumerate(JOURS):
            grille[r, c] = 3 if f"couverture|{j}|{p}" in mus else 0
    for r, i in enumerate(INFIRMIERES, start=2):
        if any(g.endswith("|" + i) and not g.startswith("conges") for g in mus):
            grille[r, :] = 1
        for j in s["conges"].get(i, []):
            grille[r, JOURS.index(j)] = 3 if f"conges|{i}" in mus else 2
    ax.imshow(grille, cmap=ListedColormap(["#f2f2f2", "#f6d5cc", "#cfcfcf", "#c8553d"]), vmin=0, vmax=3,
              aspect="auto")
    ax.axhline(1.5, color="black", lw=2)
    ax.set_xticks(range(7))
    ax.set_xticklabels(JOURS)
    ax.set_yticks(range(len(INFIRMIERES) + 2))
    ax.set_yticklabels(["besoin J", "besoin N"] + INFIRMIERES)
    ax.set_xticks(np.arange(-0.5, 7), minor=True)
    ax.set_yticks(np.arange(-0.5, len(INFIRMIERES) + 2), minor=True)
    ax.grid(which="minor", color="white", lw=1.5)
    ax.tick_params(which="minor", length=0)


fig, axes = plt.subplots(2, 2, figsize=(15, 9), width_ratios=[1, 1.25])
for row, nom in zip(axes, ["S2_conges", "S3_regles"]):
    s = scenario(nom)
    n_ineq, iis = iis_gurobi(s)
    mus, appels = filtre_suppression(s)
    lev = leviers(s)

    print(f"=== {nom} : INFEASIBLE ===")
    print(f"a) IIS Gurobi : {n_ineq} inégalités, {len(iis)} groupes métier")
    print(f"b) Conflit minimal (MUS) : {len(mus)} groupes, trouvé en {appels} appels au solveur")
    print(f"   En résumé : {resume(s, mus)}")
    for g in mus:
        print(f"   - {phrase(g, s)}")
    print("   identique à l'IIS de Gurobi" if set(mus) == set(iis) else "   différent de l'IIS de Gurobi")
    print("c) Leviers pour rendre le planning faisable :")
    for texte, v in lev.items():
        print(f"   - {texte} : {'ne suffit pas' if v is None else f'{v} unité(s)'}")
    print()

    carte(row[0], s, mus)
    row[0].set_title(f"{nom} — conflit minimal de {len(mus)} groupes", fontweight="bold")
    resume_types = ", ".join(f"{c} × {t}" for t, c in Counter(g.split("|")[0] for g in mus).items())
    texte = ["En une phrase :", f"  {resume(s, mus)}", "",
             f"En détail ({resume_types}) :"] + [f"  • {phrase(g, s)}" for g in mus[:9]]
    if len(mus) > 9:
        texte.append(f"  • … et {len(mus) - 9} autres")
    texte += ["", "Que faire ? (relâchement minimal, feasRelax)"]
    texte += [f"  • {t} : {'ne suffit pas' if v is None else f'{v} unité(s)'}" for t, v in lev.items()]
    row[1].axis("off")
    row[1].text(0, 1, "\n".join(texte), va="top", fontsize=10, family="DejaVu Sans")

fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in ["#c8553d", "#f6d5cc", "#cfcfcf"]],
           labels=["élément du conflit", "infirmière concernée par une règle du conflit", "congé hors conflit"],
           loc="lower center", ncol=3)
fig.suptitle("Ce que pourrait voir le cadre : le conflit localisé, expliqué en français, avec les leviers",
             fontweight="bold")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("figures/2_explication_du_conflit.png", dpi=150)
print("figures/2_explication_du_conflit.png")
