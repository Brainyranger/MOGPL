import matplotlib.pyplot as plt
from gurobipy import *
import random
import time

# Fonction pour générer une instance aléatoire
def creer_instance(n, p):
    couts = [random.randint(1, 100) for _ in range(n)]
    utilites = [[random.randint(1, 100) for _ in range(n)] for _ in range(p)]
    budget = sum(couts) / 2
    return couts, utilites, budget

# Fonction pour résoudre Max OWA
def maxOWA(n, p, couts, utilites, budget):
    try:
        m = Model("maxOWA")
        
        # Variables
        x = m.addVars(n, vtype=GRB.BINARY, name="x")  # Variables de sélection des projets
        y = m.addVars(p, vtype=GRB.CONTINUOUS, name="y")  # Variables pour OWA
        
        # Objectif : Max OWA
        m.setObjective(y.sum(), GRB.MAXIMIZE)
        
        # Contraintes
        # Budget
        m.addConstr(quicksum(couts[i] * x[i] for i in range(n)) <= budget, "Budget")
        
        # Calcul des utilités pondérées pour OWA
        for j in range(p):
            m.addConstr(y[j] <= quicksum(utilites[j][i] * x[i] for i in range(n)), f"Util_{j}")
        
        m.optimize()
        if m.status == GRB.OPTIMAL:
            return m.objVal
        else:
            return None
    except Exception as e:
        print(f"Erreur dans Max OWA: {e}")
        return None

# Fonction pour résoudre Min OWA des regrets
def minOWA(n, p, couts, utilites, budget):
    try:
        m = Model("minOWA")
        
        # Variables
        x = m.addVars(n, vtype=GRB.BINARY, name="x")  # Variables de sélection des projets
        y = m.addVars(p, vtype=GRB.CONTINUOUS, name="y")  # Variables pour OWA
        
        # Objectif : Min OWA
        m.setObjective(y.sum(), GRB.MINIMIZE)
        
        # Contraintes
        # Budget
        m.addConstr(quicksum(couts[i] * x[i] for i in range(n)) <= budget, "Budget")
        
        # Calcul des utilités pondérées pour OWA
        for j in range(p):
            m.addConstr(y[j] >= quicksum(utilites[j][i] * x[i] for i in range(n)), f"Regret_{j}")
        
        m.optimize()
        if m.status == GRB.OPTIMAL:
            return m.objVal
        else:
            return None
    except Exception as e:
        print(f"Erreur dans Min OWA: {e}")
        return None

# Fonction pour calculer le temps moyen de résolution
def temps_moyen(nb_instances, n, p, methode):
    temps = []
    for _ in range(nb_instances):
        c, u, b = creer_instance(n, p)
        debut = time.time()
        if methode == 'max':
            maxOWA(n, p, c, u, b)
        elif methode == 'min':
            minOWA(n, p, c, u, b)
        fin = time.time()
        temps.append(fin - debut)
    return sum(temps) / nb_instances

# Calcul des temps moyens pour Max OWA et Min OWA des regrets
n_values = [5, 10, 15]
p_values = [10, 15, 20]

temps_maxowa = []
temps_minowa_regret = []

for n in n_values:
    for p in p_values:
        temps_maxowa.append(temps_moyen(10, n, p, 'max'))
        temps_minowa_regret.append(temps_moyen(10, n, p, 'min'))

# Création des grilles pour n et p
n_grid = [n for n in n_values for _ in p_values]
p_grid = p_values * len(n_values)

# Création des graphiques
fig, ax = plt.subplots(1, 2, figsize=(14, 7))

# Graphique pour Max OWA
scatter_maxowa = ax[0].scatter(n_grid, p_grid, c=temps_maxowa, cmap='viridis', s=100)
ax[0].set_title('Temps moyen Max OWA', fontsize=16)
ax[0].set_xlabel('n (Scénarios)', fontsize=14)
ax[0].set_ylabel('p (Projets)', fontsize=14)

# Graphique pour Min OWA des regrets
scatter_minowa = ax[1].scatter(n_grid, p_grid, c=temps_minowa_regret, cmap='viridis', s=100)
ax[1].set_title('Temps moyen Min OWA des regrets', fontsize=16)
ax[1].set_xlabel('n (Scénarios)', fontsize=14)
ax[1].set_ylabel('p (Projets)', fontsize=14)

# Affichage de la barre de couleur
fig.colorbar(scatter_maxowa, ax=ax[0], label='Temps (secondes)')
fig.colorbar(scatter_minowa, ax=ax[1], label='Temps (secondes)')

# Ajustement de l'affichage
plt.tight_layout()

# Affichage du graphique
plt.show()
