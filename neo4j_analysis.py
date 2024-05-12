from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

driver = GraphDatabase.driver(uri, auth=(user, password))

def analizar_usuarios_activos(tx, skip, limit):
    query = """
    MATCH (u:Usuario)
    RETURN u.name AS usuario, u.posts AS posts, u.polaridad_promedio AS polaridad_promedio, u.tendencia AS tendencia
    ORDER BY u.posts DESC
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    return [(record["usuario"], record["posts"], record["polaridad_promedio"], record["tendencia"]) for record in result]

def analizar_hashtags_populares(tx, skip, limit):
    query = """
    MATCH (h:Hashtag)
    RETURN h.name AS hashtag, h.frecuencia AS frecuencia
    ORDER BY h.frecuencia DESC
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    return [(record["hashtag"], record["frecuencia"]) for record in result]

def obtener_hashtags_por_usuario(tx, skip, limit):
    query = """
    MATCH (u:Usuario)-[:USADO]->(h:Hashtag)
    RETURN u.name AS usuario, collect(h.name) AS hashtags
    ORDER BY usuario
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    return [(record["usuario"], record["hashtags"]) for record in result]

def calcular_coocurrencia_hashtags(hashtags_por_usuario):
    coocurrencia_hashtags = []
    for usuario, hashtags in hashtags_por_usuario:
        for i in range(len(hashtags)):
            for j in range(i+1, len(hashtags)):
                hashtag1 = hashtags[i]
                hashtag2 = hashtags[j]
                coocurrencia_hashtags.append((hashtag1, hashtag2))
    return coocurrencia_hashtags

def analizar_coocurrencia_hashtags(tx, skip, limit):
    hashtags_por_usuario = obtener_hashtags_por_usuario(tx, skip, limit)
    coocurrencia_hashtags = calcular_coocurrencia_hashtags(hashtags_por_usuario)
    return coocurrencia_hashtags

def detectar_comunidades(tx, skip, limit):
    query = """
    MATCH (c:Comunidad) 
    RETURN c.id AS id
    ORDER BY c.id
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    comunidades = {}
    for record in result:
        comunidad_id = record["id"]
        query = """
        MATCH (u:Usuario)-[:PERTENECE]->(c:Comunidad {id: $id})
        RETURN u.name AS usuario
        """
        usuarios_result = tx.run(query, id=comunidad_id)
        usuarios = [record["usuario"] for record in usuarios_result]
        comunidades[comunidad_id] = usuarios
    return comunidades

def analizar_polaridad_promedio(tx):
    query = """
    MATCH (u:Usuario)
    RETURN AVG(u.polaridad_promedio) AS polaridad_promedio
    """
    result = tx.run(query)
    return result.single()["polaridad_promedio"]

def analizar_tendencia_usuarios(tx):
    query = """
    MATCH (u:Usuario)
    RETURN u.tendencia AS tendencia, COUNT(*) AS cantidad
    ORDER BY cantidad DESC
    """
    result = tx.run(query)
    return [(record["tendencia"], record["cantidad"]) for record in result]

def analizar_influencers(tx, skip, limit):
    query = """
    MATCH (u:Usuario)
    RETURN u.name AS usuario, u.influencia AS influencia
    ORDER BY u.influencia DESC
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    return [(record["usuario"], record["influencia"]) for record in result]

def analizar_temas_discutidos(tx, skip, limit):
    query = """
    MATCH (t:TemaDiscutido)
    RETURN t.name AS tema, t.frecuencia AS frecuencia
    ORDER BY t.frecuencia DESC
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    return [(record["tema"], record["frecuencia"]) for record in result]

def analizar_tipos_contenido(tx, skip, limit):
    query = """
    MATCH (t:TipoContenido)
    RETURN t.name AS tipo, t.frecuencia AS frecuencia
    ORDER BY t.frecuencia DESC
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    return [(record["tipo"], record["frecuencia"]) for record in result]

def analizar_actividad_diaria(tx, skip, limit):
    query = """
    MATCH (a:ActividadDiaria)
    RETURN a.fecha AS fecha, a.frecuencia AS frecuencia
    ORDER BY a.fecha
    SKIP $skip
    LIMIT $limit
    """
    result = tx.run(query, skip=skip, limit=limit)
    actividad_diaria = {}
    for record in result:
        fecha = record["fecha"]
        frecuencia = record["frecuencia"]
        actividad_diaria[fecha] = frecuencia
    return actividad_diaria

def ejecutar_analisis():
    batch_size = 1000
    skip = 0

    usuarios_activos = []
    hashtags_populares = []
    coocurrencia_hashtags = []
    comunidades = {}
    tendencia_usuarios = []
    influencers = []
    temas_discutidos = []
    tipos_contenido = []
    actividad_diaria = {}

    with driver.session() as session:
        while True:
            usuarios_activos_batch = session.execute_read(analizar_usuarios_activos, skip, batch_size)
            if not usuarios_activos_batch:
                break
            usuarios_activos.extend(usuarios_activos_batch)
            skip += batch_size

        skip = 0
        while True:
            hashtags_populares_batch = session.execute_read(analizar_hashtags_populares, skip, batch_size)
            if not hashtags_populares_batch:
                break
            hashtags_populares.extend(hashtags_populares_batch)
            skip += batch_size

        skip = 0
        while True:
            coocurrencia_hashtags_batch = session.execute_read(analizar_coocurrencia_hashtags, skip, batch_size)
            if not coocurrencia_hashtags_batch:
                break
            coocurrencia_hashtags.extend(coocurrencia_hashtags_batch)
            skip += batch_size

        skip = 0
        while True:
            comunidades_batch = session.execute_read(detectar_comunidades, skip, batch_size)
            if not comunidades_batch:
                break
            comunidades.update(comunidades_batch)
            skip += batch_size

        polaridad_promedio = session.execute_read(analizar_polaridad_promedio)

        tendencia_usuarios = session.execute_read(analizar_tendencia_usuarios)

        skip = 0
        while True:
            influencers_batch = session.execute_read(analizar_influencers, skip, batch_size)
            if not influencers_batch:
                break
            influencers.extend(influencers_batch)
            skip += batch_size

        skip = 0
        while True:
            temas_discutidos_batch = session.execute_read(analizar_temas_discutidos, skip, batch_size)
            if not temas_discutidos_batch:
                break
            temas_discutidos.extend(temas_discutidos_batch)
            skip += batch_size

        skip = 0
        while True:
            tipos_contenido_batch = session.execute_read(analizar_tipos_contenido, skip, batch_size)
            if not tipos_contenido_batch:
                break
            tipos_contenido.extend(tipos_contenido_batch)
            skip += batch_size

        skip = 0
        while True:
            actividad_diaria_batch = session.execute_read(analizar_actividad_diaria, skip, batch_size)
            if not actividad_diaria_batch:
                break
            actividad_diaria.update(actividad_diaria_batch)
            skip += batch_size

    print("An√°lisis completado")

    # Imprimir resultados o realizar otras acciones con los datos obtenidos

    driver.close()

if __name__ == "__main__":
    ejecutar_analisis()