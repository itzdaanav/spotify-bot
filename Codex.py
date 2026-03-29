import discord
from discord.ext import commands
import os
from flask import Flask
import threading
import time

# 🔥 CONFIG
TOKEN = os.getenv("DISCORD_TOKEN")  # ← Railway env var
SPOTIFY_ROLE_NAME = "Spotify Listener"
SPOTIFY_CHANNEL_NAME = "spotify-logs"

# 🌐 FLASK WEB SERVER (Railway requirement)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Spotify Bot is running! ✅"

@app.route('/health')
def health():
    return {"status": "alive", "bot": bot.user.name if 'bot' in globals() else "starting"}

# ⚙️ DISCORD BOT
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_presence_update(before, after):
    guild = after.guild
    role = discord.utils.get(guild.roles, name=SPOTIFY_ROLE_NAME)
    channel = discord.utils.get(guild.text_channels, name=SPOTIFY_CHANNEL_NAME)

    if not role:
        return

    def get_spotify(member):
        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                return activity
        return None

    before_spotify = get_spotify(before)
    after_spotify = get_spotify(after)

    # STARTED LISTENING
    if not before_spotify and after_spotify:
        await after.add_roles(role)
        if channel:
            embed = discord.Embed(
                title="🎧 Now Listening",
                description=f"{after.mention} started listening!",
                color=discord.Color.green()
            )
            embed.add_field(name="Song", value=after_spotify.title, inline=False)
            embed.add_field(name="Artist", value=after_spotify.artist, inline=False)
            embed.add_field(name="Album", value=after_spotify.album, inline=False)
            embed.set_thumbnail(url=after_spotify.album_cover_url)
            await channel.send(embed=embed)

    # STOPPED LISTENING
    elif before_spotify and not after_spotify:
        await after.remove_roles(role)
        if channel:
            embed = discord.Embed(
                title="⛔ Stopped Listening",
                description=f"{after.mention} stopped listening",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)

# 🚀 START EVERYTHING
def run_bot():
    bot.run(TOKEN)

if __name__ == "__main__":
    # Start Discord bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask web server (Railway needs this)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
