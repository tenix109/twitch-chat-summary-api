# Twitch Chat Summary API

Twitch Chat Summary API is a self-hosted Flask API for streamers to automatically collect, summarize, and save Twitch chat messages during streams.

It includes a built-in Pomodoro timer system to support focused work sessions and structured breaks, automatically summarizing chat at the end of each work session.

---

## Features

- Collects live Twitch chat messages during Pomodoro work sessions
- Summarizes chat using a local Ollama model (Mistral, OpenChat, Zephyr, etc.)
- Speaks the generated summary aloud using Edge TTS
- Saves chat logs, text summaries, and spoken audio files
- Supports customizable work and break session lengths
- Designed to be controlled remotely from a separate streaming PC
- Separates all user configuration into a settings file

---

## Requirements

- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed and running locally
- Microsoft Edge TTS (`edge-tts` Python package)
- Twitch account with OAuth token for chat access

---

## Setup Instructions

1. Clone the repository:
    ```bash
   git clone https://github.com/aaron1127dev/twitch-chat-summary-api.git
   cd twitch-chat-summary-api
   ```

2. Create and activate a virtual environment:
    ```bash
   python3 -m venv venv
   source venv/bin/activate    # Mac/Linux
   venv\Scripts\activate.bat   # Windows
    ```
3. Install required packages:
   pip install -r requirements.txt

4. Configure your settings:
   - Copy `settings_example.py` to `settings.py`
   - Fill in the required fields:
     - `TWITCH_TOKEN`
     - `TWITCH_CHANNEL`
     - `BOT_NICK`
     - `SUMMARIZER_MODEL`
     - `TTS_VOICE`
     - `DEFAULT_WORK_MINUTES`
     - `DEFAULT_BREAK_MINUTES`
     - `PROMPT_TEMPLATE`

5. Run the server:
   python app.py

---

## API Endpoints

| Method | Route                | Description |
|--------|----------------------|-------------|
| GET    | /summary              | Generate and store a chat summary without speaking |
| GET    | /speak                | Speak the latest summary without saving |
| GET    | /finalize             | Speak the latest summary, archive the session (chat log, text summary, MP3), and clear the chat log |
| GET    | /start_pomodoro       | Start a new Pomodoro timer (?minutes=x&mode=work or mode=break). Defaults are configurable |
| GET    | /status               | Check if a Pomodoro timer is active and view time remaining |
| GET    | /clear                | Manually clear the chat log without saving |
| GET    | /play                 | Play the most recent summary audio file |
| GET    | /history              | Returns a list of previous summary sessions (`session-logs`).
| GET    | /history/<timestamp>  | Returns a specific saved summary by timestamp.
---

## Pomodoro Workflow

1. Start a work session:
   GET /start_pomodoro?mode=work

   If no `minutes` parameter is provided, the default from `settings.py` will be used.

2. Chat is collected silently during the work session.

3. When the timer completes:
   - The system automatically summarizes, speaks, saves the session, and clears the chat log.

4. Start a break session:
   GET /start_pomodoro?mode=break

   Break sessions do not clear chat or trigger summarization.

---

## Saved Session Logs

When a session is finalized, a folder is created under `session-logs/` containing:

- chat_log.txt – Raw collected chat messages
- summary.txt – Generated text summary
- summary.mp3 – TTS spoken version of the summary

Example folder structure:

session-logs/
 └── 2025-04-27_00-44/
      ├── chat_log.txt
      ├── summary.txt
      └── summary.mp3

---

## Notes

- Ollama must be running locally before using summarization endpoints.
- Microsoft Edge TTS requires an active internet connection.
- `settings.py` is intentionally ignored by Git for security.
- Only work sessions clear chat and trigger summarization. Break sessions do not.

---

## License

MIT License.

This project is free to use, modify, and distribute.
