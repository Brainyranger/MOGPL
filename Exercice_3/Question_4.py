import random
import time
import string
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
import csv

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


def generate_random_graph( p, density=0.4):
    """
    Génère un graphe aléatoire avec p nœuds et une densité d'arcs donnée.
    Les coûts des arcs sont tirés aléatoirement dans l'intervalle [1, 100].
    Les nœuds sont nommés avec des lettres ('a', 'b', 'c', ...).
    """
    # Création des noms des nœuds (utilisation de lettres pour les nœuds)
    nodes = list(string.ascii_lowercase[:p])  # Créer une liste des p premiers caractères de l'alphabet

    arcs = {}  # Dictionnaire pour les arcs avec leurs coûts
    for i in range(p):
        for j in range(i + 1, p):
            if random.random() < density:  # Décision aléatoire d'ajouter un arc
                cout = random.randint(1, 100)  # Coût aléatoire pour l'arc
                arcs[(nodes[i], nodes[j])] = cout  # Ajouter l'arc et son coût au dictionnaire

    return arcs

def generate_scenarios(graph, n_scenarios):
    """
    Génère n_scenarios scénarios de coûts aléatoires pour chaque arc.
    """
    scenarios = []
    for _ in range(n_scenarios):
        scenario = {arc: random.randint(1, 100) for arc, _ in graph}
        scenarios.append(scenario)
    return scenarios

def mesure_temps_resolution(n_scenarios, p_nodes, n_instances=10):
    """
    Mesure le temps de résolution moyen pour chaque critère de chemin robuste.
    """
    times_maxmin = []
    times_minmax_regret = []
    times_maxowa = []
    times_minowa = []

    results = []
    
    for _ in range(n_instances):
        # Générer un graphe aléatoire avec p_nodes nœuds
        graph = generate_random_graph(p_nodes)
        scenarios = generate_scenarios(graph, n_scenarios)
        weights = [random.random() for _ in range(n_scenarios)]  # Poids aléatoires
        
        # 1. Résoudre le problème pour le critère maxmin
        start_time = time.time()
        solve_maxmin(graph, scenarios, 0, p_nodes - 1)
        times_maxmin.append(time.time() - start_time)

        # 2. Résoudre le problème pour le critère minmax regret
        start_time = time.time()
        solve_minmax_regret(graph, scenarios, 0, p_nodes - 1)
        times_minmax_regret.append(time.time() - start_time)

        # 3. Résoudre le problème pour le critère maxOWA
        for w in weights:
            start_time = time.time()
            solve_maxowa(graph, scenarios, 0, p_nodes - 1, w)
            times_maxowa.append(time.time() - start_time)

        # 4. Résoudre le problème pour le critère minOWA
        for w in weights:
            start_time = time.time()
            solve_minowa(graph, scenarios, 0, p_nodes - 1, w)
            times_minowa.append(time.time() - start_time)

    # Calcul des temps moyens de résolution pour chaque critère
    avg_time_maxmin = sum(times_maxmin) / n_instances
    avg_time_minmax_regret = sum(times_minmax_regret) / n_instances
    avg_time_maxowa = sum(times_maxowa) / n_instances
    avg_time_minowa = sum(times_minowa) / n_instances
    
    print(f"Temps moyen pour maxmin : {avg_time_maxmin:.2f} sec")
    print(f"Temps moyen pour minmax regret : {avg_time_minmax_regret:.2f} sec")
    print(f"Temps moyen pour maxOWA : {avg_time_maxowa:.2f} sec")
    print(f"Temps moyen pour minOWA : {avg_time_minowa:.2f} sec")

    results.append([p_nodes, n_scenarios, avg_time_maxmin, avg_time_minmax_regret, avg_time_maxowa, avg_time_minowa])

    return results


# Test avec différentes configurations
n_values = [2, 5, 10]
p_values = [10, 15, 20]


# Stockage des résultats
all_results = []

# Pour chaque combinaison de n et p
for n in n_values:
    for p in p_values:
        print(f"\nTest pour n = {n} scénarios et p = {p} nœuds:")
        results = mesure_temps_resolution(n, p, n_instances=10)
        all_results.extend(results)

# Enregistrer les résultats dans un fichier CSV
with open("results_temps_resolution.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["p_nodes", "n_scenarios", "AvgTime_MaxMin", "AvgTime_MinMaxRegret", "AvgTime_MaxOWA", "AvgTime_MinOWA"])
    writer.writerows(all_results)

# Convertir les résultats pour les graphiques
p_values_for_plot = [res[0] for res in all_results]
n_values_for_plot = [res[1] for res in all_results]
times_maxmin_for_plot = [res[2] for res in all_results]
times_minmax_regret_for_plot = [res[3] for res in all_results]
times_maxowa_for_plot = [res[4] for res in all_results]
times_minowa_for_plot = [res[5] for res in all_results]

# Créer un graphique des temps de résolution pour chaque critère
plt.figure(figsize=(10, 6))

# MaxMin
plt.subplot(2, 2, 1)
plt.scatter(p_values_for_plot, times_maxmin_for_plot, c=n_values_for_plot, cmap='viridis', label="MaxMin")
plt.title("Temps moyen pour MaxMin")
plt.xlabel("p_nodes")
plt.ylabel("Temps (secondes)")
plt.colorbar(label="n_scenarios")
plt.grid(True)

# MinMaxRegret
plt.subplot(2, 2, 2)
plt.scatter(p_values_for_plot, times_minmax_regret_for_plot, c=n_values_for_plot, cmap='viridis', label="MinMaxRegret")
plt.title("Temps moyen pour MinMaxRegret")
plt.xlabel("p_nodes")
plt.ylabel("Temps (secondes)")
plt.colorbar(label="n_scenarios")
plt.grid(True)

# MaxOWA
plt.subplot(2, 2, 3)
plt.scatter(p_values_for_plot, times_maxowa_for_plot, c=n_values_for_plot, cmap='viridis', label="MaxOWA")
plt.title("Temps moyen pour MaxOWA")
plt.xlabel("p_nodes")
plt.ylabel("Temps (secondes)")
plt.colorbar(label="n_scenarios")
plt.grid(True)

# MinOWA
plt.subplot(2, 2, 4)
plt.scatter(p_values_for_plot, times_minowa_for_plot, c=n_values_for_plot, cmap='viridis', label="MinOWA")
plt.title("Temps moyen pour MinOWA")
plt.xlabel("p_nodes")
plt.ylabel("Temps (secondes)")
plt.colorbar(label="n_scenarios")
plt.grid(True)

# Afficher les graphes
plt.tight_layout()
plt.show()