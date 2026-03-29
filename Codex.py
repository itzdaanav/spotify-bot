import discord
from discord.ext import commands

# 🔥 CONFIG

SPOTIFY_ROLE_NAME = "Spotify Listener"
SPOTIFY_CHANNEL_NAME = "spotify-logs"

# ⚙️ INTENTS
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

    # 🔍 Get Spotify activity
    def get_spotify(member):
        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                return activity
        return None

    before_spotify = get_spotify(before)
    after_spotify = get_spotify(after)

    # 🎧 STARTED LISTENING
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

    # ⛔ STOPPED LISTENING
    elif before_spotify and not after_spotify:
        await after.remove_roles(role)

        if channel:
            embed = discord.Embed(
                title="⛔ Stopped Listening",
                description=f"{after.mention} stopped listening to Spotify",
                color=discord.Color.red()
            )

            await channel.send(embed=embed)

# ▶️ RUN BOT
import os
bot.run(os.getenv("TOKEN"))
