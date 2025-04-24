# -*- mode: python -*-
import os
from PyInstaller.utils.hooks import collect_submodules

# Project root directory (current working directory)
proj_path = os.getcwd()
block_cipher = None

# 1) Analysis: scripts, data files, and hidden imports
a = Analysis(
    ['wordwings_app.py'],
    pathex=[proj_path],
    binaries=[],
    datas=[
        ('scientiae_logo.png', '.'),
        ('simple_words.json', '.'),
        ('config.ini', '.'),
    ],
    hiddenimports=(
        collect_submodules('pdf2image') +
        collect_submodules('pytesseract') +
        collect_submodules('nltk') +
        collect_submodules('openai') +
        collect_submodules('speech_recognition') +
        collect_submodules('pyttsx3') +
        collect_submodules('pyaudio')
    ),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 2) PYZ: package pure Python modules
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# 3) EXE: wrap into a single executable, no console
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WordWings',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/WordWings.icns'
)

# 4) COLLECT: gather exe, libs, and data into one folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='WordWings'
)

# 5) BUNDLE: macOS .app bundle
app = BUNDLE(
    coll,
    name='WordWings.app',
    icon='assets/WordWings.icns', 
    bundle_identifier='com.sahiltyrew.wordwings'
)
