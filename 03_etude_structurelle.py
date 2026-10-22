"""Étape 3 — Quelles caractéristiques rendent un planning infaisable ?

On fait varier l'effectif (3 à 12 infirmières) et les besoins (Jour, Nuit), on résout chaque cas,
et on compare au simple comptage des capacités :
    effectif × max_jours ≥ besoins totaux,  effectif × max_nuits ≥ nuits demandées,
    effectif ≥ besoin d'une journée.
Si le comptage dit « possible » mais le solveur dit « infaisable », l'infaisabilité vient de
l'interaction des règles (repos après une nuit, etc.) : c'est une infaisabilité « cachée ».
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from donnees import BASE
from collections import Counter
from modele import faisable, construire, filtre_suppression

EFFECTIFS = range(3, 13)
BESOINS = [(j, n) for j in (1, 2, 3) for n in (1, 2, 3)]   # (besoin Jour, besoin Nuit)


def cas(effectif, bj, bn):
    s = dict(BASE, nom="etude", besoin={"J": bj, "N": bn}, conges={}, besoin_special={}, max_nuits=3,
             equipe=[f"I{k + 1}" for k in range(effectif)])
    return s


def comptage_ok(s, effectif):
    bj, bn = s["besoin"]["J"], s["besoin"]["N"]
    return (effectif * s["max_jours"] >= 7 * (bj + bn) and effectif * s["max_nuits"] >= 7 * bn
            and effectif >= bj + bn)


classe = np.zeros((len(BESOINS), len(EFFECTIFS)))   # 0 faisable, 1 détecté par comptage, 2 caché
for r, (bj, bn) in enumerate(BESOINS):
    for c, e in enumerate(EFFECTIFS):
        s = cas(e, bj, bn)
        ok = faisable(s, construire(s)[2])
        classe[r, c] = 0 if ok else (2 if comptage_ok(s, e) else 1)
        assert ok <= comptage_ok(s, e)   # le comptage est une condition nécessaire

mini_solveur = [EFFECTIFS[list(classe[r]).index(0)] for r in range(len(BESOINS))]
mini_comptage = [next(e for e in EFFECTIFS if comptage_ok(cas(e, bj, bn), e)) for bj, bn in BESOINS]
print(f"{'besoin (J, N)':<14}{'effectif min. (comptage)':<27}{'effectif min. (solveur)'}")
for (bj, bn), a, b in zip(BESOINS, mini_comptage, mini_solveur):
    print(f"({bj}, {bn}){'':<8}{a:<27}{b}{'   <- règles' if b > a else ''}")
print(f"Infaisabilités cachées : {(classe == 2).sum()} cas sur {(classe > 0).sum()} infaisables")
for r, c in zip(*np.where(classe == 2)):
    (bj, bn), e = BESOINS[r], EFFECTIFS[c]
    mus, _ = filtre_suppression(cas(e, bj, bn))
    types = Counter(g.split("|")[0] for g in mus)
    print(f"  cas caché J={bj}, N={bn}, {e} infirmières -> conflit minimal : "
          + ", ".join(f"{n} × {t}" for t, n in types.items()))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.5), width_ratios=[1.1, 1])
a1.imshow(classe, cmap=ListedColormap(["#2a6f97", "#c8553d", "#7b2cbf"]), vmin=0, vmax=2, aspect="auto")
for (r, c), v in np.ndenumerate(classe):
    a1.text(c, r, ["faisable", "manque", "règles"][int(v)], ha="center", va="center", color="white", fontsize=8)
a1.set_xticks(range(len(EFFECTIFS)))
a1.set_xticklabels(EFFECTIFS)
a1.set_yticks(range(len(BESOINS)))
a1.set_yticklabels([f"J={bj}, N={bn}" for bj, bn in BESOINS])
a1.set(xlabel="nombre d'infirmières", ylabel="besoin par jour",
       title="Faisabilité (bleu) ; infaisable par manque de personnel (rouge)\nou par interaction des règles (violet)")

x = np.arange(len(BESOINS))
a2.bar(x - 0.2, mini_comptage, 0.4, color="#9aa5b1", label="d'après le simple comptage")
a2.bar(x + 0.2, mini_solveur, 0.4, color="#2a6f97", label="d'après le solveur (vrai minimum)")
for k, (a, b) in enumerate(zip(mini_comptage, mini_solveur)):
    if b > a:
        a2.annotate(f"+{b - a}", (k + 0.2, b + 0.1), ha="center", color="#7b2cbf", fontweight="bold")
        bj, bn = BESOINS[k]
        a2.annotate(f"J={bj}, N={bn} : chaque jour {bj} de jour + {bn} de nuit\n+ {bn} au repos après la nuit"
                    f" = {bj + 2 * bn} agents,\nle comptage n'en voit que {a}",
                    (k + 0.2, b), xytext=(k - 3.6, 9.4), fontsize=9, color="#7b2cbf",
                    arrowprops=dict(arrowstyle="->", color="#7b2cbf"))
a2.set_xticks(x)
a2.set_xticklabels([f"J={bj}\nN={bn}" for bj, bn in BESOINS])
a2.set(ylabel="effectif minimal", ylim=(0, 11.5),
       title="Effectif minimal : le comptage sous-estime quand les règles interagissent")
a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
for a in (a1, a2):
    a.spines[["top", "right"]].set_visible(False)
fig.suptitle("Étude structurelle : le manque de personnel n'explique pas tout", fontweight="bold")
fig.tight_layout()
fig.savefig("figures/3_etude_structurelle.png", dpi=150)
print("figures/3_etude_structurelle.png")
