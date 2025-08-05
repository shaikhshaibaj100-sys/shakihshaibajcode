from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values('.env')
username = env_vars.get("username")
assistant_name = env_vars.get("Assistantname")
groq_api_key = env_vars.get("GroqAPIkey")  # ✅ Make sure this key is correct in `.env`

# Initialize Groq client
client = Groq(api_key='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')

# Create folder if not exists
os.makedirs("Data", exist_ok=True)

# Path to the chat log
chatlog_path = "Data/Chatlog.json"

# Load or initialize chat messages
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(chatlog_path, "w") as f:
        dump(messages, f)

# Define system behavior message
system_prompt = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {assistant_name} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English an hindi, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

system_chat = [{"role": "system", "content": system_prompt}]

# Real-time system info generator
def real_time_information():
    now = datetime.datetime.now()
    return (
        f"please use this real-time information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : {now.strftime('%M')} minute : {now.strftime('%S')} second.\n"
    )

# Clean blank lines from answer
def answer_modifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Chatbot logic
def chat_bot(query):
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=system_chat + [{"role": "system", "content": real_time_information()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

        return answer_modifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(chatlog_path, "w") as f:
            dump([], f, indent=4)
        return "An error occurred. Chat history has been reset."

# CLI loop
if __name__ == "__main__":
    while True:
        user_input = input("*****Enter your question****: ")
        print(chat_bot(user_input))
