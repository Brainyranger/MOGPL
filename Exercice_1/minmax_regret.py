from gurobipy import *

# Nombre de contraintes et variables
nbcont = 3
nbvar = 11

lignes = range(nbcont)
colonnes = range(nbvar)

# Matrice des contraintes
a = [[1, 70, 18, 16, 14, 12, 10, 8, 6, 4, 2],
     [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 70],
     [0, -60, -10, -15, -20, -25, -20, -5, -15, -20, -60]]

# Second membre
b = [112, 118, -100]

# Coefficients de la fonction objectif
c = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Fonction pour résoudre le problème de maximisation d'un critère
def max_criterion(utilites):
    m = Model("maximize_criterion")
    x = []
    x.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="a"))
    for i in range(1, 11):
        x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="p%d" % (i + 1)))
    m.update()

    # Fonction objectif (maximisation d'un critère)
    obj = LinExpr()
    for j in range(len(utilites)):
        obj += utilites[j] * x[j + 1]  # on commence à partir de p1, p2, etc.
    
    m.setObjective(obj, GRB.MAXIMIZE)

    # Contraintes
    for i in range(nbcont):
        m.addConstr(quicksum(a[i][j] * x[j] for j in range(nbvar)) <= b[i], "Contrainte%d" % i)

    # Résolution
    m.optimize()

    # Retourne la solution optimale et la valeur du critère
    solution = [x[j].x for j in range(nbvar)]
    crit_value = m.objVal
    return solution, crit_value

# Définir les utilités des scénarios
utilites_s1 = [70, 18, 16, 14, 12, 10, 8, 6, 4, 2]  # Utilités dans le scénario 1
utilites_s2 = [2, 4, 6, 8, 10, 12, 14, 16, 18, 70]  # Utilités dans le scénario 2

# Résolution pour maximiser z1(x)
x1_star, z1_star = max_criterion(utilites_s1)
print("Solution optimale pour maximiser z1(x):", x1_star)
print("Valeur de z1(x*) =", z1_star)

# Résolution pour maximiser z2(x)
x2_star, z2_star = max_criterion(utilites_s2)
print("Solution optimale pour maximiser z2(x):", x2_star)
print("Valeur de z2(x*) =", z2_star)

# Maintenant, vous avez les solutions x1* et x2* ainsi que les valeurs de leurs critères.
# Vous pouvez procéder à la minimisation du regret maxmin en utilisant ces résultats.

# Formuler le problème de regret maxmin
m_regret = Model("minmax_regret")

# Variables de décision pour les regrets (une pour chaque critère)
regrets = [m_regret.addVar(vtype=GRB.CONTINUOUS, name=f"regret{i}") for i in range(2)]  # 2 regrets, un pour chaque critère

# Introduire une variable pour le maximum des regrets
regret_max = m_regret.addVar(vtype=GRB.CONTINUOUS, name="regret_max")

# Contraintes de regret
for i in range(10):  # Nous avons 10 variables binaires
    # Calcul des regrets pour chaque critère
    regret_expr1 = z1_star - x1_star[i + 1]  # Calcul du regret pour z1
    regret_expr2 = z2_star - x2_star[i + 1]  # Calcul du regret pour z2

    # Contrainte pour les regrets
    m_regret.addConstr(regrets[0] >= regret_expr1)  # Contrainte pour z1
    m_regret.addConstr(regrets[1] >= regret_expr2)  # Contrainte pour z2

    # Contrainte sur le maximum des regrets
    m_regret.addConstr(regret_max >= regrets[0])  # regret_max doit être supérieur ou égal à regret1
    m_regret.addConstr(regret_max >= regrets[1])  # regret_max doit être supérieur ou égal à regret2

# Fonction objectif : minimiser le maximum des regrets
m_regret.setObjective(regret_max, GRB.MINIMIZE)

# Résolution du modèle maxmin regret
m_regret.optimize()
print("\nRésolution du problème de regret maxmin.")

# Afficher les regrets et la solution optimale
for regret in regrets:
    print(f"Regret : {regret.x}")

print(f"Valeur du regret maxmin : {regret_max.x}")
