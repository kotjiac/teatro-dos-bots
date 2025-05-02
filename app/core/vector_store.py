from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from uuid import uuid4
from datetime import datetime
from app.core.embedding import embed
from app.config.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, VECTOR_SIZE

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# === Inicializa a coleção de memória vetorial === #
def inicializar_colecao():
    collections = client.get_collections().collections
    nomes = [c.name for c in collections]
    if QDRANT_COLLECTION not in nomes:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"[QDRANT] Coleção '{QDRANT_COLLECTION}' criada com size={VECTOR_SIZE}.")
    else:
        print(f"[QDRANT] Coleção '{QDRANT_COLLECTION}' já existe.")

# === Adiciona memória vetorial para um agente específico === #
def adicionar_memoria(agent_id: str, texto: str, metadata: dict):
    vector = embed(texto)  # <- Centralizamos aqui

    point_id = metadata.get("uuid", str(uuid4()))
    point = PointStruct(
        id=point_id,
        vector=vector,
        payload={
            "agent_id": agent_id,
            "user_id": metadata.get("user_id", "anon"),
            "content": texto,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    client.upsert(collection_name=QDRANT_COLLECTION, points=[point])
    print(f"[QDRANT] Vetor adicionado para agente '{agent_id}'.")

# === Busca as memórias mais relevantes === #
def buscar_memoria(agent_id: str, texto: str, k: int = 5):
    vetor = embed(texto)

    filtro = Filter(
        must=[
            FieldCondition(
                key="agent_id",
                match=MatchValue(value=agent_id)
            )
        ]
    )

    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=vetor,
        limit=k,
        with_payload=True,
        query_filter=filtro
    )

    return [r.payload.get("content", "") for r in results]

# === Reseta todas as memórias de um agente === #
def resetar_memoria(agent_id: str):
    result = client.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(
                key="agent_id",
                match=MatchValue(value=agent_id)
            )]
        ),
        limit=1000  # safe default
    )
    ids = [point.id for point in result[0]]
    if ids:
        client.delete(collection_name=QDRANT_COLLECTION, points_selector={"points": ids})
        print(f"[QDRANT] Memórias apagadas para agente '{agent_id}'.")
    else:
        print(f"[QDRANT] Nenhuma memória encontrada para agente '{agent_id}'.")
