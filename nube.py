from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Datos de ejemplo
temas_discutidos = {
    "#energy":1294,
    "#energyandclimate":635,
    "#emissions":446,
    "#politics": 432,
    "#warinukraine":421,
    "#climatechange":394,
    "#sustainability":377,
    "#fire":329,
    "#trade":314
    
    }

# Crear la nube de palabras
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(temas_discutidos)

# Mostrar la nube de palabras
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()
plt.savefig('nube_palabras_temas_discutidos.png')
plt.show()