import pygame  # For audio playback
import random  # For choosing random responses
import asyncio  # For async TTS operations
import edge_tts  # Edge TTS for text-to-speech
import os  # For file handling
from dotenv import dotenv_values  # For loading environment variables

# Load environment variables from .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # e.g., "en-IN-PrabhatNeural"

# Function to convert text to audio file asynchronously
async def TextToAudioFile(text):
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+13%")
    await communicate.save(file_path)

# Function to manage basic Text-to-Speech playback
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to audio
            asyncio.run(TextToAudioFile(Text))

            # Initialize and play using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if func() is False:
                    break
                pygame.time.Clock().tick(10)

            return True

        except Exception as e:
            print(f"Error in TTS: {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")

# Function to handle longer text and add random responses if needed
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
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

    if len(Data) > 4 and len(Text) >= 250:
        intro = ".".join(Text.split(".")[0:2]) + "."
        TTS(f"{intro} {random.choice(responses)}", func)
    else:
        TTS(Text, func)

# Main Execution Loop
if __name__ == "__main__":
    while True:
        TTS(input("Enter the text: "))
        #call TextToSpeech if you want him to talk less not all
