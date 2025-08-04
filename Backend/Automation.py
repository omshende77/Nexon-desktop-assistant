import os
import subprocess
import asyncio
import webbrowser
import requests
import keyboard
from webbrowser import open as webopen
from AppOpener import open as appopen, close
from pywhatkit import search, playonyt
from dotenv import dotenv_values 
from bs4 import BeautifulSoup
from rich import print
from groq import Groq

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# HTML class names to look for in web scraping
classes = [
    "zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk bk Fzvlsh YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "Izbrdc", "05uR6d LTKDO", "vlzY6d",
    "webanswers-webanswers_table_webanswers-table", "dDoko Ikb4nh gsrt", "sXLaße",
    "Lukfite", "VQF4g", "qv3wpe", "kno-rdesc", "SPZz6b"
]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# Messages and context for the AI
messages = []

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}
]

def GoogleSearch(Topic):
    search(Topic)
    return True

# GoogleSearch("Batman")

def Content(Topic):
    
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen(['notepad.exe', File])
    
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            messages=SystemChatBot + messages,
            model="llama3-70b-8192",
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
        
    Topic: str = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)
    filename = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()
    OpenNotepad(filename)
    return True

# Content("application for sick leave")

def YouTubeSearch(Topic):
    url = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(url)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"Opened app: {app}")
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a',{'jsname' : 'UWcknb'})
            return [link.get('href') for link in links]

        # Perform Google search
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            print("Failed to retrieve search results.")
            return None

        html = search_google(app)
        if html:
            link = extract_links(html)[0]
            webopen(link)
        return True
    
def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False


def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open"):
            if "open it" in command or "open file" in command:
                continue
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

        elif command.startswith("close"):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

        elif command.startswith("play"):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif command.startswith("content"):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

        elif command.startswith("google search"):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))

        elif command.startswith("youtube search"):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))

        elif command.startswith("system"):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"No Function Found For: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    pass
    