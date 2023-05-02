import asyncio
from discord.ext import commands
import yt_dlp as youtube_dl
import discord

intents = discord.Intents.default()
intents.members=True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'),intents=intents)

@bot.command()
async def pause(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not connected to a voice channel.")
    else:
        ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not connected to a voice channel.")
    else:
        ctx.voice_client.resume()

@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not connected to a voice channel.")
    else:
        ctx.voice_client.stop()
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'nocheckcertificate': True
}
@bot.command()
async def play(ctx, url):
        if ctx.author.voice is None:
                await ctx.send("You must be connected to a voice channel to use this command.")
                return
        if ctx.voice_client is None:
                await join_channel(ctx)
        voice_client = ctx.voice_client
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']

        FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
        }

        voice_client = ctx.voice_client
        voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS),after=lambda e: after_playing(e, ctx))

def after_playing(error, ctx):
    coro = ctx.send("Playback complete. Leaving the voice channel.")
    fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        fut.result()
    except Exception as e:
        print(f"Error sending message: {e}")

    coro = ctx.voice_client.disconnect()
    fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        fut.result()
    except Exception as e:
        print(f"Error disconnecting from voice channel: {e}")

async def join_channel(ctx):
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()


bot.run('TOKEN')
