import discord
from discord.ext import commands
from gtts import gTTS
import os
import youtube_dl
import shutil


class Text_toSpeach(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_client = None

    @commands.command()
    async def join(self, ctx):
        await ctx.message.delete()
        try:
            voice_channel = ctx.message.author.voice.channel

            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.move_to(voice_channel)
            else:
                self.voice_client = await voice_channel.connect()

        except AttributeError as e:
            print(f"Error not in a channel.\n {e}")

    @commands.command()
    async def leave(self, ctx):
        await ctx.message.delete()

        await self.voice_client.disconnect()
        print(self.voice_client.is_connected())

    @commands.command()
    async def play(self, ctx,  url : str):
        await ctx.message.delete()

        try:
            old_song_there = os.path.isfile(f"./song.mp3")
            if old_song_there:
                os.remove(f"./song.mp3")
                print("removed old song")
        except PermissionError as e:
            print(f"tried to delete song file but being used.\n {e}")
            return

        ytd_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        }

        with youtube_dl.YoutubeDL(ytd_opts) as ydl:
            print(f"downloading song \n\n")
            ydl.download([url])
            print(f"downloading song")

        for file in os.listdir(f"./"):
            if file.endswith(f".mp3"):
                print(f"found song. {file}")
                name = file
                os.rename(name, "song.mp3")

                print(name)

        if os.path.isfile(f"./song.mp3"):
            self.voice_client.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("finished playing music."))
        else:
            print("cannot find song.")

    @commands.command()
    async def sounds(self, ctx):
        await ctx.message.delete()

        sounds = os.listdir(f"./Audio")
        message = f"```\n"
        for i in range(len(sounds)):
            if i == 0:
                message += f"default {sounds[i]}\n"
            else:
                message += f"{i} {sounds[i]} \n"

        message += f"```"

        await ctx.message.author.send(message)

    @commands.command()
    async def sound(self, ctx, augs=0):
        await ctx.message.delete()

        if ctx.message.author.id != 176489608492744704:
            return

        files = os.listdir(f"./Audio/")

        if self.voice_client and self.voice_client.is_connected():
            self.voice_client.play(discord.FFmpegPCMAudio(f"./Audio/{files[augs]}"), after=lambda e: print(f'done playing file {files[augs]}'))

    @commands.command()
    async def tts(self, ctx):
        await ctx.message.delete()

        if ctx.message.author.id != 176489608492744704:
            return

        text = ctx.message.content[6::]
        finished = True
        fail_count = 1

        output = gTTS(text=text, lang="en", slow=False)
        output.save("output.mp3")

        self.voice_client.play(discord.FFmpegPCMAudio(f"output.mp3"), after=lambda e: os.remove(f"./output.mp3"))



def setup(client):
    client.add_cog(Text_toSpeach(client))