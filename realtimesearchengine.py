from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")
username = env_vars.get("username", "User")
Assistantname = env_vars.get("Assistant", "Assistant")
GroqAPIkey = env_vars.get("GroqAPIkey")

# Initialize Groq client
client = Groq(api_key='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')

# System prompt
system = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar. ***
*** Just answer the question from the provided data in a professional way. ***"""

# Chatlog path
chatlog_path = os.path.join("Data", "chatlog.json")

# Ensure chatlog file exists
if not os.path.exists("Data"):
    os.makedirs("Data")

if not os.path.isfile(chatlog_path):
    with open(chatlog_path, "w") as f:
        dump([], f)

# Load chat history
with open(chatlog_path, "r") as f:
    messages = load(f)

# Google Search Helper Function
def googlesearch(query):
    try:
        results = list(search(query))  # No unsupported arguments
        answer = f"The search results for '{query}' are:\n[start]\n"
        for idx, url in enumerate(results[:5], 1):
            answer += f"{idx}. {url}\n"
        answer += "[end]"
        return answer
    except Exception as e:
        return f"Error occurred during search: {e}"

# Clean response text
def answermodifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# System instruction messages
systemchatbot = [
    {"role": "system", "content": system},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello sir, how can I help you?"}
]

# Real-time date and time info
def Information():
    now = datetime.datetime.now()
    return (
        f"Use the real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

# Main processing function
def realtimesearchengine(prompt):
    global systemchatbot, messages

    # Reload chat history
    try:
        with open(chatlog_path, "r") as f:
            messages = load(f)
    except:
        messages = []

    # Append Google search results to conversation
    search_results = googlesearch(prompt)
    messages.append({"role": "user", "content": search_results})

    # Get model response
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemchatbot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        # Save updated messages
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

        return answermodifier(answer)

    except Exception as e:
        return f"Error generating response: {e}"

# CLI interface
if __name__ == "__main__":
    while True:
        try:
            prompt = input("Enter your query >>>>>> ")
            if prompt.lower() in ["exit", "quit"]:
                print("Exiting chatbot.")
                break
            print(realtimesearchengine(prompt))
        except KeyboardInterrupt:
            print("\nChat ended by user.")
            break
