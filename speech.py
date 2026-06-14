import speech_recognition as sr


def listen():

    r = sr.Recognizer()


    try:

        with sr.Microphone() as source:

            r.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = r.listen(
                source,
                timeout=5
            )


        text = r.recognize_google(
            audio,
            language="hi-IN"
        )


        return text



    except:

        return ""