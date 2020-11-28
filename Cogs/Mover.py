import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")

file_handler = logging.FileHandler(filename=f"Log/Application.log", encoding='utf-8', mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Mover(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.classrooms = (524436176824827919, 744802995413319720)
        self.guild_id = 524436176824827907


    @commands.command()
    async def move(self, ctx):
        guild = self.client.get_guild(self.guild_id)
        channels = await self.client.fetch_channel(self.classrooms[0])
        await ctx.message.author.move_to(channels)

    @commands.command()
    async def people(self, ctx):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass

        new_channel = self.client.get_channel(374770465853669390)
        voice_channel = ctx.message.author.voice.channel
        members = voice_channel.members
        print(len(members))
        count = 0
        for member in members:
            if member.nick is None:
                print(member.name)
            else:
                print(member.nick)
            for i in member.roles:
                if i.id == 374772275959824384:
                    count += 1
                    await member.move_to(new_channel)
                    break
        print(count)



def setup(client):
    client.add_cog(Mover(client))
