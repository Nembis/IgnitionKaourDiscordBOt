import discord
from discord.ext import commands
import logging
import asyncio
import json
from random import choice

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")

file_handler = logging.FileHandler(filename=f"Log/Application.log", encoding='utf-8', mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Name_Change(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild_id = 374770465853669386
        self.default_nickname = "Sounds"
        self.current_person_id = None
        self.is_ready_to_change = True

    @commands.command()
    async def picture(self, ctx, member=None):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass
        if member is None:
            await ctx.message.author.send(ctx.message.author.avatar_url)
        else:
            member_id = member.strip("<@!>")
            user = self.client.get_user(int(member_id))
            await ctx.message.author.send(user.avatar_url)

    @commands.command()
    async def talk(self, ctx):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass




    @commands.command()
    async def all_quotes(self, ctx):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass

        with open("./resources/Json/Quotes.json", "r") as f:
            data = json.load(f)

        formatted_message = f"```\n"
        guild = self.client.get_guild(self.guild_id)

        for key, quotes in data.items():
            formatted_message += f"Person {guild.get_member(int(key)).nick}:{quotes[0]}\n"
            for quote in range(1, len(quotes)):
                formatted_message += f"{quotes[quote]}\n"

        formatted_message += f"```"

        await ctx.message.author.send(formatted_message)

    @commands.command()
    async def change_to_person(self, ctx, person=-1):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass

        if not self.is_ready_to_change:
            temp = await ctx.send(f"Still on cool down to change.")
            await asyncio.sleep(5)
            await temp.delete()
            return

        with open("./resources/Json/Quotes.json", "r") as f:
            data = json.load(f)

        guild = self.client.get_guild(self.guild_id)

        all_keys = tuple(data.keys())
        if person == -1:
            self.current_person_id = int(choice(all_keys))
        else:
            self.current_person_id = int(all_keys[person])

        print(guild.get_member(self.current_person_id))
        print(guild.get_member(self.current_person_id).display_name)

        client_as_member = guild.get_member(self.client.user.id)
        member = guild.get_member(self.current_person_id)

        await client_as_member.edit(nick=member.display_name)
        await self.client.user.edit(avatar=await member.avatar_url.read())

        self.is_ready_to_change = False
        await self.change_back_timer()

    @commands.command()
    async def change_back(self, ctx):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass

        if self.is_ready_to_change and not self.current_person_id is None:
            guild = self.client.get_guild(self.guild_id)
            client_as_member = guild.get_member(self.client.user.id)

            await client_as_member.edit(nick=self.default_nickname)
            await self.client.user.edit(avatar=await self.client.user.default_avatar_url.read())

            self.current_person_id = None
            await self.change_back_timer()

        elif self.current_person_id is None:
            await ctx.send(f"Is already default.")
        else:
            await ctx.send(f"Cannot change right now.")


    async def change_back_timer(self):
        for i in range(5):
            print(i * 60)
            await asyncio.sleep(60)

        print(F"Ready to change.")
        self.is_ready_to_change = True


    @commands.command()
    async def change_self(self, ctx, person="nick_name"):
        try:
            await ctx.message.delete()
        except FileNotFoundError:
            pass

        print("Changing to new profile.")

        guild = self.client.get_guild(self.guild_id)
        client_as_member = guild.get_member(589912092073656341)
        await client_as_member.edit(nick="Nick_name")
        await self.client.user.edit(avatar=await ctx.message.author.avatar_url.read())

        print("sleeping")
        for i in range(5):
            print(i * 60)
            await asyncio.sleep(60)

        await self.client.user.edit(avatar=await self.client.user.default_avatar_url.read())
        print("changed back.")


def setup(client):
    client.add_cog(Name_Change(client))
