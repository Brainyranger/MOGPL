import matplotlib.pyplot as plt
from gurobipy import *
import random
import time

# Fonction pour générer une instance aléatoire
def creer_instance(n, p):
    couts = [random.randint(1, 100) for i in range(p)]
    utilites = [[random.randint(1, 100) for i in range(p)] for j in range(n)]
    budget = sum(couts) / 2
    return couts, utilites, budget

# Fonction de résolution du problème maxpl
def maxpl(p, couts, utilites, budget):
    nbcont = 1
    nbvar = p
    lignes = range(nbcont)
    colonnes = range(nbvar)

    a = [couts]
    b = [budget]
    c = utilites

    m = Model("mogplex")
    x = [m.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i + 1)) for i in colonnes]
    m.update()

    obj = LinExpr()
    for j in colonnes:
        obj += c[j] * x[j]

    m.setObjective(obj, GRB.MAXIMIZE)
    
    for i in lignes:
        m.addConstr(quicksum(a[i][j] * x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

    m.optimize()
    return m.objVal

# Fonction pour résoudre le problème maxmin
def maxmin(n, p, couts, utilites, budget):
    nbcont = n + 1
    nbvar = p + 1
    lignes = range(nbcont)
    colonnes = range(nbvar)

    a = []
    b = []

    for i in range(n):
        contrainte_util = [1]
        for j in range(p):
            contrainte_util.append(-utilites[i][j])
        a.append(contrainte_util)
        b.append(0)

    contrainte_cout = [0] + couts
    a.append(contrainte_cout)
    b.append(budget)

    c = [1] + [0] * p

    m = Model("mogplex")
    x = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="a")]
    x.extend([m.addVar(vtype=GRB.BINARY, lb=0, name="p%d" % (i + 1)) for i in range(1, nbvar)])
    
    m.update()
    obj = LinExpr()
    for j in colonnes:
        obj += c[j] * x[j]
    
    m.setObjective(obj, GRB.MAXIMIZE)
    
    for i in lignes:
        m.addConstr(quicksum(a[i][j] * x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

    m.optimize()
    return m.objVal

# Fonction pour résoudre le problème minmax_regret
def minmax_regret(n, p, couts, utilites, budget):
    opt_scenar = [maxpl(p, couts, utilites[i], budget) for i in range(n)]
    nbcont = n + 1
    nbvar = p + 1
    lignes = range(nbcont)
    colonnes = range(nbvar)

    a = []
    for i in range(n):
        contrainte_util = [1] + [utilites[i][j] for j in range(p)]
        a.append(contrainte_util)

    contrainte_cout = [0] + [-couts[i] for i in range(p)]
    a.append(contrainte_cout)

    b = opt_scenar + [-budget]

    c = [1] + [0] * p

    m = Model("mogplex")
    x = [m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="a")]
    x.extend([m.addVar(vtype=GRB.BINARY, lb=0, name="p%d" % (i + 1)) for i in range(1, nbvar)])

    m.update()
    obj = LinExpr()
    for j in colonnes:
        obj += c[j] * x[j]
    
    m.setObjective(obj, GRB.MINIMIZE)
    
    for i in lignes:
        m.addConstr(quicksum(a[i][j] * x[j] for j in colonnes) >= b[i], "Contrainte%d" % i)

    m.optimize()
    return m.objVal

# Fonction pour calculer le temps moyen de résolution
def temps_moyen(nb_instances, n, p):
    temps_maxmin = []
    temps_minmax_regret = []
    for i in range(nb_instances):
        c, u, b = creer_instance(n, p)
        debut = time.time()
        maxmin(n, p, c, u, b)
        fin = time.time()
        temps_maxmin.append(fin - debut)

        debut = time.time()
        minmax_regret(n, p, c, u, b)
        fin = time.time()
        temps_minmax_regret.append(fin - debut)

    return sum(temps_maxmin) / nb_instances, sum(temps_minmax_regret) / nb_instances

# Calcul des temps pour chaque combinaison de n et p
temps_exec = []
for k in [5, 10, 15]:
    for l in [10, 15, 20]:
        temps_exec.append(temps_moyen(10, k, l))

# Résultats pour l'affichage graphique
temps_maxmin = [temps_exec[i][0] for i in range(len(temps_exec))]
temps_minmax_regret = [temps_exec[i][1] for i in range(len(temps_exec))]

# Création du graphique
n_values = [5, 10, 15]
p_values = [10, 15, 20]
n_grid, p_grid = zip(*[(n, p) for n in n_values for p in p_values])

# Affichage du temps moyen de résolution pour maxmin et minmax_regret
fig, ax = plt.subplots(1, 2, figsize=(14, 7))

# Graphique pour MaxMin
ax[0].scatter(n_grid, p_grid, c=temps_maxmin, cmap='viridis', s=100)
ax[0].set_title('Temps moyen MaxMin', fontsize=16)
ax[0].set_xlabel('n (Scénarios)', fontsize=14)
ax[0].set_ylabel('p (Projets)', fontsize=14)

# Graphique pour MinMax Regret
ax[1].scatter(n_grid, p_grid, c=temps_minmax_regret, cmap='viridis', s=100)
ax[1].set_title('Temps moyen MinMax Regret', fontsize=16)
ax[1].set_xlabel('n (Scénarios)', fontsize=14)
ax[1].set_ylabel('p (Projets)', fontsize=14)

# Affichage
plt.colorbar(ax[0].collections[0], ax=ax[0], label='Temps (secondes)')
plt.colorbar(ax[1].collections[0], ax=ax[1], label='Temps (secondes)')
plt.tight_layout()
plt.show()
