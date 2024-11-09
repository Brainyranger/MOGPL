## Formulation du problème de chemin le plus rapide avec un programme linéaire

On cherche à minimiser le temps total pour aller du sommet initial s au sommet de destination t dans un graphe orienté et pondéré.
Le temps pour parcourir chaque arc (i, j) dépend d'un scénario donné $$s \in S$$, et est noté $$\(t_{ij}^s\)$$.

### 1. Variables de décision
Pour chaque arc \((i, j)\) du graphe, on définit une variable de décision :
- $$x_{ij}$$ est une variable binaire qui vaut 1 si l'arc (i, j) est utilisé dans le chemin, et 0 sinon.

### 2. Fonction objectif
La fonction objectif consiste à minimiser le temps total pour parcourir le chemin de s à t sous le scénario donné s. Elle est exprimée ainsi :

$$\text{Minimiser} \quad \sum_{(i,j) \in A} t_{ij}^s \cdot x_{ij}$$

où A est l'ensemble des arcs du graphe.

### 3. Contraintes de flux
Pour garantir que le chemin relie le sommet initial s au sommet de destination t, on utilise les contraintes de flux suivantes :

1. **Contrainte d'entrée et de sortie des sommets intermédiaires :**
Pour chaque sommet $$k \in V \setminus \{s, t\}$$, le nombre d'arcs entrants dans k doit être égal au nombre d'arcs sortants de k, ce qui assure la continuité du chemin.

   $$\sum_{(i,k) \in E} x_{ik} - \sum_{(k,j) \in E} x_{kj} = 0 \quad \forall k \in V \setminus{s, t}$$


2. **Contrainte pour le sommet initial s :** Un seul arc doit sortir du sommet initial.

   $$\sum_{(s,j) \in E} x_{sj} - \sum_{(i,s) \in E} x_{is} = 1$$

3. **Contrainte pour le sommet de destination t :**
   Un seul arc doit entrer dans le sommet de destination.

   $$\sum_{(t,j) \in E} x_{it} - \sum_{(i,t) \in E} x_{tj} = 1$$

5. **Binarité des variables de décision :**
  Les variables $$x_{ij}$$ doivent être binaires, indiquant si l'arc (i, j) est utilisé ou non dans le chemin.

   $$x_{ij} \in \{0, 1\}$$  $$\quad \forall (i, j) \in E$$

### 4. Formulation complète du programme linéaire

Le programme linéaire est formulé ainsi :

$$\text{Minimiser} \quad \sum_{(i,j) \in E} t_{ij}^s \cdot x_{ij}$$

sous les contraintes :

$$\sum_{(i,k) \in E} x_{ik} - \sum_{(k,j) \in E} x_{kj} = 0 \quad \forall k \in V \setminus \{s, t\}$$

$$\sum_{(s,j) \in E} x_{sj} - \sum_{(i,s) \in E} x_{is} = 1$$

$$\sum_{(t,j) \in E} x_{it} - \sum_{(i,t) \in E} x_{tj} = 1$$

$$x_{ij} \in ${0, 1}$ \quad \forall (i, j) \in E$$

