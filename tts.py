from gtts import gTTS
from playsound import playsound
import tempfile
import os


def speak(text):

    filename = tempfile.mktemp(
        ".mp3"
    )


    tts = gTTS(
        text=text,
        slow=False
    )


    tts.save(filename)


    playsound(filename)


    os.remove(filename)