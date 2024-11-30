from gurobipy import *

# Données du problème
z = [2, 9, 6, 8, 5, 4]  # valeurs du vecteur z
n = len(z)  # taille du vecteur z

# Résolution du problème dual pour différentes valeurs de k
for k in range(1, n + 1):
    m = Model(f"Dual_Dk_{k}")

    # Variables duales
    r = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="r_k")  # Variable duale associée à la contrainte ∑ aik = k
    b = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"b_{i}") for i in range(n)]  # Variables duales b_i pour chaque i

    # Mise à jour du modèle
    m.update()

    # Fonction objectif du dual : maximiser k * r_k - Σ b_i
    m.setObjective(k * r - quicksum(b[i] for i in range(n)), GRB.MAXIMIZE)

    # Contraintes : r_k - b_i = z_i pour chaque i
    for i in range(n):
        m.addConstr(r - b[i] == z[i], name=f"constraint_{i}")

    # Résolution
    m.optimize()

    # Affichage des résultats pour chaque k
    print(f"Solution optimale pour k={k}:")
    print(f"r_k = {r.x}")
    for i in range(n):
        print(f"b_{i} = {b[i].x}")
    print(f"Valeur optimale des regrets (L_{k}(z)) : {m.objVal}\n")
