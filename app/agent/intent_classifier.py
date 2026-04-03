from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

VALID_INTENTS = ["summarize", "extract", "answer"]

def classify_intent(question: str) -> str:
    prompt = f"""You are an intent classifier for a document QA system.
Classify the user's question into exactly ONE of these intents:

- summarize: user wants a summary or overview
- extract: user wants specific data pulled out (names, dates, numbers, lists)
- answer: user wants a direct answer to a specific question

Respond with ONLY one word: summarize, extract, or answer.

Question: {question}
Intent:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,        # deterministic — we want consistent classification
        max_tokens=5
    )

    intent = response.choices[0].message.content.strip().lower()

    # Fallback if model returns something unexpected
    return intent if intent in VALID_INTENTS else "answer"