from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
import os
 

class VectorStore:
    def __init__(self, image_path: str = 'image_store', text_path: str = 'text_store'):
        if not os.path.exists(image_path):
            self.images = QdrantClient(path=image_path)
            self.create(self.images, 2*1024, 'images')
        else:
            self.images = QdrantClient(path=image_path)
        
        
        if not os.path.exists(text_path):
            self.texts = QdrantClient(path=text_path)
            self.create(self.texts, 1024, 'texts')
        else:
            self.texts = QdrantClient(path=text_path)


    def query(self, image_vector: list, text_vector: list, limit: int = 5):
        img_hits = self.images.search(
            limit=limit,
            collection_name="images",
            query_vector=image_vector
        )
        text_hits = self.texts.search(
            limit=limit,
            collection_name="texts",
            query_vector=text_vector
        )

        print(img_hits, text_hits)
        # TODO merge res

    def insert(self, id, vector: list, filename, page, v_type):
        client = self.texts if v_type == 'text' else self.images
        client.upload_records(
            collection_name=v_type + 's',
            records=[
                models.Record(
                    id=id,
                    vector=vector,
                    payload={
                        'filename': filename,
                        'page': page
                    }
                )
            ]
        )

    def create(self, client: QdrantClient, var_size: int, name: str):
        client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=var_size,
                distance=Distance.COSINE,
            )
        )