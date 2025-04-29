#######################
# Rename to settings.py
#######################

# Twitch setup
TWITCH_TOKEN = "oauth:YOUR_TOKEN_HERE"
TWITCH_CHANNEL = "yourchannel"
BOT_NICK = "yourbotname" # Optional

# Model setup
SUMMARIZER_MODEL = "openchat"  # or mistral, zephyr, etc.

# TTS setup
TTS_VOICE = "en-US-GuyNeural"  # Customize your Edge TTS voice here

# Pomodoro default durations
DEFAULT_WORK_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5

# Prompt Template - this takes a bit of prompt engineering for these local LLMs
PROMPT_TEMPLATE = (
    "You're summarizing Twitch chat for me, the streamer. "
    "Speak directly to me. Use 'you' or '{twitch_channel}'. "
    "Group similar comments. Try to do half as many, or "
    "less, sentences as chat messages, if possible. "
    "Focus only on chat messages.\n\n"
    "Chat log:\n{chat_text}"
)

# Use this to test and tweak prompts and voices
# In app.py set chat_log = SAMPLE_CHAT on line 34
SAMPLE_CHAT = [
    "coolguy123: LET'S GOOOOOO!",
    "pixieplays: you totally nailed that boss",
    "spammer69: Pog Pog Pog Pog Pog",
    "modbot9000: Reminder: No spoilers in chat please.",
    "ghostlygal: omg I jumped at that scream 😂",
    "coolguy123: ngl I thought you were gonna die there lmao",
    "snackytime: snack break incoming?",
    "lurky_mcgee: been lurking, but love the vibe tonight",
    "backseatbob: bro you missed the switch on the left",
    "streammommy: hydrate or diedrate",
    "ragequitter77: this game is actual garbage lol",
    "pixieplays: don’t listen to the trolls, you’re crushing it!",
    "coolguy123: agreed! loving this stream so much rn",
    "whispershard: that puzzle took me 3 hours the first time 😭",
    "ghostlygal: oooo lore drop??? 👀",
    "spammer69: CHAT’S ON FIRE 🔥🔥🔥",
    "modbot9000: Warning issued to ragequitter77 for excessive negativity.",
    "streammommy: 💜💜💜",
    "snackytime: brb fridge run",
    "lurky_mcgee: clip that moment omg",
    "coolguy123: we’re witnessing greatness"
]