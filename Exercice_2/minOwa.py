from gurobipy import *
# Données de l'exemple 1
projets = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
couts = [60, 10, 15, 25, 20, 20, 40, 10, 30, 60]
utilite_s1 = [70, 18, 16, 14, 12, 18, 12, 16, 14, 8]
utilite_s2 = [2, 4, 6, 8, 4, 6, 14, 16, 18, 10]

# Paramètres du modèle
budget_max = 100  # Budget total
n = len(projets)  # Nombre de projets

# Création du modèle Gurobi
model = Model("MinOWA_Des_Regrets")

# Variables de décision
x = model.addVars(projets, vtype=GRB.BINARY, name="Selection")  # 1 si le projet est sélectionné, 0 sinon
r = model.addVars(projets, lb=0, name="Regret")  # Regrets pour chaque projet

# Fonction objectif : minimiser la somme des regrets
model.setObjective(quicksum(r[i] for i in projets), GRB.MINIMIZE)

# Contraintes : respecter le budget
model.addConstr(quicksum(x[i] * couts[i - 1] for i in projets) <= budget_max, "Budget")

# Calcul des regrets pour chaque projet
for i in projets:
    model.addConstr(r[i] >= max(utilite_s1[i - 1], utilite_s2[i - 1]) - (x[i] * max(utilite_s1[i - 1], utilite_s2[i - 1])), f"Regret_{i}")

# Résolution du problème
model.optimize()

# Affichage des résultats
if model.status == GRB.OPTIMAL:
    print(f"Statut de la solution: {model.status}")
    print("Projets sélectionnés:")
    for i in projets:
        if x[i].x > 0.5:  # Si le projet est sélectionné (valeur binaire > 0.5)
            print(f"Projet {i} avec un regret de {r[i].x}")

    print(f"Valeur optimale des regrets: {model.objVal}")
else:
    print("Aucune solution optimale trouvée.")