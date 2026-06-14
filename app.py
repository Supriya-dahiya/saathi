import streamlit as st
from llm import explain_topic, generate_quiz
from speech import listen
from tts import speak
import time


st.set_page_config(
    page_title="saAthI",
    page_icon="🎓",
    layout="wide"
)


# --------------------
# SESSION STORAGE
# --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_audio" not in st.session_state:
    st.session_state.last_audio = ""



# --------------------
# LOGO
# --------------------

st.image(
    "assets/logo.png",
    width=250
)

st.title("saathi")
st.subheader("Your Voice Teaching Assistant")



# --------------------
# SIDEBAR
# --------------------

with st.sidebar:

    st.header("⚙️ Settings")


    mode = st.radio(
        "Select Mode",
        [
            "👩‍🏫 Teacher Mode",
            "👨‍🎓 Student Mode"
        ]
    )


    language = st.selectbox(
        "Preferred Language",
        [
            "Auto",
            "English",
            "Hindi",
            "Hinglish"
        ]
    )


    st.info(
        "Speak your doubt and saAthI will explain it."
    )



# --------------------
# CHAT DISPLAY
# --------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])



# --------------------
# VOICE INPUT
# --------------------

if st.button("🎤 Speak Topic"):


    with st.spinner("Listening... 🎧"):

        topic = listen()


    if topic == "":

        st.warning(
            "I could not hear you. Please try again."
        )


    else:

        st.session_state.messages.append(
            {
                "role":"user",
                "content":topic
            }
        )


        with st.spinner("Thinking..."):

            answer, image, quiz = explain_topic(
                topic,
                language,
                mode
            )


        st.session_state.messages.append(
            {
                "role":"assistant",
                "content":answer
            }
        )


        st.image(image)


        st.write(answer)


        speak(answer)



        if st.button("📝 Start Quiz"):

            quiz_text = generate_quiz(topic)

            st.write(quiz_text)

            speak(quiz_text)




# --------------------
# TEXT INPUT
# --------------------


question = st.chat_input(
    "Type your question..."
)


if question:


    st.session_state.messages.append(
        {
        "role":"user",
        "content":question
        }
    )


    answer, image, quiz = explain_topic(
        question,
        language,
        mode
    )


    st.session_state.messages.append(
        {
        "role":"assistant",
        "content":answer
        }
    )


    st.image(image)

    st.write(answer)

    speak(answer)



# --------------------
# REPLAY
# --------------------

if st.session_state.messages:

    if st.button("🔁 Replay"):

        speak(
            st.session_state.messages[-1]["content"]
        )