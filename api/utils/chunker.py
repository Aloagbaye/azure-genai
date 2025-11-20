import nltk
from uuid import uuid4

def chunk_text(text, max_tokens=200):
    sentences = nltk.sent_tokenize(text)
    chunks, current = [], ""
    for sent in sentences:
        if len((current + sent).split()) > max_tokens:
            chunks.append(current.strip())
            current = sent
        else:
            current += " " + sent
    if current:
        chunks.append(current.strip())
    return chunks

def prepare_documents(text, title):
    chunks = chunk_text(text)
    return [
        {
            "id": str(uuid4()),
            "title": title,
            "content": chunk
        }
        for chunk in chunks
    ]
