
import uuid
import hashlib

from qdrant_client.models import PointStruct, Distance, VectorParams

from qdrant.qdrant_connection import (
    get_qdrant_client,
    COLLECTION_NAME
)

VECTOR_SIZE = 4


def create_collection():
    client = get_qdrant_client()

    collections = [
        item.name for item in client.get_collections().collections
    ]

    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )


def create_account_vector(account):
    followers = float(account.get("followers", 0))
    following = float(account.get("following", 0))
    posts = float(account.get("posts_count", 0))
    age = float(account.get("account_age_days", 0))

    return [
        followers / (followers + 100),
        following / (following + 100),
        posts / (posts + 100),
        age / (age + 100)
    ]


def save_account_vector(account):
    client = get_qdrant_client()
    create_collection()

    user_id = str(account["user_id"])

    point_id = str(
        uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
    )

    vector = create_account_vector(account)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "user_id": user_id,
                    "username": account.get("username", ""),
                    "followers": account.get("followers", 0),
                    "following": account.get("following", 0),
                    "posts_count": account.get("posts_count", 0),
                    "account_age_days": account.get(
                        "account_age_days", 0
                    )
                }
            )
        ]
    )

    return point_id


def search_similar_accounts(account, limit=5):
    client = get_qdrant_client()
    create_collection()

    vector = create_account_vector(account)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit,
        with_payload=True
    )

    return results.points

def delete_account_vector(user_id):
    import uuid
    from qdrant_client.models import PointIdsList

    client = get_qdrant_client()

    point_id = str(
        uuid.uuid5(uuid.NAMESPACE_DNS, str(user_id))
    )

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=PointIdsList(
            points=[point_id]
        )
    )
