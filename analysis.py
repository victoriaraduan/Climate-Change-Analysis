import re
from textblob import TextBlob
from collections import defaultdict
import nltk
import networkx as nx
from datetime import datetime
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def obtener_hashtags_cambio_climatico(posts):
    hashtags_cambio_climatico = set()

    for post in posts:
        hashtags = [tag['name'].lower() for tag in post.get('tags', [])]
        hashtags_cambio_climatico.update(hashtags)

    return list(hashtags_cambio_climatico)

def identificar_hashtags_populares(hashtags):
    frecuencia_hashtags = defaultdict(int)
    for hashtag in hashtags:
        frecuencia_hashtags[hashtag] += 1

    hashtags_populares = sorted(frecuencia_hashtags.items(), key=lambda x: x[1], reverse=True)
    return hashtags_populares

def detectar_comunidades(red_social): 
    comunidades = list(nx.strongly_connected_components(red_social))
    return comunidades

def analizar_sentimientos(posts):
    polaridades = []
    usuarios_activos = defaultdict(lambda: {'posts': 0, 'polaridad_total': 0, 'hashtags': []})

    for post in posts:
        contenido = post.get('content', '')
        polaridad = TextBlob(contenido).sentiment.polarity
        polaridades.append(polaridad)

        usuario = post['account']['acct']
        usuarios_activos[usuario]['posts'] += 1
        usuarios_activos[usuario]['polaridad_total'] += polaridad
        usuarios_activos[usuario]['hashtags'].extend([tag['name'].lower() for tag in post.get('tags', [])])

    polaridad_promedio = sum(polaridades) / len(polaridades) if polaridades else 0

    for usuario in usuarios_activos:
        usuarios_activos[usuario]['polaridad_promedio'] = usuarios_activos[usuario]['polaridad_total'] / usuarios_activos[usuario]['posts']
        usuarios_activos[usuario]['tendencia'] = "Alarmista" if usuarios_activos[usuario]['polaridad_promedio'] < 0 else "Optimista"

    return polaridad_promedio, dict(usuarios_activos)

def analizar_tendencias_hashtags(posts):
    hashtags = obtener_hashtags_cambio_climatico(posts)
    hashtags_populares = identificar_hashtags_populares(hashtags)

    coocurrencia_hashtags = defaultdict(int)
    for post in posts:
        hashtags_post = [tag['name'].lower() for tag in post.get('tags', [])]
        for i in range(len(hashtags_post)):
            for j in range(i+1, len(hashtags_post)):
                hashtag1 = hashtags_post[i]
                hashtag2 = hashtags_post[j]
                coocurrencia_hashtags[(hashtag1, hashtag2)] += 1
                coocurrencia_hashtags[(hashtag2, hashtag1)] += 1

    return hashtags_populares, dict(coocurrencia_hashtags)

def analizar_contenido(posts):
    temas_discutidos = defaultdict(int)
    tipos_contenido = defaultdict(int)

    for post in posts:
        contenido = post.get('content', '')
        temas = re.findall(r'#\w+', contenido)
        for tema in temas:
            temas_discutidos[tema.lower()] += 1

        if 'media_attachments' in post:
            tipos_contenido['media'] += 1
        elif 'reblog' in post:
            tipos_contenido['compartido'] += 1
        else:
            tipos_contenido['texto'] += 1

    return dict(temas_discutidos), dict(tipos_contenido)

def analizar_redes_sociales(posts):
    red_social = nx.DiGraph()

    for post in posts:
        usuario_autor = post['account']['acct']
        red_social.add_node(usuario_autor)

        if 'mentions' in post:
            for mencion in post['mentions']:
                usuario_mencionado = mencion['acct']
                red_social.add_node(usuario_mencionado)
                red_social.add_edge(usuario_autor, usuario_mencionado)

    comunidades = detectar_comunidades(red_social)
    influencers = nx.betweenness_centrality(red_social)

    return red_social, comunidades, dict(influencers)

def analizar_actividad(posts):
    actividad_diaria = defaultdict(int)

    for post in posts:
        fecha_publicacion = post['created_at']
        fecha = datetime.strptime(fecha_publicacion, "%Y-%m-%dT%H:%M:%S.%fZ")
        dia = fecha.strftime("%Y-%m-%d")
        actividad_diaria[dia] += 1

    return dict(actividad_diaria)


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def generar_grafico_actividad_diaria(actividad_diaria):
    fechas = [datetime.strptime(fecha, "%Y-%m-%d") for fecha in actividad_diaria.keys()]
    frecuencias = list(actividad_diaria.values())

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(fechas, frecuencias, linewidth=1, color='blue', label='Actividad diaria')
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Actividad', fontsize=12)
    ax.set_title('Actividad diaria en el discurso sobre el cambio climático en Mastodon', fontsize=14)

    # Formatear las fechas en el eje x
    date_format = mdates.DateFormatter('%Y-%m')
    ax.xaxis.set_major_formatter(date_format)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Mostrar etiquetas cada mes
    fig.autofmt_xdate(rotation=45)

    # Ajustar los límites del eje y
    ax.set_ylim(bottom=0)

    # Mostrar una cuadrícula
    ax.grid(True, linestyle='--', linewidth=0.5)

    # Resaltar valores atípicos o eventos significativos
    fechas_destacadas = ['2024-02-28', '2024-03-06', '2024-03-19']
    for fecha in fechas_destacadas:
        if fecha in actividad_diaria:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            ax.annotate(fecha, xy=(fecha_dt, actividad_diaria[fecha]), xytext=(10, 10), textcoords='offset points',
                        fontsize=10, color='red', arrowprops=dict(arrowstyle='->', color='red'))

    # Agregar una leyenda
    ax.legend(loc='upper left', fontsize=10)

    plt.tight_layout()
    plt.savefig('actividad_diaria.png', dpi=300)
    plt.show()