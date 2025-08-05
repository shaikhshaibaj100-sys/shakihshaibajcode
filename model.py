# shakihshaibajcode
#i create a personal ai assistance llike jarvis an nova
import cohere
from rich import print
from dotenv import dotenv_values

# Load API Key from .env
env_vars = dotenv_values('.env')
CohereAPIkey = env_vars.get("CohereAPIkey")
Co = cohere.Client(api_key='hYqwv9L7NOfcgaZ6KUXTCQh6D786Kh6EmjeuJpYo')

# Functional types
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "youtube search", "reminder", "google search", "content",
    "generate image", "system"
]

# History and system preamble
chatHistory = [
    {"role": "user", "message": "how are you?"},
    {"role": "CHATBOT", "message": "general how are you?"},
    {"role": "user", "message": "do you like pizza?"},
    {"role": "CHATBOT", "message": "general do you like pizza?"},
    {"role": "user", "message": "open chrome and tell me about mahatma gandhi.."},
    {"role": "CHATBOT", "message": "open chrome, general tell me about mahatma gandhi.."},
    {"role": "user", "message": "open chrome and open firefox"},
    {"role": "CHATBOT", "message": "open chrome, open firefox"},
    {"role": "user", "message": "what is todays date and remind me I have a dancing performance on 5th aug at 11pm"},
    {"role": "CHATBOT", "message": "general what is todays date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "user", "message": "chat with me..."},
    {"role": "CHATBOT", "message": "general chat with me..."}
]

# Instruction prompt
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general (query)' if a query can be answered by a llm model...
-> Respond with 'realtime (query)' if a query requires up-to-date information...
-> Respond with 'open (application)', 'close (application)', etc. as per user's task.
*** If the query asks to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** Respond with 'exit' if the user says goodbye or ends conversation ***
*** If you can't classify the query, respond with 'general (query)' ***
"""

# Message history for current session (optional)
messages = []

# Main Decision-Making Function
def FirstlayerDMM(prompt: str = "test", depth: int = 0):
    if depth > 3:
        return ["general " + prompt]

    messages.append({"role": "user", "content": prompt})

    # Stream response from Cohere
    stream = Co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=chatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    response_text = ""
    for event in stream:
        if event.event_type == "text-generation":
            response_text += event.text

    # Clean and split response
    response_text = response_text.replace("\n", "")
    raw_tasks = [i.strip() for i in response_text.split(",")]

    # Filter tasks based on known functions
    classified_tasks = []
    for task in raw_tasks:
        for func in funcs:
            if task.startswith(func):
                classified_tasks.append(task)

    # Retry if invalid output
    if any("(query)" in task for task in classified_tasks):
        return FirstlayerDMM(prompt=prompt, depth=depth + 1)

    return classified_tasks


# Run from command line
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ("exit", "quit", "bye"):
            print("exit")
            break
        print(FirstlayerDMM(user_input))
