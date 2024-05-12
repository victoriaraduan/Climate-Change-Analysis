from config import load_config
from mastodon import obtener_todos_los_post_mongodb
from analysis import analizar_actividad, generar_grafico_actividad_diaria

# Cargar configuración
config = load_config()

def generar_grafico():
    try:
        print("Obteniendo los posts...")
        posts = obtener_todos_los_post_mongodb(config)
        print("Tengo:", len(posts), "posts")

        actividad_diaria = analizar_actividad(posts)
        generar_grafico_actividad_diaria(actividad_diaria)

    except Exception as e:
        print(f'Error al generar el gráfico: {e}')

if __name__ == "__main__":
    generar_grafico()