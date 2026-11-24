"""
Speech-to-Text (STT) module for saAthI.
Listens to microphone input and converts it to text using Google Speech Recognition
with localized acoustic models for English, Hindi, and Hinglish.
"""

import speech_recognition as sr


def listen(language: str = "Hinglish") -> str:
    """
    Captures voice input from the user's microphone and converts it to text.
    Configures language-specific recognition models:
    - English: 'en-IN' (Indian English accent recognition)
    - Hindi: 'hi-IN' (Devanagari Hindi recognition)
    - Hinglish: 'hi-IN' (Recognizes Hindi and English bilingual speech)
    """
    r = sr.Recognizer()

    # Determine speech recognition language code
    lang_lower = language.lower() if language else "hinglish"
    if "english" in lang_lower or lang_lower == "en":
        recog_lang = "en-IN"
    elif "hindi" in lang_lower or lang_lower == "hi":
        recog_lang = "hi-IN"
    else:  # Hinglish / Auto
        recog_lang = "hi-IN"

    try:
        with sr.Microphone() as source:
            # Calibrate for ambient room noise
            r.adjust_for_ambient_noise(source, duration=0.8)
            # Listen with reasonable timeout and phrase limit
            audio = r.listen(source, timeout=6, phrase_time_limit=12)

        text = r.recognize_google(audio, language=recog_lang)
        return text.strip()

    except (sr.WaitTimeoutError, sr.UnknownValueError):
        # Microphone did not detect intelligible speech
        return ""
    except Exception as e:
        print(f"[SpeechRecognition Notice] {e}")
        return ""
