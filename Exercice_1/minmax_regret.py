from gurobipy import *

nbcont=3
nbvar=11

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

m = Model("mogplex")     
        
# declaration variables de decision
x = []
x.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="a"))
for i in range(1, 11):
	x.append(m.addVar(vtype=GRB.BINARY, lb=0, name="p%d" % (i+1)))

# maj du modele pour integrer les nouvelles variables
m.update()

obj = LinExpr();
obj =0
for j in colonnes:
    obj += c[j] * x[j]
        
# definition de l'objectif
m.setObjective(obj,GRB.MINIMIZE)

# Definition des contraintes
for i in lignes:
    m.addConstr(quicksum(a[i][j]*x[j] for j in colonnes) >= b[i], "Contrainte%d" % i)

# Resolution
m.optimize()


print("")                
print('Solution optimale:')
for j in colonnes:
    print('x%d'%(j+1), '=', x[j].x) 
print("")
print('Valeur de la fonction objectif :', m.objVal)