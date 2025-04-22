#wordwings_core

#1 ------- Imports First: -----------------------------------------------------------------

import os
import logging
import time
import threading

import tkinter as tk
from tkinter import scrolledtext, ttk, Label, PhotoImage, filedialog, messagebox, END
import tkinter.font as tkfont

from PIL import Image, ImageTk, Image  # PIL used for image processing and OCR

import pyttsx3
from openai import OpenAI

#LIBRARIES FOR WITHOUT AI SIMPLIFY TEXT
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet

# OCR libraries
import pytesseract
# pdf2image is imported inside the OCR function because it is only needed there
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename


#Stretch Feature: Voice Command:
    #install brew audtio 
    #pip install pyaudio
    #pip install speechrecognization

#first import waht is needed:
import pyaudio
import speech_recognition as sr
#need import tkinter as t and END, but have that in beginning so its okay 


# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Simple dictionary for rule‑based simplification
SIMPLE_WORDS = {
    "inability": "trouble",
    "comprehend": "understand",
    "complicated": "hard",
    "inhibiting": "stopping",
    "academic": "school",
    "progress": "learning",
    "utilize": "use",
    "demonstrate": "show",
    "approximately": "about",
    "significant": "big"
}

def simplify_text(text: str) -> str:
    """Rule‑based simplification using a small dictionary + splitting long sentences."""
    sentences = sent_tokenize(text)
    simplified = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        out = []
        for w in words:
            lw = w.lower()
            sw = SIMPLE_WORDS.get(lw, w)
            # preserve capitalization
            if w.istitle(): sw = sw.capitalize()
            elif w.isupper(): sw = sw.upper()
            out.append(sw)
        joined = " ".join(out)
        # split on 'and' if very long
        if len(words) > 15 and "and" in joined.lower():
            simplified.extend(joined.split(" and "))
        else:
            simplified.append(joined)
    return " ".join(simplified)

def simplify_text_with_ai(text: str) -> str:
    """AI‑based simplification via OpenAI ChatCompletion."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OpenAI API Key not found. Falling back to rule‑based.")
        return simplify_text(text)
    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Simplify complex text for students with dyslexia. Use clear, easy language."},
                {"role": "user", "content": f"Simplify this text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.5
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return simplify_text(text)

def chunk_text(text: str, max_tokens: int = 100) -> list[str]:
    """Split text into chunks of <= max_tokens words, breaking only at sentence boundaries when possible."""
    sentences = sent_tokenize(text)
    chunks, current = [], ""
    for sent in sentences:
        candidate = (current + " " + sent).strip()
        if len(word_tokenize(candidate)) <= max_tokens:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(word_tokenize(sent)) <= max_tokens:
                current = sent
            else:
                # sentence itself too long: split at word
                words = word_tokenize(sent)
                sub = ""
                for w in words:
                    cand2 = (sub + " " + w).strip()
                    if len(word_tokenize(cand2)) <= max_tokens:
                        sub = cand2
                    else:
                        chunks.append(sub)
                        sub = w
                if sub:
                    chunks.append(sub)
                current = ""
    if current:
        chunks.append(current)
    return chunks

def image_to_text(filepath: str) -> str:
    """Perform OCR on an image or PDF file at filepath, returning extracted text."""
    text = ""
    if filepath.lower().endswith(".pdf"):
        pages = convert_from_path(filepath, dpi=300)
        for page in pages:
            page = page.convert("L")
            text += pytesseract.image_to_string(page, lang="eng") + "\n\n"
    else:
        img = pytesseract.image_to_string(filepath, lang="eng")
        text = img
    return text
