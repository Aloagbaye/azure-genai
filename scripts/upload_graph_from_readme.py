import os
import spacy
from gremlin_python.driver import client, serializer
from dotenv import load_dotenv

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Load env variables
load_dotenv()

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "knowledge")
COSMOS_GRAPH = os.getenv("COSMOS_GRAPH", "tutorialgraph")

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def extract_entities_and_edges(text):
    doc = nlp(text)
    entities = set()
    edges = []

    for sent in doc.sents:
        ents = [ent.text.strip() for ent in sent.ents if ent.label_ not in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY"]]
        for i in range(len(ents) - 1):
            edges.append((ents[i], "related_to", ents[i + 1]))
            entities.update([ents[i], ents[i + 1]])

    return list(entities), edges

def get_gremlin_client():
    return client.Client(
        "wss://genai-graph.gremlin.cosmos.azure.com:443/",
        "g",
        username=f"/dbs/{COSMOS_DATABASE}/colls/{COSMOS_GRAPH}",
        password=COSMOS_KEY,
        message_serializer=serializer.GraphSONSerializersV2d0()
        )


def upload_to_graphdb(entities, edges):
    gremlin = get_gremlin_client()
    #import pdb; pdb.set_trace()
    for entity in entities:
        gremlin.submit(f"""g.V('{entity}').fold().coalesce(unfold(), addV('entity').property('id', '{entity}').property('pk', '1'))""").all().result()

    for src, rel, tgt in edges:
        gremlin.submit(f"g.V('{src}').addE('{rel}').to(g.V('{tgt}'))").all().result()

def main():
    with open("azure_genai_rag_article.md", "r", encoding="utf-8") as f:
        text = f.read()

    entities, edges = extract_entities_and_edges(text)
    print(f"✅ Extracted {len(entities)} entities and {len(edges)} edges.")
    upload_to_graphdb(entities, edges)
    print("✅ Uploaded to Cosmos DB Graph.")

if __name__ == "__main__":
    main()