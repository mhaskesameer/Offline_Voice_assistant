# Offline Voice Assistant using Vosk

This is an offline voice assistant built using Python, Vosk speech recognition, and Tkinter GUI.

## 🔧 Features
- Offline speech-to-text using Vosk
- Dynamic voice responses via pyttsx3
- GUI interface built with Tkinter
- Logs all interactions
- Fun and educational Q&A on AI, robotics, and Python

## 🛠 Requirements
- Python 3.8 to 3.11
- Dependencies: `pip install -r requirements.txt`
- Vosk model: `vosk-model-small-en-in-0.4`

## 🚀 Setup

```bash
git clone https://github.com/yourusername/OfflineVoiceAssistant.git
cd OfflineVoiceAssistant

# Download the Vosk model:
# https://alphacephei.com/vosk/models
# Extract and place the folder `vosk-model-small-en-in-0.4` here.

# Install dependencies
pip install -r requirements.txt

# Run the assistant
python assistant.py
