"""
saAthI - Voice-Enabled Teaching Assistant
Multilingual, voice-interactive educational app supporting:
- English, Hindi (हिंदी), and Hinglish with full UI and AI localization.
- Text-to-Speech (TTS) preprocessing that strips emojis for crystal-clear narration.
- Streamlit native audio playback controls (play, pause, scrub, speed, download) across all devices.
- Responsive, modern visual hierarchy, interactive quizzes, and seamless speech/text input.
"""

import streamlit as st
from llm import explain_topic, generate_quiz
from speech import listen
from tts import speak, get_tts_audio_bytes, clean_text_for_tts

# ----------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------
st.set_page_config(
    page_title="saAthI - Voice Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# LOCALIZATION DICTIONARY
# ----------------------------------------------------
LOCALIZATION = {
    "English": {
        "app_title": "saathI",
        "tagline": "Your Intelligent Voice Teaching Assistant",
        "hero_desc": "Empowering learners through voice-first explanations, visual illustrations, and interactive quizzes.",
        "settings_header": "⚙️ Settings & Preferences",
        "mode_label": "Teaching Persona",
        "modes": {
            "Teacher": "👩‍🏫 Teacher Mode (Structured & In-depth)",
            "Student": "👨‍🎓 Student Mode (Fun & Conversational)"
        },
        "mode_badge": "Active Persona",
        "language_label": "Preferred Language",
        "lang_badge": "Active Language",
        "audio_settings_header": "🔊 Audio Controls",
        "autoplay_label": "Auto-narrate answers",
        "play_local_label": "Play on desktop speakers",
        "info_title": "💡 How to interact",
        "info_body": "Click **'🎤 Speak Topic'** to ask with your voice, or type in the chat input below. saAthI will explain with illustrations and audio narration.",
        "speak_btn": "🎤 Speak Topic",
        "listening": "Listening... 🎧 Please speak clearly into your microphone",
        "silence_warning": "Could not detect clear speech. Please check your mic and try again, or type your question below.",
        "thinking": "Formulating educational explanation... 🧠",
        "synthesizing": "Synthesizing voice narration... 🎙️",
        "input_placeholder": "Ask any doubt or topic... (e.g. How does photosynthesis work?)",
        "quick_topics_label": "✨ Quick Topics:",
        "quick_topics": [
            ("Photosynthesis", "Photosynthesis 🌱"),
            ("Water Cycle", "Water Cycle 💧"),
            ("Solar System", "Solar System 🪐"),
            ("Gravity", "Gravity 🍎"),
            ("Human Heart", "Human Heart 🫀"),
            ("Artificial Intelligence", "AI & Robotics 🤖")
        ],
        "audio_player_title": "🎧 Voice Narration (Emoji-Free Audio)",
        "quiz_btn": "📝 Test Yourself with a Quiz",
        "generating_quiz": "Generating interactive quiz... ⏳",
        "quiz_title": "🎯 Knowledge Check",
        "quiz_reveal": "👁️ Reveal Correct Answer & Explanation",
        "replay_btn": "🔁 Replay Voice",
        "clear_btn": "🗑️ Clear Chat History",
        "user_label": "You",
        "assistant_label": "saAthI Assistant",
        "download_audio": "⬇️ Download Audio (.mp3)",
        "empty_chat_prompt": "👋 Welcome! Select a quick topic above, click the microphone, or type below to start learning."
    },
    "Hindi": {
        "app_title": "साथी (saAthI)",
        "tagline": "आपका बुद्धिमान वॉइस शिक्षण सहायक",
        "hero_desc": "आवाज़ और चित्रों के माध्यम से सीखने का एक नया, संवादात्मक और सरल अनुभव।",
        "settings_header": "⚙️ सेटिंग्स एवं प्राथमिकताएं",
        "mode_label": "शिक्षण मोड चुनें",
        "modes": {
            "Teacher": "👩‍🏫 शिक्षक मोड (विस्तृत एवं संरचित)",
            "Student": "👨‍🎓 छात्र मोड (रोचक एवं सरल)"
        },
        "mode_badge": "सक्रिय मोड",
        "language_label": "पसंदीदा भाषा (Preferred Language)",
        "lang_badge": "सक्रिय भाषा",
        "audio_settings_header": "🔊 ऑडियो नियंत्रण",
        "autoplay_label": "उत्तर का स्वतः वाचन (Autoplay)",
        "play_local_label": "सिस्टम स्पीकर पर भी बजाएं",
        "info_title": "💡 उपयोग कैसे करें",
        "info_body": "**'🎤 विषय बोलें'** पर क्लिक करके अपना प्रश्न बोलें, या नीचे दिए गए बॉक्स में टाइप करें। साथी आपको चित्रों और स्पष्ट आवाज़ के साथ समझाएगा।",
        "speak_btn": "🎤 विषय बोलें (Speak)",
        "listening": "सुन रहा हूँ... 🎧 कृपया माइक्रोफ़ोन में स्पष्ट बोलें",
        "silence_warning": "आपकी आवाज़ स्पष्ट नहीं सुनाई दी। कृपया माइक्रोफ़ोन जांचें या नीचे लिखकर पूछें।",
        "thinking": "व्याख्या तैयार की जा रही है... 🧠",
        "synthesizing": "आवाज़ (ऑडियो) तैयार हो रही है... 🎙️",
        "input_placeholder": "कोई भी प्रश्न पूछें... (जैसे: प्रकाश संश्लेषण कैसे काम करता है?)",
        "quick_topics_label": "✨ लोकप्रिय विषय:",
        "quick_topics": [
            ("Photosynthesis", "प्रकाश संश्लेषण 🌱"),
            ("Water Cycle", "जल चक्र 💧"),
            ("Solar System", "सौर मंडल 🪐"),
            ("Gravity", "गुरुत्वाकर्षण 🍎"),
            ("Human Heart", "मानव हृदय 🫀"),
            ("Artificial Intelligence", "एआई और रोबोटिक्स 🤖")
        ],
        "audio_player_title": "🎧 ऑडियो स्पष्टीकरण (इमोजी रहित आवाज़)",
        "quiz_btn": "📝 ज्ञान परीक्षा (क्विज़ शुरू करें)",
        "generating_quiz": "प्रश्नोत्तरी तैयार की जा रही है... ⏳",
        "quiz_title": "🎯 ज्ञान परीक्षा (Quiz)",
        "quiz_reveal": "👁️ सही उत्तर और व्याख्या देखें",
        "replay_btn": "🔁 दोबारा सुनें",
        "clear_btn": "🗑️ चैट इतिहास साफ़ करें",
        "user_label": "आप (Student)",
        "assistant_label": "साथी (saAthI)",
        "download_audio": "⬇️ ऑडियो डाउनलोड करें (.mp3)",
        "empty_chat_prompt": "👋 नमस्ते! ऊपर दिए गए किसी विषय पर क्लिक करें, माइक्रोफ़ोन दबाकर बोलें, या नीचे अपना प्रश्न लिखें।"
    },
    "Hinglish": {
        "app_title": "saAthI",
        "tagline": "Aapka Smart Voice Teaching Assistant",
        "hero_desc": "Voice-first explanations, visual diagrams aur interactive quizzes ke saath seekhein aasani se.",
        "settings_header": "⚙️ Settings & Options",
        "mode_label": "Teaching Mode Chunein",
        "modes": {
            "Teacher": "👩‍🏫 Teacher Mode (Structured & In-depth)",
            "Student": "👨‍🎓 Student Mode (Easy & Friendly)"
        },
        "mode_badge": "Current Mode",
        "language_label": "Language Chunein",
        "lang_badge": "Active Language",
        "audio_settings_header": "🔊 Audio Controls",
        "autoplay_label": "Answers auto-narrate karein",
        "play_local_label": "System speaker par bhi play karein",
        "info_title": "💡 Kaise use karein",
        "info_body": "**'🎤 Topic Boliye'** par click karke sawaal poochhein, ya neeche type karein. saAthI audio narration aur visuals ke saath explain karega.",
        "speak_btn": "🎤 Topic Boliye (Speak)",
        "listening": "Sun raha hoon... 🎧 Mic mein boliye please",
        "silence_warning": "Awaaz sunai nahi di. Mic check karke dobara try karein ya neeche type karein.",
        "thinking": "Explanation tayyar ho raha hai... 🧠",
        "synthesizing": "Voice narration ban raha hai... 🎙️",
        "input_placeholder": "Apna sawaal likhein... (jaise: Photosynthesis kaise hota hai?)",
        "quick_topics_label": "✨ Popular Topics:",
        "quick_topics": [
            ("Photosynthesis", "Photosynthesis 🌱"),
            ("Water Cycle", "Water Cycle 💧"),
            ("Solar System", "Solar System 🪐"),
            ("Gravity", "Gravity 🍎"),
            ("Human Heart", "Human Heart 🫀"),
            ("Artificial Intelligence", "AI & Robotics 🤖")
        ],
        "audio_player_title": "🎧 Voice Explanation (Emoji-Free Narration)",
        "quiz_btn": "📝 Interactive Quiz Shuru Karein",
        "generating_quiz": "Quiz question generate ho raha hai... ⏳",
        "quiz_title": "🎯 Quick Quiz Challenge",
        "quiz_reveal": "👁️ Sahi Answer aur Explanation Dekhein",
        "replay_btn": "🔁 Audio Replay Karein",
        "clear_btn": "🗑️ Chat Clear Karein",
        "user_label": "Aap (User)",
        "assistant_label": "saAthI Assistant",
        "download_audio": "⬇️ MP3 Download Karein",
        "empty_chat_prompt": "👋 Hello! Upar diye kisi topic par click karein, mic dabakar bolein, ya neeche apna doubt type karein."
    }
}

# ----------------------------------------------------
# MODERN UI STYLING (CSS)
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus+Jakarta+Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        max-width: 960px;
    }

    .hero-card {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        border-radius: 20px;
        padding: 24px 30px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.35);
        display: flex;
        align-items: center;
        gap: 24px;
    }
    .hero-logo-box {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 12px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .hero-content h1 {
        color: #ffffff !important;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-content p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.02rem;
        margin: 6px 0 0 0;
        line-height: 1.45;
    }
    .status-badge-row {
        display: flex;
        gap: 10px;
        margin-top: 14px;
        flex-wrap: wrap;
    }
    .status-pill {
        background: rgba(255, 255, 255, 0.22);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #ffffff;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .lang-switcher-card {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }

    .audio-player-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px 18px;
        margin-top: 14px;
        margin-bottom: 8px;
    }
    .audio-player-header {
        font-size: 0.88rem;
        font-weight: 700;
        color: #475569;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .quiz-card {
        background: linear-gradient(135deg, #fefce8 0%, #fffbeb 100%);
        border: 1px solid #fde047;
        border-radius: 16px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 4px 12px rgba(234, 179, 8, 0.12);
    }
    .quiz-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #854d0e;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    @media (max-width: 768px) {
        .hero-card {
            flex-direction: column;
            text-align: center;
            padding: 20px;
        }
        .hero-content h1 {
            font-size: 1.7rem;
        }
        .status-badge-row {
            justify-content: center;
        }
        .lang-switcher-card {
            flex-direction: column;
            align-items: flex-start;
        }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "language" not in st.session_state:
    st.session_state.language = "English"

if "mode" not in st.session_state:
    st.session_state.mode = "Teacher"

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

# Active localization dictionary
cur_lang = st.session_state.language
loc = LOCALIZATION.get(cur_lang, LOCALIZATION["English"])

# ----------------------------------------------------
# SIDEBAR: SETTINGS & CONTROLS
# ----------------------------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=140)

    st.markdown(f"### {loc['settings_header']}")

    # 1. Preferred Language Selector (Synced)
    lang_options = ["English", "Hindi", "Hinglish"]
    lang_labels = {
        "English": "🇺🇸 English",
        "Hindi": "🇮🇳 हिंदी (Hindi)",
        "Hinglish": "🌐 Hinglish (Hindi + English)"
    }
    
    current_lang_idx = lang_options.index(st.session_state.language) if st.session_state.language in lang_options else 0
    
    def on_sidebar_lang_change():
        st.session_state.language = st.session_state.sidebar_lang_selector

    selected_sidebar_lang = st.selectbox(
        loc["language_label"],
        options=lang_options,
        index=current_lang_idx,
        format_func=lambda x: lang_labels.get(x, x),
        key="sidebar_lang_selector",
        on_change=on_sidebar_lang_change
    )

    # 2. Teaching Persona / Mode
    def on_mode_change():
        st.session_state.mode = st.session_state.sidebar_mode_selector

    mode_options = ["Teacher", "Student"]
    current_mode_idx = 0 if st.session_state.mode == "Teacher" else 1

    st.radio(
        loc["mode_label"],
        options=mode_options,
        index=current_mode_idx,
        format_func=lambda m: loc["modes"][m],
        key="sidebar_mode_selector",
        on_change=on_mode_change
    )

    # 3. Audio & Voice Settings
    st.markdown(f"#### {loc['audio_settings_header']}")
    autoplay_enabled = st.checkbox(loc["autoplay_label"], value=True, key="autoplay_audio")
    play_local_speakers = st.checkbox(loc["play_local_label"], value=True, key="play_local_audio")

    # 4. Instructions & Clear Chat
    st.markdown("---")
    st.info(f"**{loc['info_title']}**\n\n{loc['info_body']}")

    if st.session_state.messages:
        if st.button(loc["clear_btn"], use_container_width=True):
            st.session_state.messages = []
            st.session_state.quiz_data = {}
            st.rerun()

# Refresh loc after potential sidebar change
loc = LOCALIZATION.get(st.session_state.language, LOCALIZATION["English"])

# ----------------------------------------------------
# MAIN HEADER & DYNAMIC HERO CARD
# ----------------------------------------------------
mode_badge_text = loc["modes"][st.session_state.mode].split("(")[0].strip()
lang_badge_text = lang_labels.get(st.session_state.language, st.session_state.language)

st.markdown(f"""
<div class="hero-card">
    <div class="hero-logo-box">
        <span style="font-size: 2.6rem;">🎓</span>
    </div>
    <div class="hero-content">
        <h1>{loc['app_title']}</h1>
        <p>{loc['hero_desc']}</p>
        <div class="status-badge-row">
            <span class="status-pill">🌐 {loc['lang_badge']}: <b>{lang_badge_text}</b></span>
            <span class="status-pill">{mode_badge_text}</span>
            <span class="status-pill">🎙️ Voice Ready</span>
            <span class="status-pill">🚫 Emoji-Free Speech</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# PROMINENT MAIN PAGE LANGUAGE SWITCHER
# (Ensures all 3 languages are instantly accessible and functional anywhere)
# ----------------------------------------------------
st.markdown(f"**🌐 {loc['language_label']}:**")
main_lang_col1, main_lang_col2, main_lang_col3 = st.columns(3)

if main_lang_col1.button("🇺🇸 English", type="primary" if st.session_state.language == "English" else "secondary", use_container_width=True):
    st.session_state.language = "English"
    st.rerun()

if main_lang_col2.button("🇮🇳 हिंदी (Hindi)", type="primary" if st.session_state.language == "Hindi" else "secondary", use_container_width=True):
    st.session_state.language = "Hindi"
    st.rerun()

if main_lang_col3.button("🌐 Hinglish", type="primary" if st.session_state.language == "Hinglish" else "secondary", use_container_width=True):
    st.session_state.language = "Hinglish"
    st.rerun()

# ----------------------------------------------------
# QUICK TOPIC PROMPTS
# ----------------------------------------------------
st.markdown(f"**{loc['quick_topics_label']}**")
topic_cols = st.columns(len(loc["quick_topics"]))
triggered_topic = None

for idx, (raw_query, display_label) in enumerate(loc["quick_topics"]):
    if topic_cols[idx].button(display_label, key=f"quick_topic_{idx}", use_container_width=True):
        triggered_topic = raw_query

# ----------------------------------------------------
# VOICE & ACTION TOOLBAR
# ----------------------------------------------------
top_action_col1, top_action_col2 = st.columns([1, 1])

voice_clicked = False
with top_action_col1:
    if st.button(loc["speak_btn"], type="primary", use_container_width=True):
        voice_clicked = True

with top_action_col2:
    if st.session_state.messages:
        last_assistant_msg = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
        if last_assistant_msg and st.button(loc["replay_btn"], use_container_width=True):
            if "audio_bytes" in last_assistant_msg and last_assistant_msg["audio_bytes"]:
                st.audio(last_assistant_msg["audio_bytes"], format="audio/mp3", autoplay=True)
            if play_local_speakers:
                speak(last_assistant_msg["content"], language=st.session_state.language, play_local=True)

# ----------------------------------------------------
# PROCESS INPUT (VOICE OR QUICK TOPIC)
# ----------------------------------------------------
input_query = None

if voice_clicked:
    with st.spinner(loc["listening"]):
        voice_input = listen(language=st.session_state.language)
    if voice_input:
        input_query = voice_input
    else:
        st.warning(loc["silence_warning"])

elif triggered_topic:
    input_query = triggered_topic

# ----------------------------------------------------
# CHAT DISPLAY & MESSAGE HISTORY
# ----------------------------------------------------
if not st.session_state.messages and not input_query:
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px; color: #64748b; background: #f8fafc; border-radius: 16px; border: 1px dashed #cbd5e1; margin-top: 15px;">
        <span style="font-size: 2.2rem;">🎙️</span>
        <h4 style="color: #334155; margin-top: 10px;">{loc['empty_chat_prompt']}</h4>
    </div>
    """, unsafe_allow_html=True)

for m_idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👨‍🎓"):
            st.markdown(f"**{loc['user_label']}**: {msg['content']}")
    else:
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(f"**{loc['assistant_label']}**")
            # Show image if available
            if msg.get("image"):
                st.image(msg["image"], use_container_width=True)

            # Display explanation text (retains emojis on screen)
            st.markdown(msg["content"])

            # Native Audio Player Controls (Play, Pause, Progress scrubber, Speed, Download)
            if msg.get("audio_bytes"):
                st.markdown(f"""
                <div class="audio-player-header">
                    <span>{loc['audio_player_title']}</span>
                </div>
                """, unsafe_allow_html=True)
                # Autoplay only on the newest assistant message if autoplay is enabled
                is_latest_message = (m_idx == len(st.session_state.messages) - 1)
                should_autoplay = autoplay_enabled and is_latest_message
                st.audio(msg["audio_bytes"], format="audio/mp3", autoplay=should_autoplay)

            # Interactive Quiz Section attached to topic
            topic_key = msg.get("topic", "")
            if topic_key:
                quiz_col1, quiz_col2 = st.columns([1, 1])
                with quiz_col1:
                    if st.button(loc["quiz_btn"], key=f"btn_quiz_{m_idx}"):
                        with st.spinner(loc["generating_quiz"]):
                            quiz_content = generate_quiz(
                                topic_key,
                                language=st.session_state.language,
                                mode=st.session_state.mode
                            )
                            st.session_state.quiz_data[topic_key] = quiz_content

                if topic_key in st.session_state.quiz_data:
                    quiz_text = st.session_state.quiz_data[topic_key]
                    st.markdown(f"""
                    <div class="quiz-card">
                        <div class="quiz-header">
                            <span>{loc['quiz_title']} ({topic_key})</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Split quiz text into Question/Options and Answer/Explanation for interactive reveal
                    if "Correct Answer:" in quiz_text or "उत्तर:" in quiz_text:
                        split_marker = "Correct Answer:" if "Correct Answer:" in quiz_text else "उत्तर:"
                        parts = quiz_text.split(split_marker, 1)
                        st.markdown(parts[0].strip())
                        with st.expander(loc["quiz_reveal"], expanded=False):
                            st.markdown(f"**{split_marker}** {parts[1].strip()}")
                    else:
                        st.markdown(quiz_text)

# ----------------------------------------------------
# PROCESS NEW INPUT
# ----------------------------------------------------
typed_query = st.chat_input(loc["input_placeholder"])
query_to_process = input_query or typed_query

if query_to_process:
    # 1. Add User Message
    st.session_state.messages.append({
        "role": "user",
        "content": query_to_process
    })

    # 2. Generate Explanation & Visuals via LLM (Strict language enforcement)
    with st.spinner(loc["thinking"]):
        answer, image, _ = explain_topic(
            query_to_process,
            language=st.session_state.language,
            mode=st.session_state.mode
        )

    # 3. Synthesize Speech Audio (Emojis and symbols strictly stripped)
    with st.spinner(loc["synthesizing"]):
        audio_bytes = get_tts_audio_bytes(answer, language=st.session_state.language)

    # 4. Save to Session State
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "image": image,
        "audio_bytes": audio_bytes,
        "topic": query_to_process
    })

    # 5. Play on local speakers if requested
    if play_local_speakers:
        speak(answer, language=st.session_state.language, play_local=True)

    # Rerun to render new message smoothly
    st.rerun()
