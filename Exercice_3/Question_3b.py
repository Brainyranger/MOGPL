import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt


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


# 3. MaxOWA
def solve_maxowa(arcs, scenarios, source, cible, weights):
    model = gp.Model("MaxOWA")
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
    
    # Nombre de scénarios
    n_scenarios = len(scenarios)
    
    # Créer les variables z, une pour chaque scénario
    z = model.addVars(n_scenarios, vtype=GRB.CONTINUOUS, name="z")

    # Contraintes de flux
    add_flow_constraints(model, x, arcs, source, cible)

    # MaxOWA : Maximiser la pondération OWA
    for s in range(n_scenarios):
        z_value = gp.quicksum(
            scenarios[s].get((u, v), 10**6) * x[u, v]  # Remplacer 'float('inf')' par un grand nombre
            for u, v in arcs
        )
        
        model.addConstr(z[s] == z_value, name=f"owa_scenario_{s}")
    
    # Objectif : Maximiser la somme pondérée des z avec le même poids pour chaque scénario
    model.setObjective(gp.quicksum(weights * z[i] for i in range(n_scenarios)),
                       GRB.MAXIMIZE)

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return [arc for arc in arcs if x[arc].X > 0.5], model.ObjVal
    return None, None

# 4. MinOWA
def solve_minowa(arcs, scenarios, source, cible, weights):
    model = gp.Model("MinOWA")
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
    
    # Nombre de scénarios
    n_scenarios = len(scenarios)
    
    # Créer les variables z, une pour chaque scénario
    z = model.addVars(n_scenarios, vtype=GRB.CONTINUOUS, name="z")

    # Contraintes de flux
    add_flow_constraints(model, x, arcs, source, cible)

    # MinOWA : Minimiser la pondération OWA
    for s in range(n_scenarios):
        z_value = gp.quicksum(
            scenarios[s].get((u, v), 10**6) * x[u, v]  # Remplacer 'float('inf')' par un grand nombre
            for u, v in arcs
        )
        
        model.addConstr(z[s] == z_value, name=f"owa_scenario_{s}")
    
    # Objectif : Minimiser la somme pondérée des z avec le même poids pour chaque scénario
    model.setObjective(gp.quicksum(weights * z[i] for i in range(n_scenarios)),
                       GRB.MINIMIZE)

    model.optimize()

    if model.status == GRB.OPTIMAL:
        return [arc for arc in arcs if x[arc].X > 0.5], model.ObjVal
    return None, None




scenarios_gauche = [arcs_scenario1_gauche, arcs_scenario2_droite]
scenarios_droite = [arcs_scenario1_droite, arcs_scenario2_droite]


weights_list = [2, 4, 8, 16]


# Stockage des résultats pour les graphes gauche et droite
results_gauche = {"maxowa": [], "minowa": []}
results_droite = {"maxowa": [], "minowa": []}

# Analyse pour chaque poids
for weights in weights_list:
    print(f"\nPoids : {weights}")

    # Calcul pour le graphe gauche
    minowa_gauche_values = []
    for i, scenario in enumerate(scenarios_gauche):
        _, value_minowa = solve_minowa(scenario, scenarios=scenarios_gauche, source='a', cible='f', weights=weights)
        minowa_gauche_values.append(value_minowa)
    results_gauche["minowa"].append(minowa_gauche_values)

    # Calcul pour le graphe droite
    minowa_droite_values = []
    for i, scenario in enumerate(scenarios_droite):
        _, value_minowa = solve_minowa(scenario, scenarios=scenarios_droite, source='a', cible='g', weights=weights)
        minowa_droite_values.append(value_minowa)
    results_droite["minowa"].append(minowa_droite_values)

# Affichage des MinOWA et MaxOWA séparément
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

# Visualisation des MinOWA
for idx, weights in enumerate(weights_list):
    ax1.plot(range(1, len(scenarios_gauche) + 1), results_gauche["minowa"][idx], label=f"MinOWA Poids {weights}", marker='o')
    ax2.plot(range(1, len(scenarios_droite) + 1), results_droite["minowa"][idx], label=f"MinOWA Poids {weights}", marker='o')

ax1.set_title("Graph Gauche : MinOWA")
ax1.set_xlabel("Scénarios")
ax1.set_ylabel("Valeurs des MinOWA")
ax1.set_xticks(range(1, len(scenarios_gauche) + 1))
ax1.set_xticklabels([f"Scénario {i+1}" for i in range(len(scenarios_gauche))])
ax1.legend()
ax1.grid(True)

ax2.set_title("Graph Droite : MinOWA")
ax2.set_xlabel("Scénarios")
ax2.set_xticks(range(1, len(scenarios_droite) + 1))
ax2.set_xticklabels([f"Scénario {i+1}" for i in range(len(scenarios_droite))])
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig("minowa_comparison.png")
plt.show()

# Affichage des MaxOWA
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

# Calcul et visualisation des MaxOWA
for weights in weights_list:
    maxowa_gauche_values = []
    for i, scenario in enumerate(scenarios_gauche):
        _, value_maxowa = solve_maxowa(scenario, scenarios=scenarios_gauche, source='a', cible='f', weights=weights)
        maxowa_gauche_values.append(value_maxowa)
    results_gauche["maxowa"].append(maxowa_gauche_values)

    maxowa_droite_values = []
    for i, scenario in enumerate(scenarios_droite):
        _, value_maxowa = solve_maxowa(scenario, scenarios=scenarios_droite, source='a', cible='g', weights=weights)
        maxowa_droite_values.append(value_maxowa)
    results_droite["maxowa"].append(maxowa_droite_values)

# Graphe gauche (MaxOWA)
for idx, weights in enumerate(weights_list):
    ax1.plot(range(1, len(scenarios_gauche) + 1), results_gauche["maxowa"][idx], label=f"MaxOWA Poids {weights}", marker='o')
ax1.set_title("Graph Gauche : MaxOWA")
ax1.set_xlabel("Scénarios")
ax1.set_ylabel("Valeurs des MaxOWA")
ax1.set_xticks(range(1, len(scenarios_gauche) + 1))
ax1.set_xticklabels([f"Scénario {i+1}" for i in range(len(scenarios_gauche))])
ax1.legend()
ax1.grid(True)

# Graphe droite (MaxOWA)
for idx, weights in enumerate(weights_list):
    ax2.plot(range(1, len(scenarios_droite) + 1), results_droite["maxowa"][idx], label=f"MaxOWA Poids {weights}", marker='o')
ax2.set_title("Graph Droite : MaxOWA")
ax2.set_xlabel("Scénarios")
ax2.set_xticks(range(1, len(scenarios_droite) + 1))
ax2.set_xticklabels([f"Scénario {i+1}" for i in range(len(scenarios_droite))])
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig("maxowa_comparison.png")
plt.show()