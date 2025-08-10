from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIkey = env_vars.get("GroqAPIKey")

# Classes for Google search scraping
classes = [
    'zCubwf', 'hgkElc', 'LTKOO sY7ric', 'Z0LcW', 'gsrt vk_bk FzvWSb YwPhnf', 'pclqee',
    'tw-Data-text tw-Data-small tw-ta', 'IZ6rdc', 'OSuR6d', 'LTKOO', 'vlzY6d',
    'webanswers-webansers-table__webanswers-table', 'dDoNo ikb48b gsrt', 'sXLaDe',
    'LWkfKe', 'VQF4g', 'qv3Wpe', 'kno-rdesc', 'SPZz6b'
]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'

# Initialize Groq client
client = Groq(api_key='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')

professional_response = [
    "Your satisfaction is my top priority; feel free to ask for any changes or additional information.",
    "I am at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []
systemchatbot = [{
    'role': 'system',
    'content': f'Hello, I am {os.environ.get("Username", "User")}, you are a content writer. You have to write content like a letter.'
}]

# Google Search
def GoogleSearch(topic):
    search(topic)
    return True

# Open Notepad with a file
def openNotepad(File):
    default_text_editor = 'notepad.exe'
    subprocess.Popen([default_text_editor, File])

# Content Writer using Groq API
def ContentWriter(prompt):
    messages.append({'role': 'user', 'content': prompt})

    completion = client.chat.completions.create(
        model='mixtral-8x7b-instruct-v0.1',
        messages=systemchatbot + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None,
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.replace('</s>', "")
    messages.append({"role": "assistant", "content": Answer})
    return Answer

# Save AI content to file
def Content(topic):
    topic_clean = topic.replace("content", "").strip()
    content_by_ai = ContentWriter(topic_clean)

    file_path = rf"Data\{topic_clean.lower().replace(' ', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)

    openNotepad(file_path)
    return True

# YouTube search
def Youtubesearch(topic):
    Url4Search = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(Url4Search)
    return True

# Play YouTube video
def playYoutube(query):
    playonyt(query)
    return True

# Open an app, fallback to Google search if not found
def openApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to fetch search results!")
                return None

        html = search_google(app)
        if html:
            links = extract_links(html)
            for link in links:
                webopen(link)
        return False

# Close an app
def closeApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

# System commands
def system(command):
    def mute():
        keyboard.press_and_release('volume mute')

    def unmute():
        keyboard.press_and_release('volume mute')

    def volume_up():
        keyboard.press_and_release('volume up')

    def volume_down():
        keyboard.press_and_release('volume down')

    if command == 'mute':
        mute()
    elif command == 'unmute':
        unmute()
    elif command == 'volume up':
        volume_up()
    elif command == 'volume down':
        volume_down()

    return True

# Command translator & executor
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith('open'):
            fun = asyncio.to_thread(openApp, command.removeprefix('open').strip())
            funcs.append(fun)

        elif command.startswith('close'):
            fun = asyncio.to_thread(closeApp, command.removeprefix('close').strip())
            funcs.append(fun)

        elif command.startswith('play'):
            fun = asyncio.to_thread(playYoutube, command.removeprefix('play').strip())
            funcs.append(fun)

        elif command.startswith('content'):
            fun = asyncio.to_thread(Content, command.removeprefix('content').strip())
            funcs.append(fun)

        elif command.startswith('google search'):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix('google search').strip())
            funcs.append(fun)

        elif command.startswith('youtube search'):
            fun = asyncio.to_thread(Youtubesearch, command.removeprefix('youtube search').strip())
            funcs.append(fun)

        elif command.startswith('system'):
            fun = asyncio.to_thread(system, command.removeprefix('system').strip())
            funcs.append(fun)

        else:
            print(f"No function found for {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Automation runner
async def automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


#if __name__=="__main__":
 #   asyncio.run(automation(['open Notepad','play saiyaara']))
