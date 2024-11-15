import gurobipy as gp
from gurobipy import GRB

# Définir les nœuds pour chaque scénario du graphe
noeuds = ['a', 'b', 'c', 'd', 'e', 'f']  # Pour le graphe de gauche (scénarios 1 et 2)
arcs_scenario1 = {
    ('a', 'b'): 4, ('a', 'c'): 5,
    ('b', 'c'): 2, ('b', 'e'): 2,('b', 'f'): 7,('b', 'd'): 1,
    ('c', 'd'): 5, ('c', 'e'): 2,
    ('d', 'f'): 3,
    ('e', 'f'): 5
}
arcs_scenario2 = {
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

# Fonction pour résoudre le problème de plus court chemin pour un ensemble d'arcs donné
def resoudre_plus_court_chemin(arcs, source='a', cible='f', noeuds=noeuds):
    modele = gp.Model("PlusCourtChemin")
    # Définir les variables : 1 si l'arc est utilisé dans le chemin, 0 sinon
    x = modele.addVars(arcs.keys(), vtype=GRB.BINARY, name="x")

    # Objectif : Minimiser le temps total de parcours
    modele.setObjective(gp.quicksum(arcs[i] * x[i] for i in arcs.keys()), GRB.MINIMIZE)

    # Contraintes de flux pour chaque nœud
    for noeud in noeuds:
        entree = gp.quicksum(x[i, noeud] for i, j in arcs if j == noeud)
        sortie = gp.quicksum(x[noeud, j] for i, j in arcs if i == noeud)
        
        if noeud == source:
            modele.addConstr(sortie - entree == 1)  # La source a un flux net de sortie de 1
        elif noeud == cible:
            modele.addConstr(entree - sortie == 1)  # La cible a un flux net d'entrée de 1
        else:
            modele.addConstr(sortie - entree == 0)  # Les nœuds intermédiaires ont un flux équilibré

    # Résoudre le modèle
    modele.optimize()

    # Extraction de la solution
    if modele.status == GRB.OPTIMAL:
        print(f"Coût du chemin le plus court de {source} à {cible} : {modele.objVal}")
        chemin = [i for i in arcs.keys() if x[i].x > 0.5]
        print("Chemin :", chemin)
    else:
        print("Aucune solution optimale trouvée.")

# affichage des résultats pour chaque scénario du graphe de gauche
print("Résolution pour le Scénario 1 du graphe de gauche :")
resoudre_plus_court_chemin(arcs_scenario1, source='a', cible='f', noeuds=noeuds)
print("\n==============================================")
print("\nRésolution pour le Scénario 2 du graphe de gauche :")
resoudre_plus_court_chemin(arcs_scenario2, source='a', cible='f', noeuds=noeuds)
print("\n==============================================")
# Résolution pour chaque scénario du graphe de droite
print("\nRésolution pour le Scénario 1 du graphe de droite :")
resoudre_plus_court_chemin(arcs_scenario1_droite, source='a', cible='g', noeuds=noeuds_droite)
print("\n==============================================")
print("\nRésolution pour le Scénario 2 du graphe de droite :")
resoudre_plus_court_chemin(arcs_scenario2_droite, source='a', cible='g', noeuds=noeuds_droite)
