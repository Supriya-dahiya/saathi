"""
Test script for TTS preprocessing and speech generation.
Verifies that emojis are stripped and audio output is generated.
"""

from tts import speak, clean_text_for_tts, get_tts_audio_bytes

# Test 1: Clean text with various emojis and markdown
sample = "Hello 👩‍🏫! Welcome to class. 🌱 Today we study **Photosynthesis** ☀️. 100% fun! 🚀"
cleaned = clean_text_for_tts(sample)
print("Original:", sample)
print("Cleaned :", cleaned)
assert "👩‍🏫" not in cleaned
assert "🌱" not in cleaned
assert "☀️" not in cleaned
assert "🚀" not in cleaned
assert "Photosynthesis" in cleaned
assert "100%" in cleaned

print("\nEmoji stripping test passed successfully!")

# Test 2: Generate audio for English, Hindi, and Hinglish
for lang, text in [
    ("English", "Welcome to class. Let us learn together."),
    ("Hindi", "नमस्ते विद्यार्थियों, कक्षा में आपका स्वागत है।"),
    ("Hinglish", "Hello students, aaj hum saath mein seekhenge.")
]:
    audio = get_tts_audio_bytes(text, language=lang)
    print(f"Generated {lang} audio: {len(audio)} bytes")
    assert len(audio) > 1000

print("\nAll TTS tests passed!")
