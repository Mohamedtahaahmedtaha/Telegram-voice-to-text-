# Telegram Voice-to-Text Bot

This project is a Telegram bot that converts voice messages into text and automatically adds them as cards to a Trello board. It supports both **Arabic and English**.

## Features

- Convert voice messages to text using OpenAI Whisper (local small model or OpenRouter API).
- Automatically add transcribed text to Trello.
- Handles text messages as well.
- Optimized for weak devices using the Whisper small model.
- Medium Whisper model included as a comment for reference for higher accuracy.

## Requirements

- Python 3.10+
- Telegram bot token
- Trello API key, token, and list ID
- FFmpeg installed on your system

## Setup

1. Clone the repository:
    git clone https://github.com/Mohamedtahaahmedtaha/Telegram-voice-to-text-.git
    cd Telegram-voice-to-text- 

2. Create a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install dependencies:
     pip install -r requirements.txt


Then send a voice message or a text message to your Telegram bot. The message will be transcribed and added automatically to your Trello board.

##Notes

If OpenRouter API key is provided, the bot will first try to use the API for transcription.

The local Whisper small model is used for weak devices. The medium model is commented out for reference and can be used for higher accuracy.

