from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time
import sys
import speech_recognition 

# Load environment variables
env_vars = dotenv_values(".env")
Inputlanguage = env_vars.get("InputLanguage", "en")

# HTML content with language dynamically injected
HtmlCode ="""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{Inputlanguage}';
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + " ";
            }};

            recognition.onend = function() {{
                recognition.start();  // restart if stopped
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) recognition.stop();
        }}
    </script>
</body>
</html>
"""

# Save HTML file
os.makedirs("date", exist_ok=True)
html_path = os.path.abspath("date/voice.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Set up Chrome options (without headless)
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")  # suppress INFO/WARNING/ERROR logs

# Remove headless mode (important!)
# chrome_options.add_argument("--headless")  ← do NOT use this

# Launch driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Paths
current_dir = os.getcwd()
tempDirpath = os.path.join(current_dir, "frontend", "Files")
os.makedirs(tempDirpath, exist_ok=True)

def setAssistantstatus(status):
    with open(os.path.join(tempDirpath, "status.data"), "w", encoding='utf-8') as file:
        file.write(status)

def QueryModifired(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "can you", "what's", "where's", "how's"]
    if any(word in new_query for word in question_words):
        new_query = new_query.rstrip(".?!") + "?"
    else:
        new_query = new_query.rstrip(".?!") + "."
    return new_query.capitalize()

def UniversalTranslator(text):
    english_translation = mt.translate(text, "en", "auto")
    return english_translation.capitalize()

def speechRecognition():
    driver.get("file:///" + html_path)
    time.sleep(1)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            time.sleep(2)
            text = driver.find_element(By.ID, "output").text.strip()
            if text:
                driver.find_element(By.ID, "end").click()
                if Inputlanguage.lower().startswith("en"):
                    return QueryModifired(text)
                else:
                    setAssistantstatus("translating >>>.....")
                    return QueryModifired(UniversalTranslator(text))
        except Exception:
            continue

if __name__ == "__main__":
    while True:
        result = speechRecognition()
        print(result)
