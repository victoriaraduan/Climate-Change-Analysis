import pandas as pd

# Lee el archivo CSV exportado desde Neo4j
data = pd.read_csv('C:/Users/Vic/Downloads/prueba.csv')

# Calcula el coeficiente de correlación de Pearson entre la polaridad y la influencia
correlation_coefficient = data['num_posts'].corr(data['influencia'])

print(f"Coeficiente de correlación de Pearson: {correlation_coefficient:.4f}")