import discord
from discord.ext import commands
import asyncio
import time
import json
import logging
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")

file_handler = logging.FileHandler(filename=f"Log/Application.log", encoding='utf-8', mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Application(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = {}
        self.app_up = False
        self.item_in_queue = False
        self.channel_id = 0
        self.main_count_id = 0
        self.guild_id = 374770465853669386

    @commands.command()
    @commands.has_role("Officer")
    async def start_app(self, ctx):
        await ctx.message.delete()
        with open(f"resources/Json/Application_votes.json", "w") as f:
            temp = {}
            json.dump(temp, f)

        logger.info(f"{self.client.get_user(ctx.message.author.id)} Started an an application.\n")

        self.app_up = True

        self.channel_id = ctx.message.channel.id
        message = await ctx.send(f"Upvotes = 0\nDownvotes = 0\npercent of upvotes = 0%")
        self.main_count_id = message.id

        await ctx.message.author.send("Started app.")

        while self.app_up:
            await asyncio.sleep(60)
            if self.item_in_queue:
                await self.update_votes(ctx)
                logger.info("updating votes\n")

    @commands.command()
    async def upvote(self, ctx):
        if ctx.message.author.id in self.queue.keys():
            error = await ctx.send(f"Error you cannot vote / change your vote right now. Please try again in 2 minutes.")
            await asyncio.sleep(10)
            await error.delete()
            await ctx.message.delete()
        else:
            logger.info(f"{ctx.message.author} upvoted\n")
            if self.app_up:
                temp = ctx.message.content[9::]
                self.queue[ctx.message.author.id] = [True, temp]

                temp = ctx.message
                await temp.add_reaction(emoji="👌")

                self.item_in_queue = True


    @commands.command()
    async def downvote(self, ctx):
        if ctx.message.author.id in self.queue.keys():
            error = await ctx.send(f"Error you cannot vote / change your vote right now. Please try again in 2 minutes.")
            await asyncio.sleep(10)
            await error.delete()
            await ctx.message.delete()
        else:
            logger.info(f"{ctx.message.author} downvoted\n")
            if self.app_up:
                temp = ctx.message.content[11::]
                self.queue[ctx.message.author.id] = [False, temp]

                temp = ctx.message
                await temp.add_reaction(emoji="👌")

                self.item_in_queue = True

    @commands.command()
    @commands.has_role("Officer")
    async def update_votes(self, ctx):
        if not self.item_in_queue or not self.app_up:
            return
        self.clearing_queue()

        channel = self.client.get_channel(self.channel_id)
        count_message = await channel.fetch_message(self.main_count_id)
        guild = self.client.get_guild(self.guild_id)

        with open(f"resources/Json/Application_votes.json") as f:
            data = json.load(f)

        upvotes = 0
        downvotes = 0

        for i in data.keys():
            if data[i][1] is True:
                if data[i][2] is True:
                    upvotes += 1
                elif data[i][2] is False:
                    downvotes += 1

            vote = "Upvote" if data[i][2] else "Downvote"
            print(type(i))
            print(i)
            member = guild.get_member(int(i))
            print(member)
            if data[i][1]:
                approved = "Counts"
            else:
                approved = "Doesn't count"

            if data[i][0] == 0:
                display_tag = await channel.send(f"*_**{member.display_name} ({member}): {vote}: {approved}**_*")
                new_message = await channel.send(f"{data[i][3]}")
                data[i] = [new_message.id, data[i][1], data[i][2], data[i][3], display_tag.id]
            else:
                display_temp = await channel.fetch_message(data[i][4])
                await display_temp.edit(content=f"*_**{member.display_name} ({member}): {vote}: {approved}**_*")
                temp = await channel.fetch_message(data[i][0])
                await temp.edit(content=f"{data[i][3]}")

        with open(f"resources/Json/Application_votes.json", "w") as f:
            json.dump(data, f, indent=4)

        percent = 0
        if upvotes > 0 or downvotes > 0:
            percent = (upvotes / (upvotes + downvotes)) * 100
        await count_message.edit(content=f"Upvotes = {upvotes}\nDownvotes = {downvotes}\npercent of upvotes = {round(percent, 2)}%")

    def clearing_queue(self):
        with open(f"resources/Json/Application_votes.json") as f:
            data = json.load(f)

        for i in self.queue.keys():
            if str(i) in data.keys():
                data[str(i)] = [data[str(i)][0], data[str(i)][1], self.queue[i][0], self.queue[i][1], data[str(i)][4]]
            else:
                data[i] = [0, True, self.queue[i][0], self.queue[i][1], 0]

        with open(f"resources/Json/Application_votes.json", "w") as f:
            json.dump(data, f, indent=4)
        self.queue.clear()
        self.item_in_queue = False

    @commands.command()
    @commands.has_role("Officer")
    async def close_app(self, ctx):
        logger.info(f"{ctx.message.author} Closed the application\n")
        await self.update_votes(ctx)
        self.app_up = False

        await ctx.message.delete()
        await ctx.message.author.send(f"Closed the app.")

    @commands.command()
    @commands.has_role("Officer")
    async def approve(self, ctx):
        await ctx.message.delete()
        logger.info(f"{self.client.get_user(ctx.message.author.id)} approved the app")
        parts = ctx.message.content.split(" ")
        person_id = parts[1].strip("<@!>")

        with open(f"resources/Json/Application_votes.json") as f:
            data = json.load(f)
            data[person_id][1] = True

        with open(f"resources/Json/Application_votes.json", "w") as f:
            json.dump(data, f, indent=4)

        self.item_in_queue = True

    @commands.command()
    @commands.has_role("Officer")
    async def disapprove(self, ctx):
        await ctx.message.delete()
        logger.info(f"{self.client.get_user(ctx.message.author.id)} approved the app")
        parts = ctx.message.content.split(" ")
        person_id = parts[1].strip("<@!>")
        with open(f"resources/Json/Application_votes.json") as f:
            data = json.load(f)
            data[person_id][1] = False

        with open(f"resources/Json/Application_votes.json", "w") as f:
            json.dump(data, f, indent=4)

        self.item_in_queue = True

        person = self.client.get_user(int(person_id))
        if person:
            await person.send("Your vote was discounted by an officer.\ngive a better reason\n::upvote reason\nor\n::downvote reason")
        else:
            print("error Person cannnot be found")

    @commands.command()
    @commands.has_role("Officer")
    async def get_app_logs(self, ctx):
        await ctx.message.delete()

        logger.info(f"{ctx.message.author} grabbed the logs.")

        file = f"Log/Application.log"
        await ctx.message.author.send(file=discord.File(file))
        logger.info(f"Successful\n")

    @commands.command()
    @commands.has_role("Officer")
    async def clear_app_logs(self, ctx):
        await ctx.message.delete()

        with open(f"resources/Json/Application_votes.json", "w") as f:
            pass

def setup(client):
    client.add_cog(Application(client))
