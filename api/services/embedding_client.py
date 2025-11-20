from openai import AzureOpenAI
import os


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

EMBED_MODEL = os.getenv("AZURE_EMBEDDINGS_MODEL", "embedding-small")

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=[text]
    )
    return response.data[0].embedding
