import matplotlib.pyplot as plt

# Définition des points (vecteurs image)
points = {
    "z(x^*)": (66.0, 66.0), 
    "z(x1^*)":(66.0,0),
    "z(x2^*)":(0,66.0),
    "z(x'_1)": (112.0, 0), 
    "z(x'_2)": (0, 118.0), 
    "z(x'^*) ": (112.0, 118.0)  
}

# Création du graphique
plt.figure(figsize=(8, 6))

# Tracer les points
for label, (z1, z2) in points.items():
    plt.scatter(z1, z2, label=f'{label} ({z1}, {z2})', s=100, zorder=5)

# Ajouter des annotations pour les points
for label, (z1, z2) in points.items():
    plt.annotate(f'{label}', (z1 + 1, z2 + 1), fontsize=12)

# Ajouter des axes et des labels
plt.axhline(0, color='black',linewidth=1)
plt.axvline(0, color='black',linewidth=1)
plt.xlabel('$z_1(x)$', fontsize=14)
plt.ylabel('$z_2(x)$', fontsize=14)

# Ajouter un titre
plt.title('Représentation des points dans le plan $z_1(x)$, $z_2(x)$', fontsize=16)

# Ajouter une légende
plt.legend()

# Afficher le graphique
plt.grid(True)
plt.show()
