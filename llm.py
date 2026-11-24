"""
LLM module for saAthI - Voice Teaching Assistant.
Integrates with Google Gemini API to generate pedagogical explanations,
multilingual content (English, Hindi, Hinglish), educational visuals, and quizzes.
Uses strict system instructions to guarantee full language adherence across all three languages.
"""

import os
import urllib.parse
import requests
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

# Load API key from .env file
env_path = find_dotenv(usecwd=True)
if not env_path or not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def get_image(topic: str) -> str:
    """
    Fetches an authentic educational visual for the given topic:
    1. First queries the Wikipedia API for authentic diagrams / images from Wikimedia Commons.
    2. Falls back to Pollinations AI educational prompt if no Wikipedia thumbnail exists.
    """
    clean_topic = topic.strip().title()

    # 1. Try Wikipedia Summary API
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_topic)}"
        headers = {"User-Agent": "SaathiEducationalAssistant/2.0 (educational_teaching_bot)"}
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            if "thumbnail" in data and "source" in data["thumbnail"]:
                return data["thumbnail"]["source"]
    except Exception:
        pass

    # 2. High-quality educational illustration fallback
    query = urllib.parse.quote(f"{topic} educational science concept diagram illustration high quality")
    return f"https://image.pollinations.ai/prompt/{query}?width=600&height=400&nologo=true"


def explain_topic(topic: str, language: str = "Hinglish", mode: str = "Teacher"):
    """
    Generates an educational explanation strictly adhering to the selected language and mode.

    Languages:
    - English: 100% fluent, natural English with emojis.
    - Hindi: 100% pure Hindi in Devanagari script (हिंदी लिपि) with emojis.
    - Hinglish: Conversational Hindi written in Roman/Latin alphabet with English terms and emojis.

    Modes:
    - Teacher Mode: Encouraging, structured, pedagogical breakdown with real-life examples.
    - Student Mode: Relatable peer-to-peer study buddy, intuitive everyday analogies.
    """
    clean_mode = "Teacher" if "teacher" in mode.lower() else "Student"
    lang_lower = language.lower() if language else "hinglish"

    # Strict language system instructions
    if "english" in lang_lower or lang_lower == "en":
        target_lang = "English"
        sys_instruction = (
            "You are saAthI, a world-class AI Teacher. "
            "CRITICAL MANDATORY LANGUAGE RULE: You must write your ENTIRE explanation strictly in English. "
            "Do NOT include any Hindi or Romanized Hindi words, regardless of the language of the topic or query. "
            "Use clear formatting and friendly emojis for visual reading on screen, but do not describe the emojis in words."
        )
    elif "hindi" in lang_lower or lang_lower == "hi":
        target_lang = "Hindi"
        sys_instruction = (
            "You are saAthI, a world-class AI Teacher. "
            "CRITICAL MANDATORY LANGUAGE RULE: You must write your ENTIRE explanation strictly in pure Hindi using Devanagari script (हिंदी भाषा - देवनागरी लिपि). "
            "Do NOT use English sentences or Roman script, even if the topic is asked in English. "
            "Key technical terms may have English in parentheses (e.g. प्रकाश संश्लेषण (Photosynthesis)). "
            "Use clear formatting and friendly emojis for visual reading on screen, but do not describe the emojis in words."
        )
    else:  # Hinglish
        target_lang = "Hinglish"
        sys_instruction = (
            "You are saAthI, a world-class AI Teacher. "
            "CRITICAL MANDATORY LANGUAGE RULE: You must write your ENTIRE explanation in conversational Hinglish "
            "(Hindi written in the Roman/English alphabet, blended with English technical terms). "
            "Example style: 'Photosynthesis ek aisi biological process hai jisme plants sunlight, water aur carbon dioxide use karke apna food banate hain...' "
            "Do NOT write in Devanagari script for Hinglish mode. "
            "Use clear formatting and friendly emojis for visual reading on screen, but do not describe the emojis in words."
        )

    if clean_mode == "Teacher":
        persona = "Adopt an encouraging, knowledgeable Teacher persona with structured points and real-world applications."
    else:
        persona = "Adopt an enthusiastic, friendly Study Buddy (Student Mode) persona using simple analogies and fun comparisons."

    user_prompt = f"""Persona: {persona}
Topic: {topic}
Required Output Language: {target_lang}

Please explain '{topic}' clearly in around 75 to 100 words.
Keep it structured, engaging, and easy to understand when read or listened to.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=sys_instruction)
        response = model.generate_content(user_prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = f"I encountered an error generating the explanation: {str(e)}"

    image = get_image(topic)
    return answer, image, None


def generate_quiz(topic: str, language: str = "Hinglish", mode: str = "Teacher"):
    """
    Generates a localized interactive quiz question strictly adhering to the requested language.
    """
    lang_lower = language.lower() if language else "hinglish"

    if "english" in lang_lower or lang_lower == "en":
        target_lang = "English"
        sys_instruction = (
            "You are saAthI AI Teaching Assistant. Generate the entire quiz strictly in English. "
            "Do NOT use Hindi."
        )
    elif "hindi" in lang_lower or lang_lower == "hi":
        target_lang = "Hindi"
        sys_instruction = (
            "You are saAthI AI Teaching Assistant. Generate the entire quiz strictly in authentic Hindi using Devanagari script (हिंदी देवनागरी लिपि). "
            "Do NOT use English sentences."
        )
    else:
        target_lang = "Hinglish"
        sys_instruction = (
            "You are saAthI AI Teaching Assistant. Generate the entire quiz in natural conversational Hinglish (Hindi written in Roman/English alphabet with English technical terms). "
            "Do NOT use Devanagari script."
        )

    prompt = f"""Create a fun, interactive 1-question multiple-choice quiz about: {topic}
Required Language: {target_lang}

Format strictly as:
Question: [Question text with a relevant emoji]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Correct Answer: [Letter and option text]
Explanation: [1-2 sentences explaining why]
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=sys_instruction)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Unable to generate quiz at this time: {str(e)}"
