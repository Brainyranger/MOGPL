#Résolution du problème MAXMIN

from gurobipy import *

nbcont=6
nbvar=7

lignes = range(nbcont)
colonnes = range(nbvar)

# Matrice des contraintes
a = [[1, -1, 0, 0, 0, 0, 0],
     [1, 0, -1, 0, 0, 0, 0],
     [1, 0, 0, -1, 0, 0, 0],
     [1, 0, 0, 0, -1, 0, 0],
     [1, 0, 0, 0, 0, -1, 0],
     [1, 0, 0, 0, 0, 0, -1]]

# Second membre
b = [2, 9, 6, 8, 5, 4]

# Coefficients de la fonction objectif (1ère valeur = k)
c = [6, -1, -1, -1, -1, -1, -1]

m = Model("mogplex")     
        
# declaration variables de decision
x = []
for i in colonnes:
	x.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p%d" % (i+1)))

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
