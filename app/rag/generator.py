from groq import Groq
from app.config import GROQ_API_KEY
from typing import List

client = Groq(api_key=GROQ_API_KEY)

def generate_answer(question: str, chunks: List[str]) -> str:
    context = "\n\n".join(chunks)

    prompt = f"""You are a helpful assistant. Answer the question using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find relevant information in the document."

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()