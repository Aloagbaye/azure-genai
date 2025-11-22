import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    nodes = set()
    edges = []

    for sent in doc.sents:
        ents = [ent.text for ent in sent.ents]
        for i in range(len(ents) - 1):
            edges.append((ents[i], "related_to", ents[i + 1]))
            nodes.update([ents[i], ents[i + 1]])

    return list(nodes), edges
