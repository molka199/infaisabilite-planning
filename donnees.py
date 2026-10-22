"""Petit service fictif : 6 infirmières, 1 semaine, 2 postes (Jour, Nuit).

Trois scénarios construits pour illustrer le sujet :
  S1 : situation normale -> planning faisable
  S2 : quatre congés le même mercredi -> manque de ressources
  S3 : renfort de nuit + règle « 2 nuits max » -> règles trop restrictives
"""
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]
POSTES = ["J", "N"]
INFIRMIERES = ["Amira", "Basma", "Chaima", "Dorra", "Emna", "Farah"]

BASE = {
    "besoin": {"J": 2, "N": 1},   # agents requis chaque jour par poste
    "max_jours": 5,               # contrat : jours travaillés max par semaine
    "max_nuits": 2,               # règle : nuits max par semaine
    "conges": {},                 # infirmière -> jours de congé
    "besoin_special": {},         # (jour, poste) -> besoin modifié
}


def scenario(nom):
    s = dict(BASE, nom=nom, conges={}, besoin_special={})
    if nom == "S2_conges":
        s["conges"] = {i: ["mer"] for i in INFIRMIERES[:4]}
    if nom == "S3_regles":
        s["besoin_special"] = {(j, "N"): 2 for j in JOURS}
    return s


SCENARIOS = ["S1_normal", "S2_conges", "S3_regles"]


def besoin(s, jour, poste):
    return s["besoin_special"].get((jour, poste), s["besoin"][poste])
