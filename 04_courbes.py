"""Étape 4 — Trois courbes simples pour lire les résultats d'un coup d'œil.

4 : combien de postes restent non couverts selon l'effectif (impact des effectifs disponibles) ;
5 : combien selon la règle des nuits (impact d'une contrainte réglementaire) ;
6 : les leviers de S2 et S3 côte à côte (que faut-il changer, et de combien ?).
Le « manque » est le plus petit nombre de postes non couverts, calculé par feasRelax.
"""
import matplotlib.pyplot as plt
from donnees import BASE, scenario
from modele import manque_minimal

plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
COULEURS = {1: "#2a9d8f", 2: "#e9c46a", 3: "#c8553d"}


def cas(effectif, nuit, max_nuits=2):
    return dict(BASE, nom="courbe", besoin={"J": 2, "N": nuit}, conges={}, besoin_special={},
                max_nuits=max_nuits, equipe=[f"I{k + 1}" for k in range(effectif)])


def courbe(ax, xs, construire_cas, xlabel):
    for nuit, c in COULEURS.items():
        ys = [manque_minimal(construire_cas(x, nuit)) for x in xs]
        ax.plot(xs, ys, "o-", color=c, lw=2.5, ms=7, label=f"{nuit} agent(s) de nuit par jour")
        x0 = next((x for x, y in zip(xs, ys) if y == 0), None)
        if x0 is None:
            ax.annotate("jamais faisable : assouplir la règle\nne suffit pas, il manque du personnel",
                        (xs[-1], ys[-1]), xytext=(xs[-1] - 1.6, ys[-1] + 3), color=c, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=c))
        else:
            ax.annotate(f"faisable dès {x0}", (x0, 0), xytext=(x0 + 0.15, 2 + 2.5 * nuit), color=c,
                        fontweight="bold", arrowprops=dict(arrowstyle="->", color=c))
        print(f"   {nuit} nuit(s) : manque = {ys}")
    ax.axhline(0, color="black", lw=0.8)
    ax.set(xlabel=xlabel, ylabel="postes non couverts (minimum)")
    ax.set_xticks(list(xs))
    ax.legend(frameon=False)


print("Figure 4 : manque selon l'effectif (2 agents de jour, 2 nuits max)")
fig, ax = plt.subplots(figsize=(9, 5.5))
courbe(ax, range(3, 13), lambda e, n: cas(e, n), "nombre d'infirmières dans le service")
ax.set_title("Plus il y a de personnel, moins il manque de postes", fontweight="bold")
fig.tight_layout()
fig.savefig("figures/4_manque_selon_effectif.png", dpi=150)

print("Figure 5 : manque selon la règle des nuits (6 infirmières, 2 agents de jour)")
fig, ax = plt.subplots(figsize=(9, 5.5))
courbe(ax, range(1, 6), lambda r, n: cas(6, n, max_nuits=r), "nombre de nuits autorisées par semaine et par infirmière")
ax.set_title("À effectif égal, une règle plus souple peut suffire", fontweight="bold")
fig.tight_layout()
fig.savefig("figures/5_manque_selon_regle_nuits.png", dpi=150)

print("Figure 6 : leviers de S2 et S3")
leviers = {"baisser les besoins": "couverture", "déplacer des congés": "conges",
           "autoriser des nuits en plus": "max_nuits", "faire travailler plus de jours": "max_jours"}
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)
for ax, nom in zip(axes, ["S2_conges", "S3_regles"]):
    s = scenario(nom)
    for k, (texte, t) in enumerate(leviers.items()):
        v = manque_minimal(s, t)
        if v is None:
            ax.barh(k, 3, color="#eeeeee")
            sans_objet = t == "conges" and not s["conges"]
            ax.text(0.1, k, "sans objet (aucun congé)" if sans_objet else "ne suffit pas", va="center",
                    color="dimgray")
        else:
            ax.barh(k, v, color="#2a6f97")
            ax.text(v + 0.05, k, f"{v} unité(s)", va="center", fontweight="bold")
        print(f"   {nom} - {texte} : {v}")
    ax.set_yticks(range(len(leviers)))
    ax.set_yticklabels(list(leviers))
    ax.set_xlim(0, 3.5)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_title(nom, fontweight="bold")
axes[0].invert_yaxis()
fig.suptitle("Que faut-il changer, et de combien ? (une seule action à la fois)", fontweight="bold")
fig.tight_layout()
fig.savefig("figures/6_leviers.png", dpi=150)
print("figures 4, 5, 6 -> figures/")
