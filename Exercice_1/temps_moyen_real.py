n = 5
p = 10

from gurobipy import *
import random
import time

def creer_instance(n, p) :

	couts = [random.randint(1, 100) for i in range(p)]
	utilites = [[random.randint(1, 100) for i in range(p)] for j in range(n)]
	budget = sum(couts)/2
	return couts, utilites, budget
	
def maxpl(p, couts, utilites, budget) :

	nbcont=1
	nbvar=p

	lignes = range(nbcont)
	colonnes = range(nbvar)

	a = [couts]

	b = [budget]

	c = utilites

	m = Model("mogplex")     

	x = []
	for i in colonnes:
		x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i+1)))

	m.update()

	obj = LinExpr();
	obj =0
	for j in colonnes:
		obj += c[j] * x[j]

	m.setObjective(obj,GRB.MAXIMIZE)

	for i in lignes:
		m.addConstr(quicksum(a[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

	m.optimize()
	return m.objVal

def maxmin(n, p, couts, utilites, budget) :

	nbcont=n+1
	nbvar=p+1

	lignes = range(nbcont)
	colonnes = range(nbvar)
	
	a = []
	b = []
	
	for i in range(n) :
		contrainte_util = [1]
		for j in range(p) :
			contrainte_util.append(-utilites[i][j])
		a.append(contrainte_util)
		b.append(0)
	
	contrainte_cout = [0]
	for i in range(p) :
		contrainte_cout.append(couts[i])
	a.append(contrainte_cout)
	b.append(budget)

	c = [1] + [0]*p

	m = Model("mogplex")    
		
	x = []
	x.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="a"))
	for i in range(1, nbvar):	
		x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="p%d" % (i+1)))

	m.update()

	obj = LinExpr();
	obj =0
	for j in colonnes:
	    obj += c[j] * x[j]
		
	m.setObjective(obj,GRB.MAXIMIZE)

	for i in lignes:
	    m.addConstr(quicksum(a[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

	m.optimize()
	
	return m.objVal
	
def minmax_regret(n, p, couts, utilites, budget) :

	#Solution optimale pour chaque scénario
	opt_scenar = []
	for i in range(n) :
		opt_scenar.append(maxpl(p, couts, utilites[i], budget))
	
	print(opt_scenar)
	
	nbcont=n+1
	nbvar=p+1

	lignes = range(nbcont)
	colonnes = range(nbvar)
	
	a = []
	
	for i in range(n) :
		contrainte_util = [1]
		for j in range(p) :
			contrainte_util.append(utilites[i][j])
		a.append(contrainte_util)
	
	contrainte_cout = [0]
	for i in range(p) :
		contrainte_cout.append(-couts[i])
	a.append(contrainte_cout)
	
	b = opt_scenar
	b.append(-budget)

	c = [1] + [0]*p
	
	m = Model("mogplex")    
		
	x = []
	x.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="a"))
	for i in range(1, nbvar):	
		x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="p%d" % (i+1)))

	m.update()

	obj = LinExpr();
	obj =0
	for j in colonnes:
	    obj += c[j] * x[j]
		
	m.setObjective(obj,GRB.MINIMIZE)

	for i in lignes:
	    m.addConstr(quicksum(a[i][j]*x[j] for j in colonnes) >= b[i], "Contrainte%d" % i)

	m.optimize()

	return m.objVal
	
	
def temps_moyen(nb_instances, n, p) :
	temps_maxmin = []
	temps_minmax_regret = []
	for i in range(nb_instances) :
	
		c, u, b = creer_instance(n, p)
		
		debut = time.time()
		maxmin(n, p, c, u, b)
		fin = time.time()
		temps_maxmin.append(fin-debut)
		
		debut = time.time()
		minmax_regret(n, p, c, u, b)
		fin = time.time()
		temps_minmax_regret.append(fin-debut)
		
	return sum(temps_maxmin)/nb_instances, sum(temps_minmax_regret)/nb_instances
		
		

temps_exec = []
for k in [5, 10, 15] :
	for l in [10, 15, 20] :
		temps_exec.append(temps_moyen(10, k, l))
		
print(temps_exec)

	
#c, u, b = creer_instance(5, 10)
#maxmin(5, 10, c, u, b)
#minmax_regret(5, 10, c, u, b)

