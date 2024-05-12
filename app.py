import time
import os
from random import randint
import json
import neo4j
from config import load_config
from mastodon import obtener_posts, guardar_en_mongodb, obtener_post_mongodb, obtener_todos_los_post_mongodb
from analysis import (
    analizar_sentimientos,
    analizar_tendencias_hashtags,
    analizar_contenido,
    analizar_redes_sociales,
    analizar_actividad,
)
from neo4j_migration import migrate_to_neo4j

# Cargar configuración
config = load_config()
estado_path = 'estado_hastags.json'

# Leer el estado actual desde el archivo
def leer_estado():
    if os.path.exists(estado_path):
        with open(estado_path, 'r') as f:
            return json.load(f)
    return {}

# Guardar el estado actual en el archivo
def guardar_estado(estado):
    with open(estado_path, 'w') as f:
        json.dump(estado, f)


# Bucle principal
hastagsh = [
    'calentamiento', 
    'emisiones', 
    'gases', 
    'efecto', 
    'invernadero',
    'energía', 
    'renovable', 
    'sostenible', 
    'contaminación', 
    'deforestación', 
    'impacto', 
    'sequía', 
    'incendio', 
    'deshielo', 
    'acción',
    'warm-up',
    'emissions',
    'effect',
    'greenhouse',
    'energy',
    'renewable',
    'sustainable',
    'pollution',
    'deforestation',
    'impact',
    'drought',
    'fire',
    'melting',
    'action'
]
def obtener_posts_mastodon():
    while True:
        try:
            # Obtener posts y guardar en MongoDB
            hastags_done = leer_estado()
            for hastag in hastagsh:
                if hastag in hastags_done:
                    print(f"El hashtag {hastag} ya se ha procesado")
                    continue
                else:
                    max_id = None
                    posts_ = []
                    
                    while True:
                        posts = obtener_posts(config, hastag, None, max_id)
                        posts_ += posts

                        print(f"Hashtag: {hastag}")
                        print(f"Cantidad de posts obtenidos: {len(posts)}")
                        print(f"Cantidad de posts total: {len(posts_)}")
                        
                        if len(posts) < 40:
                            break
                        else:
                            max_id = posts[-1]["id"]
                        
                        time.sleep(randint(5, 15))  # Espera entre 5 y 15 segundos
                    
                    guardar_en_mongodb(posts_, config)
                    hastags_done.append(hastag)
                    guardar_estado(hastags_done)
            print("Proceso de obtener todos los posts de Mastodon completado.")
            break
        except Exception as e:
            print(f'Error en el bucle principal: {e}')
            break
def migrar_de_mongo_a_neo4j2():
    print("Entro")
    try:
        print("obteniendo los posts...")
        posts_ = obtener_todos_los_post_mongodb(config)
        print("Tengo: "+str(len(posts_)))
                
        # Realizar análisis
        polaridad_promedio, usuarios_activos = analizar_sentimientos(posts_)
        hashtags_populares, coocurrencia_hashtags = analizar_tendencias_hashtags(posts_)
        temas_discutidos, tipos_contenido = analizar_contenido(posts_)
        red_social, comunidades, influencers = analizar_redes_sociales(posts_)
        actividad_diaria = analizar_actividad(posts_)

        resultados_analisis = {
            'posts': posts_,
            'polaridad_promedio': polaridad_promedio,
            'usuarios_activos': usuarios_activos,
            'hashtags_populares': hashtags_populares,
            'coocurrencia_hashtags': coocurrencia_hashtags,
            'temas_discutidos': temas_discutidos,
            'tipos_contenido': tipos_contenido,
            'red_social': red_social,
            'comunidades': comunidades,
            'influencers': influencers,
            'actividad_diaria': actividad_diaria
        }
       
        # Migrar los resultados del análisis a Neo4j
        migrate_to_neo4j(resultados_analisis)

    except neo4j.exceptions.ClientError as e:
        if 'no such relationship type' in str(e):
            print("Error: No se encontraron relaciones 'INTERACTUA_CON' en la base de datos.")
            print("Asegúrate de que las relaciones se hayan creado correctamente durante la migración.")
        else:
            print(f'Error en el bucle principal de análisis de Neo4j: {e}')
    except Exception as e:
        print(f'Error en el bucle principal de análisis de Neo4j: {e}')

migrar_de_mongo_a_neo4j2()