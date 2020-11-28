import discord
from discord.ext import commands
import os
import asyncio

::intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix="::", intents=intents)


def get_token():
    with open(f"resources/Text/Token.txt") as f:
        return f.readline()


@client.event
async def on_ready():
    print("Bot is ready.")


@client.command()
async def load_cog(ctx, extension):
    await ctx.message.delete()
    if ctx.message.author.id == 176489608492744704:
        client.load_extension(f"Cogs.{extension}")
        await ctx.send(f"loaded cog {extension}")
    else:
        await ctx.send(f"You do not have permission.")


@client.command()
async def unload_cog(ctx, extension):
    await ctx.message.delete()
    if ctx.message.author.id == 176489608492744704:
        client.unload_extension(f"Cogs.{extension}")
        await ctx.send(f"unloaded cog {extension}")
    else:
        await ctx.send(f"You do not have permission.")

for filename in os.listdir(f"./Cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"Cogs.{filename[:-3]}")


@client.command()
async def p(ctx, args):
    person = client.get_user(206412714141155328)
    for i in range(0, 5):
        await person.send(args)
        await asyncio.sleep(5)


@client.command()
async def profile(ctx):
    await ctx.message.delete()

    user = client.get_user(105679756304846848)

    profile = user.avatar
    print(profile)


@client.command()
async def matt(ctx):
    matt = client.get_user(105679756304846848)
    message = ctx.message.content[7::]
    await matt.send(message)


@client.command()
async def data(ctx, channel):
    print(type(channel))
    print(channel)

client.run(get_token())