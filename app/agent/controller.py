from app.agent.intent_classifier import classify_intent
from app.rag.embedder import get_embeddings
from app.rag.retriever import retrieve
from groq import Groq
from app.config import GROQ_API_KEY
from typing import List

client = Groq(api_key=GROQ_API_KEY)

# Each intent gets its own prompt strategy
PROMPT_TEMPLATES = {
    "summarize": """You are a summarization expert.
Using ONLY the context below, write a clear and concise summary.
Focus on the main points and key takeaways.

Context:
{context}

Question: {question}

Summary:""",

    "extract": """You are a data extraction expert.
Using ONLY the context below, extract the specific information requested.
Present it as a clean structured list. If nothing matches, say so.

Context:
{context}

Question: {question}

Extracted Information:""",

    "answer": """You are a helpful assistant.
Using ONLY the context below, answer the question directly and concisely.
If the answer is not in the context, say "I couldn't find relevant information in the document."

Context:
{context}

Question: {question}

Answer:"""
}

def run_agent(question: str) -> dict:
    # Step 1: Classify intent
    intent = classify_intent(question)

    # Step 2: Embed and retrieve
    query_embedding = get_embeddings([question])[0]
    chunks = retrieve(query_embedding, top_k=5)

    if not chunks:
        return {
            "intent": intent,
            "answer": "No documents have been ingested yet.",
            "chunks_used": 0
        }

    # Step 3: Pick the right prompt template
    context = "\n\n".join(chunks)
    prompt = PROMPT_TEMPLATES[intent].format(
        context=context,
        question=question
    )

    # Step 4: Generate
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer = response.choices[0].message.content.strip()

    return {
        "intent": intent,
        "answer": answer,
        "chunks_used": len(chunks)
    }