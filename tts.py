"""
Text-to-Speech (TTS) module for saAthI.
Features:
- Unicode emoji and symbol stripping preprocessor (ensures no emojis or descriptions are spoken).
- Multi-language synthesis support (English, Hindi, Hinglish).
- In-memory audio byte stream generation for responsive client-side UI playback controls.
- Safe non-blocking local desktop audio playback.
"""

import io
import os
import re
import tempfile
import threading
import regex
from gtts import gTTS

try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except Exception:
    PLAYSOUND_AVAILABLE = False


def clean_text_for_tts(text: str) -> str:
    """
    Strips Unicode emojis, pictographs, symbols, and markdown markers so TTS
    reads pure spoken natural language without narrating emoji names or symbols.
    The original text remains untouched for visual on-screen display.
    """
    if not text:
        return ""

    # 1. Remove markdown links [text](url) -> keep text only
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # 2. Remove markdown images ![alt](url) -> remove completely
    cleaned = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', cleaned)

    # 3. Remove inline code and code blocks (`code` or ```code```)
    cleaned = re.sub(r'`+[^`]*`+', '', cleaned)

    # 4. Remove markdown headers (#, ##, ###)
    cleaned = re.sub(r'^\s*#+\s*', '', cleaned, flags=re.MULTILINE)

    # 5. Remove bold / italic markers (**text**, *text*, __text__, _text_)
    cleaned = re.sub(r'[*_]{1,3}([^*_\n]+)[*_]{1,3}', r'\1', cleaned)

    # 6. Remove strikethrough (~~text~~)
    cleaned = re.sub(r'~~([^~\n]+)~~', r'\1', cleaned)

    # 7. Remove bullet points and list dashes at the start of lines
    cleaned = re.sub(r'^\s*[-*+]\s+', '', cleaned, flags=re.MULTILINE)

    # 8. Strip keycap emoji sequences (e.g. 1️⃣, 2️⃣, #️⃣)
    cleaned = regex.sub(r'[0-9#*]\uFE0F?\u20E3', '', cleaned)

    # 9. Strip all Unicode emojis, pictographs, and symbols:
    # - Extended Pictographic (\p{Extended_Pictographic})
    # - Emoji Presentation (\p{Emoji_Presentation})
    # - Emoji Modifiers (\p{Emoji_Modifier})
    # - Symbol Other (\p{So}) & Symbol Modifier (\p{Sk})
    # - Variation selectors (\uFE00-\uFE0F) and Zero-Width-Joiner (\u200D)
    # - Regional indicator symbols / Flags (\U0001F1E6-\U0001F1FF)
    # - Miscellaneous symbols & dingbats (\U0001F300-\U0001FAFF, \u2600-\u27BF)
    emoji_pattern = regex.compile(
        r'[\p{Extended_Pictographic}\p{Emoji_Presentation}\p{Emoji_Modifier}\p{So}\p{Sk}'
        r'\uFE00-\uFE0F\u200D\U0001F1E6-\U0001F1FF\U0001F300-\U0001FAFF\u2600-\u27BF]'
    )
    cleaned = emoji_pattern.sub('', cleaned)

    # 10. Clean punctuation spacing (e.g., "word , next" -> "word, next")
    cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned)

    # 11. Normalize spaces and multiple newlines
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)

    return cleaned.strip()


def get_tts_audio_bytes(text: str, language: str = "Hinglish") -> bytes:
    """
    Preprocesses text to exclude emojis and generates MP3 audio bytes using gTTS.
    Configures language and dialect appropriately:
    - Hindi: lang='hi', tld='com'
    - English: lang='en', tld='co.in'
    - Hinglish: lang='en', tld='co.in' (or lang='hi' if Devanagari script detected)
    """
    clean_text = clean_text_for_tts(text)
    if not clean_text:
        return b""

    # Detect if Devanagari script is present (Unicode range U+0900 to U+097F)
    has_devanagari = bool(regex.search(r'[\u0900-\u097F]', clean_text))

    lang_lower = language.lower() if language else "hinglish"

    if "hindi" in lang_lower or lang_lower == "hi" or has_devanagari:
        lang = "hi"
        tld = "com"
    elif "english" in lang_lower or lang_lower == "en":
        lang = "en"
        tld = "co.in"
    else:  # Hinglish / Auto
        if has_devanagari:
            lang = "hi"
            tld = "com"
        else:
            lang = "en"
            tld = "co.in"

    try:
        fp = io.BytesIO()
        tts = gTTS(text=clean_text, lang=lang, tld=tld, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        print(f"[TTS Error] Audio generation failed: {e}")
        return b""


def _play_sound_async(audio_bytes: bytes):
    """Safely plays audio in a non-blocking background thread on the local machine."""
    if not PLAYSOUND_AVAILABLE or not audio_bytes:
        return

    def _worker():
        tmp_file = tempfile.mktemp(suffix=".mp3")
        try:
            with open(tmp_file, "wb") as f:
                f.write(audio_bytes)
            playsound(tmp_file)
        except Exception as err:
            print(f"[TTS Local Play Notice] {err}")
        finally:
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


def speak(text: str, language: str = "Hinglish", play_local: bool = True) -> bytes:
    """
    Main TTS entry point:
    - Strips emojis and symbols before speech synthesis.
    - Generates MP3 audio bytes.
    - Saves to output.mp3 for persistence and cache.
    - Safely plays on local machine speakers if play_local is True.
    - Returns audio bytes for Streamlit st.audio UI playback controls.
    """
    audio_bytes = get_tts_audio_bytes(text, language=language)

    if audio_bytes:
        try:
            with open("output.mp3", "wb") as f:
                f.write(audio_bytes)
        except Exception:
            pass

        if play_local:
            _play_sound_async(audio_bytes)

    return audio_bytes
