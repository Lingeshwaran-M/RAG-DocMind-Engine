import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# Load document
with open("document.txt", "r") as f:
    text = f.read()

# Split into chunks (line by line)
documents = [line.strip() for line in text.split("\n") if line.strip()]

# Load embedding model
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings
print("Creating embeddings...")
doc_embeddings = embedder.encode(documents)

# Store embeddings in FAISS
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings))

print("RAG system ready!\n")

# Ask user question
query = input("Ask something: ")

# Embed query
query_embedding = embedder.encode([query])

# Retrieve top 3 relevant lines
k = 3
D, I = index.search(np.array(query_embedding), k=k)

retrieved_context = "\n".join([documents[i] for i in I[0]])

# Create prompt
prompt = f"""
You are operating inside a STRICT Retrieval-Augmented Generation system.

IMPORTANT RULES:
1. You must answer ONLY using the provided context.
2. If the answer is not explicitly written in the context,
   you MUST respond exactly with:
   "The provided context does not contain enough information."
3. Do NOT use prior knowledge.
4. Do NOT infer or guess.
5. Do NOT explain beyond context.

Context:
{retrieved_context}

Question:
{query}

Answer:
"""


# Call Ollama
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }
)


print("\nRetrieved Context:\n")
print(retrieved_context)

print("\nFinal Answer:\n")
print(response.json()["response"])

