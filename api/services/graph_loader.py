from gremlin_python.driver import client, serializer
import os

def get_gremlin_client():
    return client.Client(
        os.getenv("COSMOS_ENDPOINT"),
        'g',
        username=f"/dbs/{os.getenv('COSMOS_DATABASE')}/colls/{os.getenv('COSMOS_GRAPH')}",
        password=os.getenv("COSMOS_KEY"),
        message_serializer=serializer.GraphSONSerializersV2d0()
    )

def insert_graph(nodes, edges):
    gremlin = get_gremlin_client()
    for node in nodes:
        gremlin.submit(f"g.addV('entity').property('id', '{node}').property('pk', '1')").all().result()

    for src, rel, tgt in edges:
        gremlin.submit(f"""
            g.V('{src}').addE('{rel}').to(g.V('{tgt}'))
        """).all().result()
