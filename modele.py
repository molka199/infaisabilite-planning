"""Modèle PLNE du planning (Gurobi). Chaque contrainte porte le nom de son groupe métier,
par exemple « couverture|mer|N » ou « conges|Amira » : c'est ce qui rend l'explication lisible."""
import gurobipy as gp
from gurobipy import GRB
from donnees import JOURS, POSTES, INFIRMIERES, besoin


def construire(s, actifs=None):
    """Construit le modèle avec les groupes de `actifs` (tous si None). Retourne (modèle, x, groupes)."""
    m = gp.Model(s["nom"])
    m.Params.OutputFlag = 0
    equipe = s.get("equipe", INFIRMIERES)
    x = m.addVars(equipe, JOURS, POSTES, vtype=GRB.BINARY, name="x")
    groupes = []

    def ajouter(groupe, expr, k=0):
        if groupe not in groupes:
            groupes.append(groupe)
        if actifs is None or groupe in actifs:
            m.addConstr(expr, name=f"{groupe}#{k}")

    # structurel : un seul poste par jour (jamais remis en cause)
    for i in equipe:
        for j in JOURS:
            m.addConstr(x.sum(i, j, "*") <= 1, name=f"structurel|{i}|{j}#0")

    for j in JOURS:
        for p in POSTES:
            ajouter(f"couverture|{j}|{p}", x.sum("*", j, p) >= besoin(s, j, p))

    for i in equipe:
        for k, j in enumerate(s["conges"].get(i, [])):
            ajouter(f"conges|{i}", x.sum(i, j, "*") == 0, k)
        for k in range(len(JOURS) - 1):
            ajouter(f"repos|{i}", x[i, JOURS[k], "N"] + x.sum(i, JOURS[k + 1], "*") <= 1, k)
        ajouter(f"max_jours|{i}", x.sum(i, "*", "*") <= s["max_jours"])
        ajouter(f"max_nuits|{i}", x.sum(i, "*", "N") <= s["max_nuits"])

    m.update()
    return m, x, groupes


def faisable(s, actifs):
    m = construire(s, actifs)[0]
    m.optimize()
    return m.Status != GRB.INFEASIBLE


def manque_minimal(s, type_souple="couverture"):
    """feasRelax : plus petit relâchement des contraintes de ce type (les autres restent dures)
    pour rendre le planning faisable. Retourne None si relâcher ce type ne suffit pas."""
    m = construire(s)[0]
    souples = [c for c in m.getConstrs() if c.ConstrName.startswith(type_souple + "|")]
    if not souples:
        return None
    m.feasRelax(0, False, None, None, None, souples, [1.0] * len(souples))
    m.optimize()
    return round(m.ObjVal) if m.Status == GRB.OPTIMAL else None


def filtre_suppression(s):
    """Chinneck & Dravnieks (1991), appliqué aux groupes : on retire chaque groupe à tour de rôle
    et on ne le garde que si sa présence est nécessaire au conflit. Retourne (MUS, appels au solveur)."""
    groupes = construire(s)[2]
    mus = list(groupes)
    for g in groupes:
        essai = [h for h in mus if h != g]
        if not faisable(s, essai):
            mus = essai
    return mus, len(groupes)


def phrase(groupe, s):
    """Traduit un groupe en phrase pour un cadre de santé."""
    t, *cle = groupe.split("|")
    if t == "couverture":
        j, p = cle
        return f"il faut {besoin(s, j, p)} agent(s) en {'Jour' if p == 'J' else 'Nuit'} le {j}"
    i = cle[0]
    if t == "conges":
        return f"{i} est en congé ({', '.join(s['conges'][i])})"
    if t == "repos":
        return f"{i} doit se reposer le lendemain d'une nuit"
    if t == "max_jours":
        return f"{i} travaille au plus {s['max_jours']} jours (contrat)"
    return f"{i} fait au plus {s['max_nuits']} nuits par semaine"
