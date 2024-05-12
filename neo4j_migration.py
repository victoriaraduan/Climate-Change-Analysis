from neo4j import GraphDatabase

def migrate_to_neo4j(results):
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"

    driver = GraphDatabase.driver(uri, auth=(user, password))

    def create_nodes_and_relationships(tx, results):
        # Crear nodos y relaciones en Neo4j según los resultados del análisis
        # Utiliza las funciones de Cypher para crear los nodos y las relaciones

        # Creación de nodos para usuarios y hashtags
        for usuario, datos in results['usuarios_activos'].items():
            print("Insertando usuario")
            tx.run("MERGE (u:Usuario {name: $usuario}) "
                   "SET u.posts = $posts, u.polaridad_promedio = $polaridad_promedio, u.tendencia = $tendencia",
                   usuario=usuario, posts=datos['posts'], polaridad_promedio=datos['polaridad_promedio'], tendencia=datos['tendencia'])

        for hashtag, frecuencia in results['hashtags_populares']:
            print("Creando hashtag")
            tx.run("MERGE (:Hashtag {name: $hashtag, frecuencia: $frecuencia})", hashtag=hashtag, frecuencia=frecuencia)

        # Creación de relaciones entre usuarios y hashtags
        for usuario, datos in results['usuarios_activos'].items():
            for hashtag in datos['hashtags']:
                print("Creando relación usuario-hashtag")
                tx.run("MATCH (u:Usuario {name: $usuario}), (h:Hashtag {name: $hashtag}) "
                       "MERGE (u)-[:USADO]->(h)", usuario=usuario, hashtag=hashtag)

        # Creación de relaciones entre usuarios
        for post in results['posts']:
            usuario_autor = post['account']['acct']
            
            if 'mentions' in post:
                for mencion in post['mentions']:
                    usuario_mencionado = mencion['acct']
                    print("Creando relación usuario-mención")
                    tx.run("MATCH (u1:Usuario {name: $usuario_autor}), (u2:Usuario {name: $usuario_mencionado}) "
                           "MERGE (u1)-[:MENCIONA]->(u2)", usuario_autor=usuario_autor, usuario_mencionado=usuario_mencionado)
                        
            if 'reblogs' in post:
                for reblog in post['reblogs']:
                    usuario_reblog = reblog['account']['acct']
                    print("Creando relación usuario-reblog")
                    tx.run("MERGE (u1:Usuario {name: $usuario_autor}) "
                        "MERGE (u2:Usuario {name: $usuario_reblog}) "
                        "MERGE (u1)-[:INTERACTUA_CON]->(u2)", usuario_autor=usuario_autor, usuario_reblog=usuario_reblog)

            if 'favourites' in post:
                for like in post['favourites']:
                    usuario_like = like['acct']
                    print("Creando relación usuario-like")
                    tx.run("MERGE (u1:Usuario {name: $usuario_autor}) "
                        "MERGE (u2:Usuario {name: $usuario_like}) "
                        "MERGE (u1)-[:INTERACTUA_CON]->(u2)", usuario_autor=usuario_autor, usuario_like=usuario_like)

        # Creación de nodos para temas discutidos y tipos de contenido
        for tema, frecuencia in results['temas_discutidos'].items():
            print("Creando tema discutido")
            tx.run("MERGE (:TemaDiscutido {name: $tema, frecuencia: $frecuencia})", tema=tema, frecuencia=frecuencia)

        for tipo, frecuencia in results['tipos_contenido'].items():
            print("Creando tipo de contenido")
            tx.run("MERGE (:TipoContenido {name: $tipo, frecuencia: $frecuencia})", tipo=tipo, frecuencia=frecuencia)

        # Creación de nodos para comunidades y relaciones con usuarios
        for i, comunidad in enumerate(results['comunidades']):
            print("Creando comunidad")
            tx.run("MERGE (:Comunidad {id: $id})", id=i)
            for usuario in comunidad:
                print("Creando relación usuario-comunidad")
                tx.run("MATCH (u:Usuario {name: $usuario}), (c:Comunidad {id: $id}) "
                       "MERGE (u)-[:PERTENECE]->(c)", usuario=usuario, id=i)

        # Creación de nodos para influencers y relaciones con usuarios
        for usuario, influencia in results['influencers'].items():
            print("Creando influencer")
            tx.run("MATCH (u:Usuario {name: $usuario}) "
                   "SET u.influencia = $influencia", usuario=usuario, influencia=influencia)

        # Creación de nodos para actividad diaria
        for fecha, frecuencia in results['actividad_diaria'].items():
            print("Creando actividad diaria")
            tx.run("MERGE (:ActividadDiaria {fecha: $fecha, frecuencia: $frecuencia})", fecha=fecha, frecuencia=frecuencia)

    with driver.session() as session:
        session.write_transaction(create_nodes_and_relationships, results)
        print("Migración completada")

    driver.close()