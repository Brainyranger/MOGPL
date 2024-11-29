import matplotlib.pyplot as plt
from gurobipy import *
import random
import time

# Fonction pour générer une instance aléatoire
def creer_instance(n, p):
    couts = [random.randint(1, 100) for i in range(n)]
    utilites = [[random.randint(1, 100) for i in range(n)] for j in range(p)]
    budget = sum(couts) / 2
    return couts, utilites, budget
    
    
# Fonction pour résoudre le problème maxmin (n = nb de projets ; p = nb de scénarios)
def maxOWA(n, p, couts, utilites, budget):
	nbcont = p**2+1 
	nbvar = p**2 + p + n
	lignes = range(nbcont)
	colonnes = range(nbvar)
    
	a = []
	b = []

	for l in range(p) :
		for i in range(p):
			contrainte_util = [0]*p
			contrainte_util[i] = 1
			for j in range(p**2):
				contrainte_util.append(0)
			contrainte_util[p+i+l] = -1
			for j in range(n) :
				contrainte_util.append(-utilites[i][j])
			a.append(contrainte_util)
			b.append(0)

	contrainte_cout = ([0]*((p**2)+p)) + couts
	a.append(contrainte_cout)
	b.append(budget)	
    
	c = [i for i in range(p)]
	c = c + [-1 for i in range(p**2)]
	c = c + [0] * n
	print(n)
	print(p)
	print(c)

	m = Model("mogplex")
	x = []
	for i in range(p**2 + p) :
		x.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x%d" % (i+1)))
	for i in range(p**2 + p, p**2 + p + n) :
		x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i+1)))
    
	m.update()
	obj = LinExpr()
	for j in colonnes:
		obj += c[j] * x[j]
    
	m.setObjective(obj, GRB.MAXIMIZE)
    
	for i in lignes:
		m.addConstr(quicksum(a[i][j] * x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

	m.optimize()
	return m.objVal

# Fonction pour calculer le temps moyen de résolution
def temps_moyen(nb_instances, n, p):
    temps_maxOWA = []
    for i in range(nb_instances):
        c, u, b = creer_instance(n, p)
        debut = time.time()
        maxOWA(n, p, c, u, b)
        fin = time.time()
        temps_maxOWA.append(fin - debut)

    return sum(temps_maxOWA) / nb_instances

# Calcul des temps pour chaque combinaison de n et p
temps_exec = []
for k in [5, 10, 15]:
    for l in [10, 15, 20]:
        temps_exec.append(temps_moyen(10, k, l))

# Résultats pour l'affichage graphique
temps_maxOWA = [temps_exec[i] for i in range(len(temps_exec))]
print(temps_exec)


