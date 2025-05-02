from app.config.config import OPENAI_API_KEY, USE_OPENAI, EMBED_MODEL
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def embed(text: str) -> list[float]:
    if USE_OPENAI:
        response = client.embeddings.create(
            input=text,
            model=EMBED_MODEL
        )
        return response.data[0].embedding
