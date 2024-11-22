from gurobipy import *

nbcont=1
nbvar=10

lignes = range(nbcont)
colonnes = range(nbvar)

# Matrice des contraintes
a = [[60, 10, 15, 20, 25, 20, 5, 15, 20, 60]]

# Second membre
b = [100]

# Coefficients de la fonction objectif
c = [70, 18, 16, 14, 12, 10, 8, 6, 4, 2]

m = Model("mogplex")     
        
# declaration variables de decision
x = []
for i in colonnes:
	x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="x%d" % (i+1)))

# maj du modele pour integrer les nouvelles variables
m.update()

obj = LinExpr();
obj =0
for j in colonnes:
    obj += c[j] * x[j]
        
# definition de l'objectif
m.setObjective(obj,GRB.MAXIMIZE)

# Definition des contraintes
for i in lignes:
    m.addConstr(quicksum(a[i][j]*x[j] for j in colonnes) <= b[i], "Contrainte%d" % i)

# Resolution
m.optimize()


print("")                
print('Solution optimale:')
for j in colonnes:
    print('x%d'%(j+1), '=', x[j].x) 
print("")
print('Valeur de la fonction objectif :', m.objVal)
