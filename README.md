# MOGPL 2024 : Optimisation robuste dans l'incertain total

## Comment utiliser notre code :
	
L'ensemble du code présenté dans les parties 1 et 2 est appliqué à l'Exemple 1 du sujet. 

Dans un terminal, effectuer _cd Exercice_X/_ pour accéder aux fichiers Python correspondants à la parti n°X, puis exécuter le fichier concerné avec la commande _python_ ```nom_fichier.py``` (ou _python3_ ```nom_fichier.py``` )


### Partie 1 : Maxmin et Minmax des regrets linéarisés

	- ```maxmin.py``` résout le programme linéaire au sens du critère Maxmin et affiche les valeurs du critère dans les deux scénarios (question 1.1) ;
	- ```minmax_regret.py``` résout le programme linéaire au sens du critère Minmax des regrets et affiche sa valeur (question 1.2) ;
	- ```temps_moyen_real.py``` mesure les temps moyens de réalisations des algorithmes précédents pour des nombres de scénarios et de projets fixés (question 1.4) ;
	- ```graphic.py``` représente les mesures temporelles sur un graphe pour une meilleure visualisation.
	
### Partie 2 : MaxOWA et MinOWA des regrets linéarisés

	- ```dualDk.py``` résout le programme linéaire dual de la question 2.2 ;
	- ```maxOWA.py``` calcule la solution optimale au sens du critère MaxOWA (question 2.4) ;
	- ```minOwa.py``` calcule la solution optimale au sens du critère MinOWA des regrets (question 2.5) ;
	- ```times_execute.py``` mesure et représente les mesures temporelles des solutions au critères MaxOWA et MinOWA des regrets (question 2.6).
	
### Partie 3 : Recherche de chemin robuste dans un graphe

On s'intéressera ici à l'Exemple 2 du sujet.

	- ```Question_1.md``` contient le programme linéaire déterminant le chemin le plus rapide (question 3.1) ;
	- ```Question_2.py``` résout les programmes linéaires associés à la recherche du chemins le plus court (question 3.2) ;
	- ```Question_3a.py``` propose et résout des programmes linéaires adaptés aux critère Maxmin et Minmax des regrets (question 3.3) ;
	- ```Question_3b.py``` propose et résout des programmes linéaires adaptés aux critère MaxOWA et MinOWA des regrets (question 3.3) ;
	- ```Question_4.py``` génère des instances aléatoires (de nombres de scénarios et de noeuds des graphes), mesure et représente les temps d'exécution des algortihmes correspondant aux 4 critères évoqués ci-dessus.
	
