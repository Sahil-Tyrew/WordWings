#gui_refractor

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import configparser
import threading

# Text processing
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
nltk.download('punkt')
nltk.download('wordnet')

# Core logic modules
from simplifier import simplify_text, simplify_text_with_ai
from ocr import do_ocr
from voice import start_recording, stop_recording

CONFIG_FILE = 'config.ini'
POPPLER_PATH = r"/opt/homebrew/Cellar/poppler/25.04.0/bin"

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Settings')
        self.resizable(False, False)
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)

        # Default settings
        font_size = self.config.getint('UI', 'font_size', fallback=12)
        line_spacing = self.config.getfloat('UI', 'line_spacing', fallback=1.2)
        theme = self.config.get('UI', 'theme', fallback='light')

        ttk.Label(self, text='Font size:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.font_var = tk.IntVar(value=font_size)
        ttk.Spinbox(self, from_=8, to=32, textvariable=self.font_var, width=5).grid(row=0, column=1, padx=5)

        ttk.Label(self, text='Line spacing:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.spacing_var = tk.DoubleVar(value=line_spacing)
        ttk.Spinbox(self, from_=1.0, to=2.0, increment=0.1, textvariable=self.spacing_var, width=5).grid(row=1, column=1, padx=5)

        ttk.Label(self, text='Theme:').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.theme_var = tk.StringVar(value=theme)
        ttk.OptionMenu(self, self.theme_var, theme, 'light', 'dark').grid(row=2, column=1, padx=5)

        frame = ttk.Frame(self)
        frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text='Save', command=self.save).pack(side='left', padx=5)
        ttk.Button(frame, text='Cancel', command=self.destroy).pack(side='right', padx=5)

    def save(self):
        if 'UI' not in self.config:
            self.config.add_section('UI')
        self.config.set('UI', 'font_size', str(self.font_var.get()))
        self.config.set('UI', 'line_spacing', str(self.spacing_var.get()))
        self.config.set('UI', 'theme', self.theme_var.get())
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)
        messagebox.showinfo('Settings', 'Settings saved. Restart to apply.')
        self.destroy()

class WordWingsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('WordWings')
        self.geometry('800x600')
        self._load_config()
        self._create_menubar()
        self._create_widgets()
        self._bind_shortcuts()

        self.voice_on = False

    def _load_config(self):
        cp = configparser.ConfigParser()
        cp.read(CONFIG_FILE)
        ui = cp['UI'] if 'UI' in cp else {}
        self.font_size = int(ui.get('font_size', 12))
        self.line_spacing = float(ui.get('line_spacing', 1.2))

    def _create_menubar(self):
        menubar = tk.Menu(self)
        fm = tk.Menu(menubar, tearoff=0)
        fm.add_command(label='Open…', accelerator='⌘O', command=self.open_file)
        fm.add_command(label='Save…', accelerator='⌘S', command=self.save_file)
        fm.add_separator()
        fm.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=fm)

        hm = tk.Menu(menubar, tearoff=0)
        hm.add_command(label='Settings', command=self.open_settings)
        hm.add_command(label='About', command=self._show_about)
        menubar.add_cascade(label='Help', menu=hm)

        self.config(menu=menubar)

    def _create_widgets(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text='Settings', command=self.open_settings).pack(side='left', padx=5)
        self.progress = ttk.Progressbar(toolbar, mode='indeterminate')
        self.progress.pack(side='left', padx=5)
        self.status = ttk.Label(toolbar, text='Ready')
        self.status.pack(side='left', padx=5)

        self.text = tk.Text(self, wrap='word', font=(None, self.font_size), spacing3=int(self.line_spacing*10))
        self.text.pack(expand=True, fill='both', padx=10, pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='Simplify', command=self.simplify_text).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Read Aloud', command=self.read_aloud).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Extract Text', command=self.extract_text).pack(side='left', padx=5)

        voice_frame = ttk.Frame(self)
        voice_frame.pack(pady=5)
        ttk.Button(voice_frame, text='Start Recording', command=self.start_voice).pack(side='left', padx=5)
        ttk.Button(voice_frame, text='Stop Recording',  command=self.stop_voice).pack(side='left', padx=5)

    def open_settings(self):
        SettingsDialog(self)

    def _show_about(self):
        messagebox.showinfo('About', 'WordWings v1.0\nA reading support tool. © 2025')

    def open_file(self):
        p = filedialog.askopenfilename(filetypes=[('Text','*.txt'),('All','*.*')])
        if p:
            with open(p) as f:
                self.text.delete('1.0', 'end')
                self.text.insert('1.0', f.read())

    def save_file(self):
        p = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text','*.txt')])
        if p:
            with open(p,'w') as f:
                f.write(self.text.get('1.0','end'))

    def _bind_shortcuts(self):
        for seq,fn in [('<Command-o>',self.open_file),('<Control-o>',self.open_file),('<Command-s>',self.save_file),('<Control-s>',self.save_file),('<Command-e>',self.simplify_text),('<Control-e>',self.simplify_text),('<Command-r>',self.start_voice),('<Control-r>',self.start_voice)]:
            self.bind_all(seq, lambda e,fn=fn: fn())

    def simplify_text(self):
        self.status.config(text='Simplifying...')
        self.progress.start()
        def job():
            txt = self.text.get('1.0','end').strip()
            out = simplify_text_with_ai(txt) if hasattr(self,'use_ai') and self.use_ai.get() else simplify_text(txt)
            self.text.delete('1.0','end')
            self.text.insert('1.0', out)
            self.after(0, lambda: [self.progress.stop(), self.status.config(text='Done')])
        threading.Thread(target=job,daemon=True).start()

    def read_aloud(self):
        from pyttsx3 import init; eng = init()
        for word in self.text.get('1.0','end').split():
            eng.say(word); eng.runAndWait()

    def extract_text(self):
        p = filedialog.askopenfilename(filetypes=[('Images','*.png *.jpg'),('PDF','*.pdf')])
        if not p: return
        try:
            txt = do_ocr(p, POPPLER_PATH)
            self.text.delete('1.0','end')
            self.text.insert('1.0', txt)
        except Exception as e:
            messagebox.showerror('OCR Error', str(e))

    def start_voice(self):
        if not self.voice_on:
            start_recording(callback=lambda t: self.text.insert('end', f"{t}\n"))
            self.voice_on = True

    def stop_voice(self):
        if self.voice_on:
            stop_recording(); self.voice_on=False

if __name__=='__main__':
    app = WordWingsApp()
    app.mainloop()
