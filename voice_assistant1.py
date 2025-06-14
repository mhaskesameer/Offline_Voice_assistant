# === Imports ===
import os
import json
import time
import threading
import difflib
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import pyttsx3
import pyaudio
from vosk import Model, KaldiRecognizer

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "vosk-model-small-en-in-0.4"
MODEL_PATH = os.path.join(BASE_DIR, MODEL_NAME)
LOG_FILE = os.path.join(BASE_DIR, "conversation_log.txt")

# === Dynamic Time Function ===
def get_dynamic_time():
    return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

# === Predefined Text Responses ===
text_responses = {
    "activation": "I'm listening. How can I help you?",
    "goodbye": "Goodbye! Have a great day.",
    "not_found": "I'm not sure I understood that. Could you please repeat?",
    "what is a collaborative robot": "A collaborative robot is designed to work safely and directly with humans.",
    "how is a collaborative robot different from a traditional robot": "Collaborative robots are safer and more interactive than traditional robots.",
    "what is ai": "AI stands for Artificial Intelligence, the simulation of human intelligence by machines.",
    "what is python": "Python is a popular and beginner-friendly programming language.",
    "tell me a joke": "Why did the robot go on vacation? It needed to recharge!",
    "what is robotics": "Robotics is the field focused on designing and building robots.",
    "who made you": "I was created by a developer using Python and Vosk.",
    "what is your name": "I'm your friendly voice assistant. You can call me Echo!",
    "how are you": "I'm functioning at optimal performance. How about you?",
    "what is the time": get_dynamic_time(),
    "who is your favorite superhero": "I admire Iron Man. A genius inventor with a heart of gold.",
    "what's the weather": "I'm not connected to the internet, but I hope it's sunny where you are!",
    "what's your favorite food": "I don't eat food, but I heard cookies are amazing!",
    "do you sleep": "I rest in standby mode, ready to assist you anytime!",
    "sing a song": "La la la! I might not win any awards, but I try my best!",
    "dance": "I would if I had legs. Imagine me doing the robot dance!",
    "what is machine learning": "Machine learning is a subset of AI where systems learn patterns from data to make decisions without being explicitly programmed.",
    "what is deep learning": "Deep learning is a part of machine learning that uses neural networks with many layers to process complex data like images and audio.",
    "what is a neural network": "A neural network is a series of algorithms that mimics the human brain to recognize patterns and solve problems.",
    "what is natural language processing": "Natural Language Processing, or NLP, allows computers to understand, interpret, and respond to human language.",
    "what is reinforcement learning": "Reinforcement learning is a type of machine learning where an agent learns by performing actions and receiving rewards or penalties.",
    "what is supervised learning": "Supervised learning is a machine learning method where the model is trained on labeled data.",
    "what is unsupervised learning": "Unsupervised learning involves finding hidden patterns in data without labeled outputs.",
    "what is autonomous robot": "An autonomous robot can perform tasks and make decisions without human intervention.",
    "what is a humanoid robot": "A humanoid robot is a robot that resembles and mimics human body and behavior.",
    "what is a drone": "A drone is an unmanned aerial vehicle used in surveillance, delivery, photography, and more.",
    "what is computer intelligence": "Computer intelligence refers to the ability of machines to simulate human cognitive processes like learning and reasoning.",
    "what is a robot arm": "A robotic arm is a programmable mechanical device used for picking, placing, or assembling tasks.",
    "what is swarm robotics": "Swarm robotics involves many robots working together as a group, inspired by nature like bees or ants.",
    "what is path planning": "Path planning is the process of determining a route for a robot to reach a target without collisions.",
    "what is slam": "SLAM stands for Simultaneous Localization and Mapping. It helps robots map an unknown environment while keeping track of their location.",
    "what is ros": "ROS stands for Robot Operating System. It's a framework used to write robot software with standard tools and libraries.",
    "what is an industrial robot": "An industrial robot is an automated machine used in factories for manufacturing, welding, assembling, or material handling.",
    "what is ai ethics": "AI ethics deals with the moral implications and responsible use of artificial intelligence."
}

# === Keywords Mapping ===
keywords_dict = {
    "collaborative robot": "what is a collaborative robot",
    "difference": "how is a collaborative robot different from a traditional robot",
    "ai": "what is ai",
    "python": "what is python",
    "joke": "tell me a joke",
    "robotics": "what is robotics",
    "who made you": "who made you",
    "bye": "goodbye", "exit": "goodbye", "quit": "goodbye",
    "name": "what is your name",
    "how are you": "how are you",
    "time": "what is the time",
    "superhero": "who is your favorite superhero",
    "weather": "what's the weather",
    "food": "what's your favorite food",
    "sleep": "do you sleep",
    "sing": "sing a song",
    "dance": "dance",
    "machine learning": "what is machine learning",
    "deep learning": "what is deep learning",
    "neural network": "what is a neural network",
    "nlp": "what is natural language processing",
    "reinforcement": "what is reinforcement learning",
    "supervised": "what is supervised learning",
    "unsupervised": "what is unsupervised learning",
    "autonomous": "what is autonomous robot",
    "humanoid": "what is a humanoid robot",
    "drone": "what is a drone",
    "intelligence": "what is computer intelligence",
    "robot arm": "what is a robot arm",
    "swarm": "what is swarm robotics",
    "path planning": "what is path planning",
    "slam": "what is slam",
    "ros": "what is ros",
    "industrial": "what is an industrial robot",
    "ethics": "what is ai ethics"
}

# === Voice Assistant Core Logic ===
class VoiceAssistant:
    def __init__(self, gui=None):
        self.gui = gui
        self.active_mode = False
        self.running = True
        self.failures = 0
        self.max_failures = 3

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 155)

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

        self.model = Model(MODEL_PATH)
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recognizer = None

    def speak(self, text):
        if self.gui:
            self.gui.update_response(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def log(self, query, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] USER: {query}\n[{timestamp}] ASSISTANT: {response}\n")

    def start_stream(self):
        if not self.stream or not self.stream.is_active():
            self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                                          input=True, frames_per_buffer=8192)
            self.recognizer = KaldiRecognizer(self.model, 16000)

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def listen(self, timeout=6):
        self.start_stream()
        start_time = time.time()
        recognized_text = ""

        if self.gui:
            self.gui.update_status(f"[{self.get_current_time()}] Listening...", "orange")

        while time.time() - start_time < timeout:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                recognized_text = result.get("text", "").strip().lower()
                break

        self.failures += 0 if recognized_text else 1

        if self.gui:
            self.gui.update_status(f"[{self.get_current_time()}] Standby", "green")
            self.gui.update_query(recognized_text or "[No speech detected]")

        return recognized_text

    def find_best_response(self, user_input):
        for keyword, mapped_key in keywords_dict.items():
            if keyword in user_input:
                response = text_responses.get(mapped_key, text_responses["not_found"])
                return response() if callable(response) else response, mapped_key

        matches = difflib.get_close_matches(user_input, text_responses.keys(), n=1, cutoff=0.6)
        if matches:
            response = text_responses[matches[0]]
            return response() if callable(response) else response, matches[0]

        return text_responses["not_found"], "not_found"

    def run(self):
        self.speak("Voice assistant is ready.")

        while self.running:
            if self.gui:
                self.gui.update_status(f"[{self.get_current_time()}] Say 'assistant' to activate...", "green")

            query_text = self.listen()

            if "assistant" in query_text:
                self.speak(text_responses["activation"])
                self.active_mode = True

            while self.active_mode:
                query_text = self.listen(timeout=7)

                if not query_text:
                    if self.failures >= self.max_failures:
                        self.speak("No input detected. Returning to standby.")
                        self.active_mode = False
                    continue

                if any(exit_word in query_text for exit_word in ["bye", "exit", "quit"]):
                    self.speak(text_responses["goodbye"])
                    self.running = False
                    return

                response, key = self.find_best_response(query_text)
                self.speak(response)
                self.log(query_text, response)

        self.stop_stream()
        self.audio.terminate()

# === GUI Interface ===
class AssistantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Offline Voice Assistant")
        self.root.geometry("950x650")
        self.root.configure(bg="#181818")

        self.status_var = tk.StringVar()
        self.query_var = tk.StringVar()
        self.response_var = tk.StringVar()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#181818", foreground="#ffffff")
        style.configure("Header.TLabel", font=("Segoe UI", 22, "bold"), foreground="#00ffaa", background="#181818")

        ttk.Label(self.root, text="Voice Assistant", style="Header.TLabel").pack(pady=20)
        self.create_display("Status:", self.status_var)
        self.create_display("You Said:", self.query_var)
        self.create_display("Response:", self.response_var)

        self.log_area = scrolledtext.ScrolledText(self.root, height=10, wrap=tk.WORD, bg="#111111", fg="#00ff9f",
                                                  font=("Consolas", 11), insertbackground="white")
        self.log_area.pack(padx=25, pady=10, fill='both', expand=True)
        self.log_area.insert(tk.END, "Log initialized...\n")
        self.log_area.config(state='disabled')

        self.status_var.set("Initializing...")
        self.query_var.set("...")
        self.response_var.set("...")

    def create_display(self, title, variable):
        frame = tk.Frame(self.root, bg="#181818")
        frame.pack(padx=30, pady=(15, 10), fill='x')
        ttk.Label(frame, text=title).pack(anchor='w')
        ttk.Label(frame, textvariable=variable, wraplength=900).pack(anchor='w')

    def update_status(self, message, color="white"):
        self.status_var.set(message)
        self.root.update()
        self.append_log(f"[STATUS] {message}")

    def update_query(self, query):
        self.query_var.set(query)
        self.root.update()
        self.append_log(f"[USER] {query}")

    def update_response(self, response):
        self.response_var.set(response)
        self.root.update()
        self.append_log(f"[ASSISTANT] {response}")

    def append_log(self, text):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

    def run(self, assistant):
        thread = threading.Thread(target=assistant.run)
        thread.start()
        self.root.mainloop()

# === Entry Point ===
if __name__ == "__main__":
    gui = AssistantGUI()
    assistant = VoiceAssistant(gui=gui)
    gui.run(assistant)
