import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()


genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)



def explain_topic(topic, language, mode):

    prompt = f"""

You are a {mode} AI teacher.

Explain {topic}.

Language rule:
If user asks English, answer only English.
If user asks Hindi, answer only Hindi.
Otherwise use simple Hinglish.

Keep answer between 60-70 words.

Avoid symbols like -, *, #.

Also provide an image keyword.

"""


    response = model.generate_content(prompt)

    answer = response.text


    image = (
        "https://source.unsplash.com/600x400/?"
        + topic.replace(" ","+")
    )


    return answer, image, None




def generate_quiz(topic):

    prompt = f"""

Create a simple quiz about {topic}.

Give:
Question:
Options:
Answer:

"""

    response = model.generate_content(prompt)

    return response.text