# simplifier.py

import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# one‑time downloads; you can remove these after the first run
nltk.download('punkt')
nltk.download('wordnet')

SIMPLE_WORDS_FILE = 'simple_words.json'
try:
    with open(SIMPLE_WORDS_FILE, 'r') as f:
        SIMPLE = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    SIMPLE = {}

def simplify_text(text: str) -> str:
    """
    Rule‑based simplification: replace words per SIMPLE dict,
    split long sentences at 'and' if >15 words.
    """
    sentences = sent_tokenize(text)
    out_sents = []

    for sent in sentences:
        words = word_tokenize(sent)
        new_words = []
        for w in words:
            lw = w.lower()
            simple = SIMPLE.get(lw, w)
            # preserve capitalization
            if w.istitle():
                simple = simple.capitalize()
            elif w.isupper():
                simple = simple.upper()
            new_words.append(simple)

        joined = ' '.join(new_words)
        if len(words) > 15 and ' and ' in joined.lower():
            out_sents.extend(joined.split(' and '))
        else:
            out_sents.append(joined)

    return ' '.join(out_sents)


def simplify_text_with_ai(text: str) -> str:
    """
    GPT‑powered simplification via OpenAI API (fallback to rule‑based on error).
    Requires OPENAI_API_KEY in env.
    """
    from openai import OpenAI
    import os, logging

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY missing; using rule-based fallback.")
        return simplify_text(text)

    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Simplify complex text for students with dyslexia."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.5
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return simplify_text(text)
