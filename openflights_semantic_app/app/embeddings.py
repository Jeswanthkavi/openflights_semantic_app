from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_text_embedding(text):
    emb = model.encode([text])[0]
    return emb.tolist()

def get_embedding(text: str):
    vec = model.encode(text).tolist()
    return vec