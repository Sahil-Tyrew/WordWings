# voice.py

import threading
import speech_recognition as sr

_recognizer = sr.Recognizer()
_mic = sr.Microphone()
_keep_recording = False
_recording_thread = None

def _record_loop(callback):
    global _keep_recording
    with _mic as source:
        while _keep_recording:
            audio = _recognizer.listen(source)
            try:
                text = _recognizer.recognize_google(audio)
                callback(text)
            except sr.UnknownValueError:
                continue

def start_recording(callback=lambda txt: print(f"Recognized: {txt}")):
    """
    Launch background thread that captures speech and calls callback(text).
    """
    global _keep_recording, _recording_thread
    if _recording_thread and _recording_thread.is_alive():
        return
    _keep_recording = True
    _recording_thread = threading.Thread(
        target=_record_loop,
        args=(callback,),
        daemon=True
    )
    _recording_thread.start()

def stop_recording():
    """
    Signal recording thread to stop.
    """
    global _keep_recording
    _keep_recording = False
