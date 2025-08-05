import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Assistancevoice = env_vars.get("Assistancevoice", "en-US-GuyNeural 	")  # default fallback

# Async function to convert text to audio file
async def texttoaudiofile(text) -> None:
    file_path = r"data\speech.mp3"

    # Ensure 'data' folder exists
    os.makedirs("data", exist_ok=True)

    # Remove old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate speech
    communicate = edge_tts.Communicate(text, Assistancevoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

# TTS playback with optional stop function
def TTS(text, func=lambda r=None: True):
    try:
        # Convert text to audio file
        asyncio.run(texttoaudiofile(text))

        # Initialize mixer
        pygame.mixer.init()

        # Load and play audio
        pygame.mixer.music.load(r"data\speech.mp3")
        pygame.mixer.music.play()

        # Loop while playing
        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            clock.tick(10)

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            func(False)
            if pygame.mixer.get_init():  # only stop if mixer was initialized
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

# Main speech logic
def texttospeech(text, func=lambda r=None: True):
    data = str(text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # Long response: only speak part and direct to chat
    if len(data) > 4 and len(text) >= 250:
        short_text = ". ".join(data[:2]) + ". " + random.choice(responses)
        TTS(short_text, func)
    else:
        TTS(text, func)

# Run from terminal
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: >>> ")
        texttospeech(user_input)
