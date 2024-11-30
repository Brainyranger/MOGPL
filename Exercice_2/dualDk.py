from gurobipy import *

# Données du problème
n = 6  # nombre de variables (taille du vecteur z)
z = [2, 9, 6, 8, 5, 4]  # valeurs du vecteur z
k = 3  # valeur donnée pour k (vous pouvez ajuster cette valeur)

# Initialisation du modèle
m = Model("Dual_Dk")

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

# Affichage des résultats
print(f"Solution optimale:")
print(f"r_k = {r.x}")  # Valeur de la variable duale r_k
for i in range(n):
    print(f"b_{i} = {b[i].x}")  # Valeurs des variables duales b_i

# Calcul de la valeur de L_k(z)
L_k_z = k * r.x - sum(b[i].x for i in range(n))
print(f"\nComposantes du vecteur L_k(z) :")
print(f"L_k(z) = {L_k_z}")
