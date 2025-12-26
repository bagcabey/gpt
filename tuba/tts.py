import pyttsx3


def speak(text: str) -> str:
    """
    Yerel pyttsx3 TTS. Seslendirir ve metni geriye döndürür.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return text
