import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
import numpy as np


# Définir les nœuds pour chaque scénario du graphe
noeuds_gauche = ['a', 'b', 'c', 'd', 'e', 'f']  # Pour le graphe de gauche (scénarios 1 et 2)
arcs_scenario1_gauche = {
    ('a', 'b'): 4, ('a', 'c'): 5,
    ('b', 'c'): 2, ('b', 'e'): 2,('b', 'f'): 7,('b', 'd'): 1,
    ('c', 'd'): 5, ('c', 'e'): 2,
    ('d', 'f'): 3,
    ('e', 'f'): 5
}
arcs_scenario2_gauche = {
    ('a', 'b'): 3, ('a', 'c'): 1, 
    ('b', 'd'): 4, ('b', 'f'): 5,('b', 'e'): 2, ('b', 'c'): 1,
    ('c', 'd'): 1, ('c', 'e'): 7,
    ('d', 'f'): 2,
    ('e', 'f'): 2
}

# Définir les nœuds pour le graphe de droite
noeuds_droite = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

# Définir les arcs et les coûts pour chaque scénario du graphe de droite
arcs_scenario1_droite = {
    ('a', 'b'): 5, ('a', 'c'): 10, ('a', 'd'): 2,
    ('b', 'c'): 4, ('b', 'e'): 4,('b', 'd'): 1,
    ('d', 'c'): 1, ('d', 'f'): 3,
    ('c', 'e'): 3, ('c', 'f'): 1, 
    ('e', 'g'): 1,
    ('f', 'g'): 1
}
arcs_scenario2_droite = {
    ('a', 'b'): 3, ('a', 'c'): 4, ('a', 'd'): 6,
    ('b', 'c'): 2, ('b', 'e'): 6,('b', 'd'): 3,
    ('d', 'c'): 4, ('d', 'f'): 5,
    ('c', 'e'): 1, ('c', 'f'): 2,
    ('e', 'g'): 1,
    ('f', 'g'): 1
}

# Fonction de base pour ajouter les contraintes de flux
def add_flow_constraints(model, x, arcs, source, destination):
    nodes = set(u for u, v in arcs).union(v for u, v in arcs)
    for node in nodes:
        if node == source:
            model.addConstr(
                gp.quicksum(x[u, v] for u, v in arcs if u == node) - 
                gp.quicksum(x[u, v] for u, v in arcs if v == node) == 1,
                name=f"flow_source_{node}")
        elif node == destination:
            model.addConstr(
                gp.quicksum(x[u, v] for u, v in arcs if u == node) - 
                gp.quicksum(x[u, v] for u, v in arcs if v == node) == -1,
                name=f"flow_dest_{node}")
        else:
            model.addConstr(
                gp.quicksum(x[u, v] for u, v in arcs if u == node) - 
                gp.quicksum(x[u, v] for u, v in arcs if v == node) == 0,
                name=f"flow_{node}")


# 1. MaxMin
def solve_maxmin(arcs, scenarios, source, cible):
    model = gp.Model("MaxMin")
    x = model.addVars(arcs.keys(), vtype=GRB.BINARY, name="x")
    z = model.addVar(vtype=GRB.CONTINUOUS, name="z")

    # Contraintes de flux
    add_flow_constraints(model, x, arcs, source, cible)

    # MaxMin : Maximiser le plus petit coût
    for s in range(len(scenarios)):
            model.addConstr(
                z <= gp.quicksum(
                    (scenarios[s].get((u, v), float('inf')) * x[u, v]) if (u, v) in scenarios[s] else 0
                    for u, v in arcs.keys()
                ),
                name=f"scenario_{s}"
            )

    # Objectif : Maximiser z (le plus petit coût)
    model.setObjective(z, GRB.MAXIMIZE)

    # Optimisation
    model.optimize()

    # Vérification des résultats
    if model.status == GRB.OPTIMAL:
        return [arc for arc in arcs.keys() if x[arc].X > 0.5], model.ObjVal
    return None, None


# 2. MinMax Regret
def solve_minmax_regret(arcs, scenarios, source, cible):
    model = gp.Model("MinMaxRegret")
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
    r = model.addVar(vtype=GRB.CONTINUOUS, name="r")

    # Contraintes de flux
    add_flow_constraints(model, x, arcs, source, cible)

    # MinMax Regret : Minimiser le regret maximum
    model.optimize()

    if model.status == GRB.OPTIMAL:
        # Calculer le coût optimal pour chaque scénario après optimisation
        optimal_s = []
        for s in range(len(scenarios)):
            scenario_cost = sum(scenarios[s].get((u, v), float('inf')) * x[u, v].X for u, v in arcs if (u, v) in scenarios[s])
            optimal_s.append(scenario_cost)

        # Calculer le regret pour chaque scénario
        for s in range(len(scenarios)):
            regret_cost = sum(scenarios[s].get((u, v), float('inf')) * x[u, v].X for u, v in arcs if (u, v) in scenarios[s]) - optimal_s[s]
            model.addConstr(r >= regret_cost, name=f"regret_scenario_{s}")

        # Définir l'objectif : Minimiser le regret maximal
        model.setObjective(r, GRB.MINIMIZE)
        model.optimize()

        # Vérification des résultats
        if model.status == GRB.OPTIMAL:
            return [arc for arc in arcs if x[arc].X > 0.5], model.ObjVal
    
    return None, None


scenarios_gauche = [arcs_scenario1_gauche, arcs_scenario2_droite]
scenarios_droite = [arcs_scenario1_droite, arcs_scenario2_droite]

print("\n=== TEST MaxMin ===")
for i, scenario in enumerate(scenarios_gauche):
    print(f"Graph gauche, scénario {i+1}")
    solution, value = solve_maxmin(arcs_scenario1_gauche, scenarios=scenarios_gauche, source='a', cible='f')
    print(f"Solution : {solution}, Valeur : {value}")

# Test pour les graphes droite
for i, scenario in enumerate(scenarios_droite):
    print(f"Graph droite, scénario {i+1}")
    solution, value = solve_maxmin(arcs_scenario1_droite, scenarios=scenarios_droite, source='a', cible='g')
    print(f"Solution : {solution}, Valeur : {value}")



print("\n=== TEST MinMaxRegret ===")
# Test pour les graphes gauche
for i, scenario in enumerate(scenarios_gauche):
    print(f"Graph gauche, scénario {i+1}")
    solution, value = solve_minmax_regret(arcs_scenario1_gauche, scenarios=scenarios_gauche, source='a', cible='f')
    print(f"Solution : {solution}, Valeur : {value}")

# Test pour les graphes droite
for i, scenario in enumerate(scenarios_droite):
    print(f"Graph droite, scénario {i+1}")
    solution, value = solve_minmax_regret(arcs_scenario1_droite, scenarios=scenarios_droite, source='a', cible='g')
    print(f"Solution : {solution}, Valeur : {value}")

# Collecte des résultats
results_maxmin_gauche = []
results_maxmin_droite = []
results_minmax_regret_gauche = []
results_minmax_regret_droite = []

# Calcul des valeurs pour MaxMin
for scenario in scenarios_gauche:
    _, value = solve_maxmin(arcs_scenario1_gauche, scenarios=scenarios_gauche, source='a', cible='f')
    results_maxmin_gauche.append(value)

for scenario in scenarios_droite:
    _, value = solve_maxmin(arcs_scenario1_droite, scenarios=scenarios_droite, source='a', cible='g')
    results_maxmin_droite.append(value)

# Calcul des valeurs pour MinMaxRegret
for scenario in scenarios_gauche:
    _, value = solve_minmax_regret(arcs_scenario1_gauche, scenarios=scenarios_gauche, source='a', cible='f')
    results_minmax_regret_gauche.append(value)

for scenario in scenarios_droite:
    _, value = solve_minmax_regret(arcs_scenario1_droite, scenarios=scenarios_droite, source='a', cible='g')
    results_minmax_regret_droite.append(value)

# Nombre de scénarios
n_scenarios_gauche = len(results_maxmin_gauche)
n_scenarios_droite = len(results_maxmin_droite)

# Création de la figure avec 2 sous-graphiques
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

# MaxMin - Diagramme en barres
x = np.arange(n_scenarios_gauche)  # Position des barres pour le graphe gauche

width = 0.35  # Largeur des barres

# Barres pour le graphique gauche et droit
ax1.bar(x - width/2, results_maxmin_gauche, width, label="Graph Gauche (MaxMin)", color='skyblue')
ax1.bar(x + width/2, results_maxmin_droite, width, label="Graph Droite (MaxMin)", color='orange')


ax1.set_title("Résultats MaxMin")
ax1.set_xlabel("Scénarios")
ax1.set_ylabel("Valeurs")
ax1.set_xticks(x)
ax1.set_xticklabels([f"Scénario {i+1}" for i in range(n_scenarios_gauche)])
ax1.legend()
ax1.grid(True)

# MinMaxRegret - Diagramme en barres
x = np.arange(n_scenarios_gauche)  # Position des barres pour le graphe gauche

# Barres pour le graphique gauche et droit
ax2.bar(x - width/2, results_minmax_regret_gauche, width, label="Graph Gauche (MinMaxRegret)", color='skyblue')
ax2.bar(x + width/2, results_minmax_regret_droite, width, label="Graph Droite (MinMaxRegret)", color='orange')

ax2.set_title("Résultats MinMaxRegret")
ax2.set_xlabel("Scénarios")
ax2.set_ylabel("Valeurs")
ax2.set_xticks(x)
ax2.set_xticklabels([f"Scénario {i+1}" for i in range(n_scenarios_gauche)])
ax2.legend()
ax2.grid(True)

# Affichage
plt.tight_layout()
plt.savefig("maxmin_minmaxregret_comparison_bar_chart.png")
plt.show()