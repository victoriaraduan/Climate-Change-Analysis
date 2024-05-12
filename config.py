import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    config = {
        'mongo_uri': os.getenv('MONGO_URI'),
        'access_token': os.getenv('ACCESS_TOKEN'),
        'base_url': 'https://mastodon.social/api/v1/',
        'db_name': 'mastodon_data',
        'posts_collection': 'cambioclimatico',
        'last_id_collection': 'last_processed_id'
    }
    return config