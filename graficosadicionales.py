import matplotlib.pyplot as plt

hashtags = ['energy', 'pollution', 'fire', 'sustainable', 'climatechange','action', 'climate', 'environment', 'drought', 'emissions']
frecuencias = [4479, 2968, 2655, 1581, 1559, 1502, 1441, 1237, 1236, 926]

# Gráfico de barras
plt.figure(figsize=(10, 6))
plt.bar(hashtags, frecuencias)
plt.xlabel('Hashtags')
plt.ylabel('Frecuencia')
plt.title('Distribución de Hashtags Populares')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('hashtags_populares_barras.png')
plt.show()

# Gráfico de pastel
plt.figure(figsize=(8, 8))
plt.pie(frecuencias, labels=hashtags, autopct='%1.1f%%')
plt.title('Distribución de Hashtags Populares')
plt.tight_layout()
plt.savefig('hashtags_populares_pastel.png')
plt.show()