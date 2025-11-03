# main.py
import threading
import json
import os
import sys
import subprocess as sp
from time import sleep
from asyncio import run as asyncio_run
from dotenv import dotenv_values

# Import integration functions from your GUI module and backend modules.
# NOTE: your original code attempted to import `GraphicalUserInterface` which didn't exist.
# Your GUI file uses `run_app()` as the entrypoint — import that instead.
from .Frontend.Gui import (
    run_app,                 # GUI entrypoint (previously missing GraphicalUserInterface)
    setAssistantStatus,
    ShowTextToScreen,
    TempDirectorypath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifire,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from .Backend.model import FirstlayerDMM
from .Backend.realtimesearchengine import realtimesearchengine
from .Backend.automation import automation
from .Backend.speechtotext import speechRecognition
from .Backend.chatbot import chat_bot
from .Backend.texttospeech import texttospeech

# -----------------------
# Config and globals
# -----------------------
env_vars = dotenv_values(".env")
Username = env_vars.get("USERNAME", "User")
Assistantname = env_vars.get("ASSISTANT", "Assistant")

# Default message shown when chatlog is empty
DefaultMessage = (
    f"{Username}: Hello {Assistantname}, how are you?\n"
    f"{Assistantname}: Welcome {Username}, I am doing well. How can I help you?"
)

DATA_CHATLOG = r"Data\Chatlog.json"
subprocesses = []  # to store child processes started for image generation etc.

# Commands recognized by automation (keep as you had)
Function = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# -----------------------
# Helper functions
# -----------------------
def ensure_chatlog_exists():
    os.makedirs(os.path.dirname(DATA_CHATLOG), exist_ok=True)
    if not os.path.isfile(DATA_CHATLOG):
        with open(DATA_CHATLOG, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

def ShowDefaultChatIfNoChats():
    ensure_chatlog_exists()
    try:
        with open(DATA_CHATLOG, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if len(content) < 5:
                # write blank database and response placeholders to temp dir
                with open(TempDirectorypath("database.data"), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectorypath("response.data"), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except Exception as e:
        print("Error in ShowDefaultChatIfNoChats:", e)

def ReadChatLogJson():
    ensure_chatlog_exists()
    try:
        with open(DATA_CHATLOG, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print("Error reading chatlog json:", e)
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = entry.get("role", "")
        content = entry.get("content", "")
        if role == "user":
            formatted_chatlog += f"{Username}: {content}\n"
        elif role == "assistant":
            formatted_chatlog += f"{Assistantname}: {content}\n"

    # Clean and modify answer text for GUI display
    try:
        modified = AnswerModifier(formatted_chatlog)
    except Exception:
        modified = formatted_chatlog

    try:
        with open(TempDirectorypath("database.data"), "w", encoding='utf-8') as file:
            file.write(modified)
    except Exception as e:
        print("Error writing database.data:", e)

def ShowChatOnGui():
    db_path = TempDirectorypath("database.data")
    resp_path = TempDirectorypath("response.data")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception:
        data = ""

    if data and len(str(data).strip()) > 0:
        # write final result to response.data for GUI to pick up
        try:
            with open(resp_path, "w", encoding="utf-8") as f:
                f.write(data)
        except Exception as e:
            print("Error writing response.data:", e)

def InitialExecution():
    try:
        SetMicrophoneStatus("False")
    except Exception:
        try:
            setAssistantStatus("Avaliable.....")
        except Exception:
            pass

    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGui()

InitialExecution()

# -----------------------
# Main assistant flow
# -----------------------
def mainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImagegenerationQuery = ''

        # update GUI status and get user speech input
        setAssistantStatus("Listening....")
        Query = speechRecognition()
        if not Query:
            return False

        ShowTextToScreen(f"{Username}: {Query}")
        setAssistantStatus("Thinking....")

        decision = FirstlayerDMM(Query)
        print("\nDecision:", decision, "\n")

        # detect presence of general/realtime decisions
        G = any([i for i in decision if i.startswith("general")])
        R = any([i for i in decision if i.startswith("realtime")])

        # Merge queries for "general" or "realtime" items into a single query string
        merged_parts = []
        for i in decision:
            if i.startswith("general") or i.startswith("realtime"):
                # remove prefix word and keep the rest
                parts = i.split(maxsplit=1)
                if len(parts) > 1:
                    merged_parts.append(parts[1])
        Mearged_Query = " and ".join(merged_parts).strip()

        # detect image generation
        for q in decision:
            if "generate" in q:
                ImagegenerationQuery = str(q)
                ImageExecution = True

        # automation tasks
        for q in decision:
            if not TaskExecution:
                if any(q.startswith(func) for func in Function):
                    try:
                        # automation may be synchronous or asynchronous — call accordingly
                        result = automation(list(decision))
                        if hasattr(result, "__await__"):
                            asyncio_run(result)
                        TaskExecution = True
                    except Exception as e:
                        print("Error running automation:", e)
                        TaskExecution = True  # avoid retry loop

        # handle image generation process
        if ImageExecution:
            try:
                img_file = r"C:\pthiin code\Frontend\Files\Imagegeneration.data"
                os.makedirs(os.path.dirname(img_file), exist_ok=True)
                with open(img_file, "w", encoding="utf-8") as file:
                    file.write(f"{ImagegenerationQuery},True")

                p1 = sp.Popen(
                    ["python", r"C:\pthiin code\Backend\Imagegeneration.py"],
                    stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, shell=False
                )
                subprocesses.append(p1)
            except Exception as e:
                print(f"Error starting Imagegeneration.py: {e}")

        # if both general and realtime or realtime only -> realtime path
        if R:
            setAssistantStatus("Searching.....")
            try:
                Answer = realtimesearchengine(QueryModifire(Mearged_Query if Mearged_Query else Query))
            except Exception as e:
                Answer = f"Error while doing realtime search: {e}"
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            setAssistantStatus("Answering.....")
            try:
                texttospeech(Answer)
            except Exception as e:
                print("Error during TTS:", e)
            return True

        # fallback: iterate decision items
        for q in decision:
            if q.startswith("general"):
                setAssistantStatus("Thinking.....")
                # remove 'general' prefix
                QueryFinal = q.replace("general", "", 1).strip()
                Answer = chat_bot(QueryModifire(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                setAssistantStatus("Answering......")
                try:
                    texttospeech(Answer)
                except Exception as e:
                    print("Error during TTS:", e)
                return True

            elif q.startswith("realtime"):
                setAssistantStatus("Searching.....")
                QueryFinal = q.replace("realtime", "", 1).strip()
                Answer = realtimesearchengine(QueryModifire(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                setAssistantStatus("Answering.....")
                try:
                    texttospeech(Answer)
                except Exception as e:
                    print("Error during TTS:", e)
                return True

            elif q == "exit" or "exit" in q:
                QueryFinal = "okay, Bye !!"
                Answer = chat_bot(QueryModifire(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                setAssistantStatus("Answering.....")
                try:
                    texttospeech(Answer)
                except Exception:
                    pass
                os._exit(0)

    except Exception as e:
        print("Unhandled error in mainExecution:", e)
        try:
            setAssistantStatus("Error")
        except Exception:
            pass
    return False

# -----------------------
# Threads: worker + GUI
# -----------------------
def FirstThread():
    # worker loop checks mic status and runs assistant when mic is active
    while True:
        try:
            currentstatus = GetMicrophoneStatus()
        except Exception:
            currentstatus = "False"

        if str(currentstatus).strip().lower() == "true":
            mainExecution()
            # small pause to avoid busy loops
            sleep(0.3)
        else:
            try:
                AIstatus = GetAssistantStatus()
            except Exception:
                AIstatus = ""
            if "Avaliable" in str(AIstatus):
                sleep(0.1)
            else:
                try:
                    setAssistantStatus("Avaliable.....")
                except Exception:
                    pass
            sleep(0.1)

def secondThread():
    # Start your GUI - must run in main thread for PyQt apps.
    # We will call run_app() from Frontend.Gui here.
    try:
        run_app()
    except Exception as e:
        print("Error starting GUI:", e)
        raise

if __name__ == "__main__":
    # Start worker thread (daemon so it won't block program exit)
    worker = threading.Thread(target=FirstThread, daemon=True)
    worker.start()

    # Run GUI in the main thread
    secondThread()
