#wordwings_app

#1 ------- Imports First: -----------------------------------------------------------------

import os
import logging
import time
import threading
import json

import tkinter as tk
from tkinter import scrolledtext, ttk, Label, PhotoImage, filedialog, messagebox, END
import tkinter.font as tkfont

from PIL import Image, ImageTk  # PIL used for image processing and OCR

import pyttsx3
from openai import OpenAI

# LIBRARIES FOR WITHOUT AI SIMPLIFY TEXT
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet

# OCR libraries
import pytesseract
# pdf2image is imported inside the OCR function because it is only needed there

# Stretch Feature: Voice Command:
#    # install brew audio
#    # pip install pyaudio
#    # pip install SpeechRecognition
import pyaudio
import speech_recognition as sr

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')

#2. ------ Global Initialization ------------------

# Initialize the TTS engine
engine = pyttsx3.init()

# Initialize logging
logging.basicConfig(level=logging.ERROR)

# Simple dictionary for word replacement
SIMPLE_WORDS_FILE = "simple_words.json"
def load_simple_words():
    try:
        with open(SIMPLE_WORDS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
SIMPLE_WORDS = load_simple_words()

CONFIG_FILE = 'config.ini'

#3. --------------------- Functions --------------------------------------

# Function to simplify text WITH AI
def simplify_text_with_ai(text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OpenAI API Key not found in environment variables.")
        return text
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Simplify complex text for students with dyslexia."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return text

# Function to simplify text WITHOUT AI
def simplify_text(text):
    sentences = sent_tokenize(text)
    simplified_sentences = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        new_words = []
        for w in words:
            lw = w.lower()
            simple = SIMPLE_WORDS.get(lw, w)
            if w.istitle(): simple = simple.capitalize()
            elif w.isupper(): simple = simple.upper()
            new_words.append(simple)
        joined = ' '.join(new_words)
        if len(words) > 15 and ' and ' in joined.lower():
            simplified_sentences.extend(joined.split(' and '))
        else:
            simplified_sentences.append(joined)
    return ' '.join(simplified_sentences)

# Function to update text box with simplified text
def simplify_button_action():
    original = text_box.get("1.0", tk.END).strip()
    if not original: return
    if use_ai_var.get():
        out = simplify_text_with_ai(original)
    else:
        out = simplify_text(original)
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", out)

# Function to read text aloud
def read_aloud():
    text = text_box.get("1.0", tk.END).strip()
    highlight_color = highlight_var.get()
    text_box.tag_configure("highlight", background=highlight_color)
    if text:
        for word in text.split():
            idx = text_box.search(word, "1.0", stopindex=tk.END)
            if idx:
                end = f"{idx}+{len(word)}c"
                text_box.tag_remove("highlight", "1.0", tk.END)
                text_box.tag_add("highlight", idx, end)
                text_box.update()
            engine.say(word)
            engine.runAndWait()
            time.sleep(0.1)
        text_box.tag_remove("highlight", "1.0", tk.END)

# Helper to split text into chunks
def chunk_text(text, max_tokens):
    sentences = sent_tokenize(text)
    chunks = []
    current = ""
    for sent in sentences:
        candidate = (current + " " + sent).strip()
        if len(word_tokenize(candidate)) <= max_tokens:
            current = candidate
        else:
            if current: chunks.append(current)
            if len(word_tokenize(sent)) <= max_tokens:
                current = sent
            else:
                sub = ""
                for w in word_tokenize(sent):
                    if len(word_tokenize((sub + ' ' + w).strip())) <= max_tokens:
                        sub = (sub + ' ' + w).strip()
                    else:
                        chunks.append(sub)
                        sub = w
                if sub: chunks.append(sub)
                current = ""
    if current: chunks.append(current)
    return chunks

def chunk_text_action():
    original = text_box.get("1.0", tk.END).strip()
    if not original: return
    out = "\n\n".join(chunk_text(original, max_tokens=20))
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", out)

# Helper functions for dropdowns
def update_font(text_widget, selected_font):
    """
    Change text_widget’s font, mapping “OpenDyslexic” → “OpenDyslexic3”.
    """
    # 1) grab current size
    curr = text_widget.cget("font").split()
    size = int(curr[1]) if len(curr) > 1 else 14

    # 2) map friendly name to real family
    if selected_font == "OpenDyslexic":
        actual = "OpenDyslexic3"
    else:
        actual = selected_font

    # 3) check it’s installed
    if actual not in tkfont.families():
        messagebox.showwarning(
            "Font not found",
            f"{actual!r} not installed; falling back to Arial."
        )
        actual = "Arial"

    text_widget.configure(font=(actual, size))

def update_color(text_widget, selected_color):
    colors = {"White":"white","Light Blue":"#ADD8E6","Soft Yellow":"#FFFFE0","Pastel Pink":"#FFD1DC"}
    text_widget.configure(bg=colors.get(selected_color,'white'))

# Voice recording setup
CHUNK, FORMAT, CHANNELS, RATE = 1024, pyaudio.paInt16, 1, 44100
class VoiceRecorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.frames=[]; self.is_recording=False; self.thread=None
    def start(self):
        self.frames=[]; self.is_recording=True
        self.stream=self.p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
        self.thread=threading.Thread(target=self._record); self.thread.start()
    def _record(self):
        while self.is_recording:
            data=self.stream.read(CHUNK); self.frames.append(data)
    def stop(self):
        self.is_recording=False; self.thread.join()
        self.stream.stop_stream(); self.stream.close()
        return sr.AudioData(b''.join(self.frames),RATE,self.p.get_sample_size(FORMAT))
recorder = VoiceRecorder()

def start_voice_recording():
    text_box.insert(END,"Voice recording started...\n")
    recorder.start()

def stop_voice_recording():
    text_box.insert(END,"Voice recording stopped.\n")
    audio = recorder.stop()
    recog=sr.Recognizer()
    try:
        cmd=recog.recognize_google(audio)
        text_box.insert(END,f"Recognized: {cmd}\n")
        if "simplify" in cmd.lower(): simplify_button_action()
        elif "read" in cmd.lower(): read_aloud()
    except Exception as e:
        text_box.insert(END,f"Voice error: {e}\n")

# OCR function
from pdf2image import convert_from_path
poppler_path = r"/opt/homebrew/Cellar/poppler/25.04.0/bin"
def image_to_text():
    path=filedialog.askopenfilename(title="Select image/PDF",filetypes=[("Images","*.png *.jpg *.jpeg *.bmp *.tiff"),("PDF","*.pdf")])
    if not path: return
    try:
        text_box.delete("1.0",tk.END)
        if path.lower().endswith('.pdf'):
            pages=convert_from_path(path,300,poppler_path)
            txt=""
            for p in pages:
                p=p.convert('L'); txt+=pytesseract.image_to_string(p,lang='eng')+"\n\n"
            text_box.insert("1.0",txt)
        else:
            img=Image.open(path).convert('L')
            text_box.insert("1.0",pytesseract.image_to_string(img,lang='eng'))
    except Exception as e:
        logging.error(e); messagebox.showerror("OCR Error",str(e))

#6. -------------------------------- GUI Setup and Main Loop -----------------------------------
window=tk.Tk(); window.title("WordWings - Reading Support Tool"); window.geometry("600x500"); window.configure(bg="#f0f8ff")

# Top spacer
tk.Frame(window,bg="#f0f8ff").pack(expand=True,fill="both")
# Logo + tagline
lf=tk.Frame(window,bg="#f0f8ff"); lf.pack(pady=20)
try:
    img=Image.open("scientiae_logo.png").resize((200,100),Image.Resampling.LANCZOS)
    ph=ImageTk.PhotoImage(img); lbl=Label(lf,image=ph,bg="#f0f8ff"); lbl.image=ph; lbl.pack()
except: pass
Label(lf,text="Empowering Readers, One Word at a Time",font=("Arial",14,"italic"),bg="#f0f8ff").pack(pady=5)
# Instruction
Label(window,text="Enter text below:",font=("Arial",12),bg="#f0f8ff").pack()
# Text box
text_box=scrolledtext.ScrolledText(window,wrap=tk.WORD,width=50,height=15,font=("Arial",18),fg="black")
text_box.pack(pady=5,expand=True,fill="both")
# Bottom spacer
tk.Frame(window,bg="#f0f8ff").pack(expand=True,fill="both")
# Controls frame
cf=tk.Frame(window); cf.pack(pady=5)
# Font dropdown
Label(cf,text="Font:").grid(row=0,column=0,padx=5)

font_val=tk.StringVar(value="Arial")
font_menu=ttk.Combobox(cf,textvariable=font_val,values=["Arial","Times New Roman","OpenDyslexic"],state="readonly", width =15)
font_menu.grid(row=0,column=1,padx=5)
#trace to changes apply 
font_val.trace_add(
    "write", 
    lambda *args: update_font(text_box, font_val.get())
)

# Color dropdown
Label(cf,text="Background Color:").grid(row=0,column=2,padx=5)
color_var=tk.StringVar(value="White")
color_menu=ttk.Combobox(cf,textvariable=color_var,values=["White","Light Blue","Soft Yellow","Pastel Pink"],state="readonly")
color_menu.grid(row=0,column=3,padx=5)
color_menu.bind("<<ComboboxSelected>>",lambda e:update_color(text_box,color_var.get()))
# Highlight dropdown
Label(cf,text="Highlight Color:").grid(row=1,column=0,padx=5)
highlight_var=tk.StringVar(value="Yellow")
highlight_menu=ttk.Combobox(cf,textvariable=highlight_var,values=["Yellow","Green","Cyan","Pink"],state="readonly")
highlight_menu.grid(row=1,column=1,padx=5)
# AI checkbox
use_ai_var=tk.BooleanVar(value=False)
tk.Checkbutton(cf,text="Use AI Simplification",variable=use_ai_var).grid(row=1,column=2,columnspan=2,padx=5)
# Buttons frame
bf=tk.Frame(window); bf.pack(pady=5)
for txt,cmd in [("Simplify Text",simplify_button_action),("Read Aloud",read_aloud),("Split Paragraph",chunk_text_action),("Extract Text from Image",image_to_text)]: ttk.Button(bf,text=txt,command=cmd).pack(side="left",padx=5)
# Voice frame
vf=tk.Frame(window,bg="#f0f8ff"); vf.pack(pady=10)
tk.Button(vf,text="Start Voice Recording",command=start_voice_recording).grid(row=0,column=0,padx=5)
tk.Button(vf,text="Stop Voice Recording",command=stop_voice_recording).grid(row=0,column=1,padx=5)
# Main loop
window.mainloop()
