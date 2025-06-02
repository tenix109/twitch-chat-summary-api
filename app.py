from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import threading
import shutil
import time
from twitchio.ext import commands
import asyncio
import subprocess
import edge_tts
from datetime import datetime
import os
import re
from settings import *
from pomodoro import PomodoroTimer
from utils import SafeDict


pomodoro_timer = PomodoroTimer()
def timer_monitor():
    while True:
        time.sleep(5)
        if pomodoro_timer.is_done():
            if pomodoro_timer.mode == "work":
                print("Work session complete! Finalizing...")
                with app.test_client() as client:
                    client.get('/finalize')
            elif pomodoro_timer.mode == "break":
                print("Break session complete! No finalization needed.")
            pomodoro_timer.reset()


# ---------------------------
# Flask App Setup
# ---------------------------
app = Flask(__name__)
CORS(app)
chat_log = []

class TwitchChatBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        if message.author.name.lower() in EXCLUDED_USERS:
            return
        chat_log.append(f"{message.author.name}: {message.content}")

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = TwitchChatBot()
    loop.run_until_complete(bot.run())

async def speak_summary(text):
    cleaned_text = clean_text_for_tts(text)
    cleaned_text = cleaned_text.replace("- ", "• ").replace("\n", "\n\n")
    communicate = edge_tts.Communicate(cleaned_text, voice=TTS_VOICE)
    await communicate.save("summary.mp3")



def save_session(chat_log, summary_text):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    session_dir = f"session-logs/{timestamp}"
    os.makedirs(session_dir, exist_ok=True)

    with open(f"{session_dir}/chat_log.txt", "w") as f:
        f.write("\n".join(chat_log))

    with open(f"{session_dir}/summary.txt", "w") as f:
        f.write(summary_text)

    if os.path.exists("summary.mp3"):
        shutil.copy("summary.mp3", f"{session_dir}/summary.mp3")

def clean_text_for_tts(text):
    text = text.replace("\\_", "_")
    text = text.replace("_", " ")
    return text

# ---------------------------
# Flask Routes
# ---------------------------

@app.route('/start_pomodoro')
def start_pomodoro():
    mode = request.args.get("mode", "work")  # default to work

    # If minutes is provided in URL, use it. Otherwise fallback to defaults based on mode
    minutes = request.args.get("minutes")
    if minutes:
        minutes = int(minutes)
    else:
        minutes = DEFAULT_WORK_MINUTES if mode == "work" else DEFAULT_BREAK_MINUTES

    if mode == "work":
        chat_log.clear()

    pomodoro_timer.start(minutes, mode)
    return jsonify({'message': f'{mode.capitalize()} session started for {minutes} minutes.'})

@app.route('/status')
def status():
    if pomodoro_timer.active:
        minutes_left = int(pomodoro_timer.time_left() // 60)
        seconds_left = int(pomodoro_timer.time_left() % 60)
        mode = pomodoro_timer.mode
        return jsonify({'status': 'active', 'mode': f'{mode}', 'time_left': f'{minutes_left:02}:{seconds_left:02}'
})
    else:
        return jsonify({'status': 'inactive'})

@app.route('/end_pomodoro')
def end_pomodoro():
    if pomodoro_timer.active:
        pomodoro_timer.reset()
        # After ending, trigger summarize + speak + save
        # Simulate calling finalize route
        with app.test_client() as client:
            client.get('/finalize')
        return jsonify({'message': 'Pomodoro ended early and finalized.'})
    else:
        return jsonify({'message': 'No active pomodoro.'})



@app.route('/summary')
def get_summary():
    if not chat_log:
        # Fallback to latest_summary if it exists
        if os.path.exists("latest_summary.txt"):
            with open("latest_summary.txt", "r") as f:
                summary = f.read()
            return jsonify({'summary': summary})
        else:
            return jsonify({'summary': 'No chat to summarize yet, and no previous summary available.'})
    
    chat_text = "\n".join(chat_log[-100:])
    prompt = PROMPT_TEMPLATE.format_map(SafeDict({
        "twitch_channel": TWITCH_CHANNEL,
        "chat_text": chat_text,
    }))

    try:
        result = subprocess.run(
            ['ollama', 'run', SUMMARIZER_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        summary = result.stdout.strip()
        if not summary:
            summary = "(No response from Ollama)"

        # Save the summary to a file
        with open("latest_summary.txt", "w") as f:
            f.write(summary)

    except Exception as e:
        summary = f"Error during summarization: {e}"
    
    return jsonify({'summary': summary})

@app.route('/speak')
def speak_latest_summary():
    if not os.path.exists("latest_summary.txt"):
        return jsonify({'message': 'No summary available to speak.'}), 404

    with open("latest_summary.txt", "r") as f:
        summary = f.read()

    asyncio.run(speak_summary(summary))
    return jsonify({'message': 'Summary spoken (but not saved).'})

@app.route('/finalize')
def finalize_summary():
    if not os.path.exists("latest_summary.txt"):
        return jsonify({'message': 'No summary available to finalize.'}), 404

    if chat_log:
        # Only if chat exists, regenerate summary and save
        chat_text = "\n".join(chat_log[-100:])
        prompt = PROMPT_TEMPLATE.format_map(SafeDict({
            "twitch_channel": TWITCH_CHANNEL,
            "chat_text": chat_text,
        }))

        try:
            result = subprocess.run(
                ['ollama', 'run', SUMMARIZER_MODEL],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60
            )
            summary = result.stdout.strip()
            if not summary:
                summary = "(No response from Ollama)"
        except Exception as e:
            summary = f"Error during summarization: {e}"

        with open("latest_summary.txt", "w") as f:
            f.write(summary)

        asyncio.run(speak_summary(summary))
        save_session(chat_log, summary)
        chat_log.clear()

        return jsonify({'message': 'New summary generated, spoken, and session saved.'})

    else:
        # No new chat, just reuse previous summary
        with open("latest_summary.txt", "r") as f:
            summary = f.read()
        asyncio.run(speak_summary(summary))
        return jsonify({'message': 'No new chat. Reusing latest summary.\n' + summary})

@app.route('/play')
def play_audio():
    if not os.path.exists("summary.mp3"):
        return jsonify({"message": "No summary audio available."}), 404
    return send_file("summary.mp3", mimetype="audio/mpeg")

@app.route('/clear')
def clear_chat():
    chat_log.clear()
    return jsonify({'message': 'Chat log cleared.'})

@app.route('/history')
def list_history():
    log_dir = "session-logs"
    if not os.path.exists(log_dir):
        return jsonify([])

    sessions = []
    for name in sorted(os.listdir(log_dir), reverse=True):
        summary_path = os.path.join(log_dir, name, "summary.txt")
        if os.path.isfile(summary_path):
            sessions.append({
                "timestamp": name,
                "path": f"/history/{name}"
            })

    return jsonify(sessions)

@app.route('/history/<timestamp>')
def get_past_summary(timestamp):
    summary_path = os.path.join("session-logs", timestamp, "summary.txt")
    if os.path.isfile(summary_path):
        with open(summary_path, "r") as f:
            return jsonify({"summary": f.read()})
    return jsonify({"summary": "Summary not found."}), 404

# ---------------------------
# Run Everything
# ---------------------------
if __name__ == '__main__':
    required_keys = ["twitch_channel", "chat_text"]

    for key in required_keys:
        if "{" + key + "}" not in PROMPT_TEMPLATE:
            raise ValueError(f"Prompt template is missing required placeholder: {key}")
    threading.Thread(target=start_bot, daemon=True).start()
    threading.Thread(target=timer_monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
    