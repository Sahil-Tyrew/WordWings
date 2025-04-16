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

#2. ------ Global Initialization ------------------

# Initialize the TTS engine
engine = pyttsx3.init()

# Initialize OpenAI client
#openai.api_key = api_key

# Function to simplify text using OpenAI
logging.basicConfig(level=logging.ERROR) #for logging Errors



#3. --------------------- Functions --------------------------------------


#------------------------------ Text simplification ------------------------------
    #Function to simplify tex WITH AI

'''
keeping the client instantiation inside the function
this approach ensures that the API key is retrieved fresh each time the function is called
'''

def simplify_text_with_ai(text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OpenAI API Key not found in environment variables.")
        return text  # Fallback to rule-based if key is missing
    
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Simplify complex text for students with dyslexia. Keep the language clear and easy to understand."},
                {"role": "user", "content": f"Simplify this text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.5
        )
        simplified_text = response.choices[0].message.content.strip()
        return simplified_text
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return text  # Fallback to original text if API fails


# Simple dictionary for word replacement
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

    # Function to simplify text WITHOUT AI
def simplify_text(text):
    sentences = sent_tokenize(text)
    simplified_sentences = []

    for sentence in sentences:
        words = word_tokenize(sentence)
        simplified_words = []

        for word in words:
            # Convert to lowercase for matching
            word_lower = word.lower()
            # Replace with simpler word if in dictionary, else keep original
            simple_word = SIMPLE_WORDS.get(word_lower, word)
            # Preserve capitalization of original word
            if word.istitle():
                simple_word = simple_word.capitalize()
            elif word.isupper():
                simple_word = simple_word.upper()
            simplified_words.append(simple_word)

        # Rejoin words into a sentence
        simplified_sentence = " ".join(simplified_words)
        # Shorten long sentences (basic rule: split at conjunctions if too long)
        if len(words) > 15 and "and" in simplified_sentence.lower():
            parts = simplified_sentence.split(" and ")
            simplified_sentences.extend(parts)
        else:
            simplified_sentences.append(simplified_sentence)

    return " ".join(simplified_sentences)


    # Function to update text box with simplified text
    #(udated to include AI Toggle)
def simplify_button_action():
    original_text = text_box.get("1.0", tk.END).strip()
    if original_text:
        if use_ai_var.get():
            simplified_text = simplify_text_with_ai(original_text)
        else:
            simplified_text = simplify_text(original_text)  # rule-based method
        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", simplified_text)

# ------------ TTS and Reading Functions -----------
        
    # Function to read text aloud
def read_aloud():
    text = text_box.get("1.0", tk.END).strip()
    words = text.split()  # Split text into words
    highlight_color = highlight_var.get()  # Get the selected highlight color
    text_box.tag_configure("highlight", background=highlight_color)  # Set highlight color dynamically

    if text:
        try:
            index_position = "1.0"  # Start searching from the beginning
            for word in words:
                index_position = text_box.search(word, index_position, stopindex=tk.END, nocase=True, forwards=True)  # Find word position
                if index_position:
                    end_index = f"{index_position}+{len(word)}c"  # Calculate end of the word
                    text_box.tag_remove("highlight", "1.0", tk.END)  # Remove previous highlights
                    text_box.tag_add("highlight", index_position, end_index)  # Highlight the current word
                    text_box.update()  # Refresh UI

                engine.say(word)  # Speak the word
                engine.runAndWait()  # Wait until it's spoken
                time.sleep(0.1)  # Small delay to simulate natural reading pace

            text_box.tag_remove("highlight", "1.0", tk.END)  # Clear highlights after reading
        except Exception as e:
            print(f"Speech synthesis error: {e}")


#------------------------- GUI Customization Functions -----------------------------
            
    # Function to update font
def update_font(*args):
    selected_font = font_val.get()
    available_fonts = tkfont.families()
    print(f"Available fonts: {available_fonts}")
    print(f"Looking for OpenDyslexic: {'OpenDyslexic3' in available_fonts}")
    if selected_font == "OpenDyslexic":
        if "OpenDyslexic3" in available_fonts:
            text_box.configure(font=("OpenDyslexic3", 14))
            print("Applied OpenDyslexic font")
        else:
            text_box.configure(font=("Arial", 14, "bold"))
            print("OpenDyslexic not found, using Arial bold")
    elif selected_font == "Arial":
        text_box.configure(font=("Arial", 14))
    elif selected_font == "Times New Roman":
        text_box.configure(font=("Times New Roman", 14))



    # Function to update background color
def update_color(*args):
    selected_color = color_var.get()
    if selected_color == "White":
        text_box.configure(bg="white")
    elif selected_color == "Light Blue":
        text_box.configure(bg="#ADD8E6")
    elif selected_color == "Soft Yellow":
        text_box.configure(bg="#FFFFE0")
    elif selected_color == "Pastel Pink":
        text_box.configure(bg="#FFD1DC")


#------------------------------ Chunk Text ----------------------------

# The function to chunk long text into smaller parts:
def chunk_text(text, max_tokens):
    """
    Splits `text` into chunks no larger than `max_tokens`.  
    Chunks break only *after* whole sentences when possible;  
    if a single sentence exceeds max_tokens, it’ll be split on word boundaries.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current = ""

    for sent in sentences:
        # try to append this sentence to the current chunk
        candidate = (current + " " + sent).strip()
        if len(word_tokenize(candidate)) <= max_tokens:
            current = candidate
        else:
            # flush what we have so far
            if current:
                chunks.append(current)
            # if this sentence itself is small enough, start a fresh chunk
            if len(word_tokenize(sent)) <= max_tokens:
                current = sent
            else:
                # sentence too big: split on words
                words = word_tokenize(sent)
                sub = ""
                for w in words:
                    if len(word_tokenize((sub + " " + w).strip())) <= max_tokens:
                        sub = (sub + " " + w).strip()
                    else:
                        chunks.append(sub)
                        sub = w
                if sub:
                    chunks.append(sub)
                current = ""
    # append any trailing text
    if current:
        chunks.append(current)

    return chunks


    #Now the function to update the text box with the new smaller parts text:
def chunk_text_action():
    original_text = text_box.get("1.0", tk.END).strip()
    if not original_text:
        return

    # call with the correct keyword and value
    chunks = chunk_text(original_text, max_tokens=20)  # ← change 20 to whatever limit you want

    # join into a single string (with blank lines between chunks)
    output = "\n\n".join(chunks)

    # replace the text box contents
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", output)



'''
This function splits the input text into sentences using NLTK's sent_tokenize.
It goes through the sentences and gets the words using word_tokenize
Adds sentences to a chunk until the combined word count exceeds the max_words limit. 
(keeps adding chunnks and does the same process when the max words limit is reached)

The action function:
calls the function and does that in the text box, replacing the original with the chunked. split version

Then there is a button that is called Split Paragraph for easy understanding that calls the function in the output!
'''



# 4. ------------------------- Class Definition for Voice Recording --------------------------------

    #the function that will read what is spoken through the microphone
    # Define recording settings
    # Rec`ording settings for PyAudio

#Audio Recording Constants       
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100



class VoiceRecorder:
    def __init__(self, rate=RATE, channels=CHANNELS, chunk=CHUNK, format=FORMAT):
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.format = format
        self.frames = []
        self.is_recording = False
        self.thread = None
        self.p = pyaudio.PyAudio()

    def start_recording(self):
        self.frames = []
        self.is_recording = True
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def _record(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk)
                self.frames.append(data)
            except Exception as e:
                print("Error reading audio:", e)
                break

    def stop_recording(self):
        self.is_recording = False
        if self.thread:
            self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        audio_data = b"".join(self.frames)
        sample_width = self.p.get_sample_size(self.format)
        # Note: If you plan on recording again in the same session, do not terminate the PyAudio instance
        # self.p.terminate()
        return sr.AudioData(audio_data, self.rate, sample_width)

# ----- Voice Command Functions ---------------
    
    # Initialize the recorder
recorder = VoiceRecorder()

def start_voice_recording():
    text_box.insert(END, "Voice recording started. Please speak...\n")
    # Start recording using our global recorder instance
    recorder.start_recording()

def stop_voice_recording():
    text_box.insert(END, "Voice recording stopped. Processing audio...\n")
    audio = recorder.stop_recording()
    recognizer = sr.Recognizer()
    try:
        command = recognizer.recognize_google(audio)
        text_box.insert(END, f"Command recognized: {command}\n")
        process_voice_command(command)
    except sr.UnknownValueError:
        text_box.insert(END, "Google Speech Recognition could not understand the audio.\n")
    except sr.RequestError as e:
        text_box.insert(END, f"Could not request results from Google Speech Recognition; {e}\n")

def process_voice_command(command):
    command_lower = command.lower()
    # Add any processing logic you need. For instance:
    if "simplify" in command_lower:
        text_box.insert(END, "Simplify command triggered.\n")
        simplify_button_action()  # Your existing function
    elif "read" in command_lower:
        text_box.insert(END, "Read command triggered.\n")
        read_aloud()  # Your existing function
    else:
        text_box.insert(END, "Voice command not recognized. Try saying 'simplify' or 'read'.\n")


'''
How it works: 
The function that was created uses sr.Microphone() which captures audio and there is a function,
recognizer.listen() with a timeout and phrase limit

The audio that is captured is sent to Google's Speech  service via recognizer.recognize_google(audio)
This translates the audio to text

It takes in the command that is given by the user, i.e. simplify or read, etc. to run the command on the speech that was given

Button is now added to the GUI as well!

'''


#5. ---------------------------OCR Text from Image/PDF Function --------------------------------------

#OCR Features (optical character recognization): 

#The first OCR feature is adding an image and converting it to the text

#function to do the OCR on the image file 

    #pip install pdf2image (for pdf reading)
    #brew install poppler and set the path to your path

def image_to_text():
    """
    Opens a file dialog to select an image or a PDF file for OCR. If an image is selected,
    the image is preprocessed (converted to grayscale) and OCR is performed.
    If a PDF is selected, each page is converted to an image and OCR is performed on each page.
    The extracted text is then inserted into the GUI text box.
    """

    # Import convert_from_path from pdf2image to process PDF files
    from pdf2image import convert_from_path

    #setting poppler path:
    poppler_path = r"/opt/homebrew/Cellar/poppler/25.04.0/bin" #use the path it is downloaded onto


    # Update filetypes to allow PDF uploads along with image files
    file_path = filedialog.askopenfilename(
        title="Select an image or PDF for OCR",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("PDF Files", "*.pdf")
        ]
    )
    
    if file_path:
        try:
            extracted_text = ""
            if file_path.lower().endswith(".pdf"):
                # Convert PDF pages to images (using 300 dpi for good accuracy) and proper poppler path
                pages = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)

                for page in pages:
                    # Convert each page to grayscale (improves OCR performance)
                    page = page.convert('L')
                    # Extract text from the page image using pytesseract
                    page_text = pytesseract.image_to_string(page, lang='eng')
                    extracted_text += page_text + "\n\n"
            else:
                # Process as an image file
                img = Image.open(file_path)
                # Convert image to grayscale for better OCR accuracy
                img = img.convert('L')
                extracted_text = pytesseract.image_to_string(img, lang='eng')
            
            # Clear the text box and insert the extracted text
            text_box.delete("1.0", tk.END)
            text_box.insert("1.0", extracted_text)
        
        except Exception as e:
            logging.error(f"OCR error: {e}")
            messagebox.showerror("OCR Error", f"An error occurred during OCR:\n{e}")


'''
How this function works:
filedialog.askopenfilename function opens a dialog for the user to choose an image file.

Pillow opens the selected image
pytesseract.image_to_string extracts the text
Then the extracted text is pastedd into the GUI
'''



# 6. -------------------------------- GUI Setup and Main Loop -----------------------------------

# Set up the GUI window
window = tk.Tk()
window.title("WordWings - Reading Support Tool")
window.geometry("600x500")
window.configure(bg="#f0f8ff")  # Set a light background color (AliceBlue)



# Create a top spacer to take up extra vertical space
top_spacer = tk.Frame(window, bg="#f0f8ff")
top_spacer.pack(expand=True, fill="both")

# This container holds your logo, tagline, and main content.
container = tk.Frame(window, bg="#f0f8ff")
container.pack()

# Frame for logo and tagline using pack
logo_frame = tk.Frame(window, bg="#f0f8ff")
logo_frame.pack(pady=20)


logo_path = "scientiae_logo.png" 
try:
     
    logo_image = Image.open(logo_path)

    # Optionally, resize the image if needed:
    try:
        resample_method = Image.Resampling.LANCZOS
    except AttributeError:
        resample_method = Image.ANTIALIAS  # for older Pillow versions

    logo_image = logo_image.resize((200, 100), resample_method)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = Label(logo_frame, image=logo_photo, bg="#f0f8ff")
    logo_label.image = logo_photo  # keep a reference
    logo_label.pack()


except Exception as e:
    print("Error loading logo:", e)

# Tagline below the logo
tagline = tk.Label(logo_frame, text="Empowering Readers, One Word at a Time", font=("Arial", 14, "italic"), bg="#f0f8ff", fg="black")
tagline.pack(pady=5)

# Main content frame for the text box, using pack to expand in remaining space

content_frame = tk.Frame(container, bg="#f0f8ff")
content_frame.pack(pady=10)


# Add a label
label = tk.Label(window, text="Enter text below:")
label.pack(pady=5)

# Add a scrollable text box
text_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=15, font=("Arial", 18), fg="black")
text_box.pack(pady=5)
text_box.pack(expand=True, fill="both")

# bottom spacer to take up space
bottom_spacer = tk.Frame(window, bg="#f0f8ff")
bottom_spacer.pack(expand=True, fill="both")

# Frame for customization options
custom_frame = tk.Frame(window)
custom_frame.pack(pady=5)

# Font selection dropdown
font_label = tk.Label(custom_frame, text="Font:")
font_label.grid(row=0, column=0, padx=5)
font_val = tk.StringVar(value="Arial")
font_menu = ttk.Combobox(custom_frame, textvariable=font_val, values=["Arial", "Times New Roman", "OpenDyslexic"], state="readonly")
font_menu.grid(row=0, column=1, padx=5)
font_menu.bind("<<ComboboxSelected>>", update_font)

# Color selection dropdown
color_label = tk.Label(custom_frame, text="Background Color:")
color_label.grid(row=0, column=2, padx=5)
color_var = tk.StringVar(value="White")

color_menu = ttk.Combobox(custom_frame, textvariable=color_var, values=["White", "Light Blue", "Soft Yellow", "Pastel Pink"], state="readonly")
color_menu.grid(row=0, column=3, padx=5)
color_menu.bind("<<ComboboxSelected>>", update_color)

# Buttons frame
button_frame = tk.Frame(window)
button_frame.pack(pady=5)

# Add a simplify button
simplify_button = tk.Button(button_frame, text="Simplify Text", command=simplify_button_action)
simplify_button.grid(row=0, column=0, padx=5)

# Add a read aloud button
read_button = tk.Button(button_frame, text="Read Aloud", command=read_aloud)
read_button.grid(row=0, column=1, padx=5)

# Add Highlight Color Dropdown
highlight_label = tk.Label(custom_frame, text="Highlight Color:")
highlight_label.grid(row=1, column=0, padx=5)

highlight_var = tk.StringVar(value="Yellow")  # Default highlight color
highlight_menu = ttk.Combobox(custom_frame, textvariable=highlight_var, values=["Yellow", "Green", "Cyan", "Pink"], state="readonly")
highlight_menu.grid(row=1, column=1, padx=5)


# GUI IMPLEMENTATION FOR AI BASED SIMPLIFICATION
#ADDS A NEW CHECKBOX in the GUI to run the AI - Based Simplification
use_ai_var = tk.BooleanVar(value=False)  # Default is rule-based
ai_checkbox = tk.Checkbutton(custom_frame, text="Use AI Simplification", variable=use_ai_var)
ai_checkbox.grid(row=1, column=2, padx=5)


#GUI IMPLEMENTATION FOR VOICE COMMAND PROMPT

# GUI IMPLEMENTATION FOR VOICE COMMAND PROMPT
voice_frame = tk.Frame(window, bg="#f0f8ff")
voice_frame.pack(pady=10)

start_voice_btn = tk.Button(voice_frame, text="Start Voice Recording", command=start_voice_recording)
start_voice_btn.grid(row=0, column=0, padx=5)

stop_voice_btn = tk.Button(voice_frame, text="Stop Voice Recording", command=stop_voice_recording)
stop_voice_btn.grid(row=0, column=1, padx=5)


#editing the GUI for adding another button for the chunk text:
chunk_button = tk.Button(button_frame, text="Split Paragraph", command=chunk_text_action)
chunk_button.grid(row=0, column=2, padx=5)


#adding a new button for the Extract Text from Image:

ocr_button = tk.Button(button_frame, text="Extract Text from Image", command=image_to_text)
ocr_button.grid(row=0, column=3, padx=5)




# Start the GUI loop
window.mainloop()



