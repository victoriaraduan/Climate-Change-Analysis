import requests
from pymongo import MongoClient

def obtener_posts(config, hashtag=None, desde_id=None, max_id=None):
    try:
        # Construir el endpoint según los parámetros
        if hashtag:
            endpoint = f'timelines/tag/{hashtag}?limit=40'
        else:
            endpoint = 'timelines/public?limit=40'
        
        # Agregar parámetros adicionales si se proporcionan
        if desde_id:
            endpoint += f'&since_id={desde_id}'
        if max_id:
            endpoint += f'&max_id={max_id}'
        print(endpoint)
        headers = {'Authorization': 'Bearer ' + config['access_token']}
        response = requests.get(config['base_url'] + endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error al obtener los posts: {response.status_code}')
            return None
    except Exception as e:
        print(f'Error al obtener los posts: {e}')
        return None

def guardar_en_mongodb(posts, config):
    try:
        client = MongoClient(config['mongo_uri'])
        db = client[config['db_name']]
        collection = db[config['posts_collection']]
        last_processed_id_collection = db[config['last_id_collection']]

        if posts:
            for post in posts:
                # Almacenar el post
                collection.insert_one(post)
                # Almacenar relaciones de menciones
                if 'mentions' in post:
                    for mention in post['mentions']:
                        # Crear una relación en MongoDB
                        db['mentions'].insert_one({'from': post['account']['username'], 'to': mention['acct']})
                # Almacenar relaciones de retweets
                if 'reblogs' in post:
                    for reblog in post['reblogs']:
                        # Crear una relación en MongoDB
                        db['retweets'].insert_one({'from': post['account']['username'], 'to': reblog['account']['acct']})
                # Almacenar relaciones de likes
                if 'favourites' in post:
                    for like in post['favourites']:
                        # Crear una relación en MongoDB
                        db['likes'].insert_one({'from': post['account']['username'], 'to': like['acct']})
            print(f'Datos guardados en MongoDB. Total de posts: {len(posts)}')
            last_processed_id = posts[-1]['id']
            guardar_ultimo_id_procesado(last_processed_id, last_processed_id_collection)
        else:
            print('No se pudieron guardar los datos en MongoDB.')
    except Exception as e:
        print(f'Error al guardar datos en MongoDB: {e}')
def obtener_post_mongodb(hastagh, config):
    try:
        client = MongoClient(config['mongo_uri'])
        db = client[config['db_name']]
        collection = db[config['posts_collection']]
        return list(collection.find({'tags.name': hastagh}))
    except Exception as e:
        print(f'Error al obtener los post de mongo: {e}')
def obtener_todos_los_post_mongodb(config):
    try:
        client = MongoClient(config['mongo_uri'])
        db = client[config['db_name']]
        collection = db[config['posts_collection']]
        return list(collection.find())
    except Exception as e:
        print(f'Error al obtener los post de mongo: {e}')    

def obtener_ultimo_id_procesado(last_processed_id_collection):
    document = last_processed_id_collection.find_one()
    if document:
        return document['last_id']
    else:
        return None

def guardar_ultimo_id_procesado(last_id, last_processed_id_collection):
    last_processed_id_collection.update_one({}, {'$set': {'last_id': last_id}}, upsert=True)