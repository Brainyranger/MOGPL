import matplotlib.pyplot as plt
import numpy as np

# Définition des points (vecteurs image)
points = {
    "z(x^*)": (66.0, 66.0), 
    "z(x1^*)": (66.0, 0),
    "z(x2^*)": (0, 66.0),
    "z(x'_1)": (112.0, 0), 
    "z(x'_2)": (0, 118.0), 
    "z(x'^*)": (112.0, 118.0)  
}

# Création du graphique
plt.figure(figsize=(11, 6))

# Tracer les points
for label, (z1, z2) in points.items():
    plt.scatter(z1, z2, label=f'{label} ({z1}, {z2})', s=100, zorder=5)

# Définir les coordonnées pour les droites reliant les points
# Droite entre z(x1^*) et z(x2^*)
x1, y1 = points["z(x1^*)"]
x2, y2 = points["z(x2^*)"]
plt.plot([x1, x2], [y1, y2], 'r--', label="Droite $z(x_1^*) - z(x_2^*)$", zorder=3)



# Droite entre z(x'_1) et z(x'_2)
x5, y5 = points["z(x'_1)"]
x6, y6 = points["z(x'_2)"]
plt.plot([x5, x6], [y5, y6], 'b--', label="Droite $z(x'_1) - z(x'_2)$", zorder=3)

# Ajouter des annotations pour les points
for label, (z1, z2) in points.items():
    plt.annotate(f'{label}', (z1 + 2, z2 + 2), fontsize=10)

# Ajouter des axes et des labels
plt.axhline(0, color='black', linewidth=1, zorder=1)
plt.axvline(0, color='black', linewidth=1, zorder=1)
plt.xlabel('$z_1(x)$', fontsize=14)
plt.ylabel('$z_2(x)$', fontsize=14)

# Ajouter un titre
plt.title('Représentation des points et des droites dans le plan $z_1(x)$, $z_2(x)$', fontsize=16)

# Ajouter une légende
plt.legend()

# Afficher le graphique
plt.grid(True)
plt.show()
