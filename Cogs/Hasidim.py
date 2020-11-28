import asyncio
import json
import logging
import random
import time

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")

file_handler = logging.FileHandler(filename=f"Log/Hasidim.log", encoding='utf-8', mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Hasidim(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild_id = 374770465853669386
        self.hasi_info = {}
        self.hasi_points = {}
        self.raffle_list = []
        self.raffle_pending = []
        self.authorized_role = [685364524890456064]
        self.authorized_user = [176489608492744704, 237007739073593345]

    @commands.command()
    async def recruit(self, ctx, args=8):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)

        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        server = self.client.get_guild(self.guild_id)
        role = server.get_role(576232407603347467)
        logger.info(f"""{ctx.message.author} posted a recruitment for {args} time slot.\n""")

        message_id = await ctx.send(f"""{role.mention} Signup for chill hasi {args}pm PST?""")
        await message_id.add_reaction(emoji="hasidude:585920757935243327")

        self.hasi_info[str(args)] = [message_id, [], []]
        self.hasi_points[str(args)] = []

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return

        for i in self.hasi_info.keys():
            if self.hasi_info[i][0].id == payload.message_id and len(self.hasi_info[i][1]) > 1:
                await self.hasi_info[i][0].remove_reaction(emoji="hasidude:585920757935243327", member=self.client.user)
                break

        for i in self.hasi_info.keys():
            if payload.message_id == self.hasi_info[i][0].id and not payload.user_id in self.hasi_info[i][1]:
                self.hasi_info[i][1].append(payload.user_id)
                self.hasi_points[i].append(payload.user_id)
                for j in self.hasi_info[i][2]:
                    if j[0] == payload.user_id:
                        self.hasi_info[i][2].remove(j)
                        break

                return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        for i in self.hasi_info.keys():
            if self.hasi_info[i][0].id == payload.message_id and payload.user_id in self.hasi_info[i][1]:
                self.hasi_info[i][1].remove(payload.user_id)
                if payload.user_id in self.hasi_points[i]:
                    self.hasi_points[i].remove(payload.user_id)
                if not payload.user_id in self.hasi_info[i][2]:
                    part = time.asctime().split(" ")
                    temp = (payload.user_id, part[3])
                    self.hasi_info[i][2].append(temp)

    @commands.command()
    async def all_keys(self, ctx):
        await ctx.message.delete()
        await ctx.message.author.send(f"""```\n{sorted(self.hasi_info)}\n```""")

    @commands.command()
    async def list(self, ctx, args="8"):
        await ctx.message.delete()

        if not args in self.hasi_info.keys():
            error_message = await ctx.send(f"""{args} is not a key. Type in ^^all_keys to see keys.""")
            await asyncio.sleep(10)
            await error_message.delete()
            return

        guild = self.client.get_guild(self.guild_id)
        spot = 1
        message = f"""```\nTime {args}\n"""
        message += f"""Sign up\n"""
        for i in self.hasi_info[args][1]:
            temp = guild.get_member(i)
            message += f"""{spot} {temp.display_name} || {temp}\n"""
            spot += 1
        message += f"""```\n```\n"""
        message += f"""Left\n"""
        for i in self.hasi_info[args][2]:
            temp = guild.get_member(i[0])
            message += f"""{temp.display_name} || {temp} Left at {i[1]}pst\n"""
        message += f"""```"""
        await ctx.message.author.send(message)

    @commands.command()
    async def point_record(self, ctx):
        await ctx.message.delete()
        with open(f"""resources/Json/Hasi_points.json""") as f:
            data = json.load(f)

        guild = self.client.get_guild(self.guild_id)

        sorted_list = []

        for i in data.keys():
            temp = guild.get_member(int(i))
            sorted_list.append((temp.display_name, data[i]))
        sorted_list.sort()

        message = f"""```\nAll Points:\n"""
        for i in sorted_list:
            if not temp is None:
                message += f"""{i[0]} || {i[1]}\n"""
        message += f"""```"""

        await ctx.message.author.send(message)

    @commands.command()
    async def points(self, ctx, args="8"):
        await ctx.message.delete()

        if not args in self.hasi_points.keys():
            error_message = await ctx.send(f"""{args} is not a key. Type in ^^all_keys to see keys.""")
            await asyncio.sleep(10)
            await error_message.delete()
            return

        guild = self.client.get_guild(self.guild_id)
        message = f"""```\nTime {args}\n"""
        for i in self.hasi_points[args]:
            temp = guild.get_member(i)
            message += f"""{temp.display_name} || {temp}\n"""
        message += f"""```"""
        await ctx.message.author.send(message)

    @commands.command()
    async def my_points(self, ctx):
        await ctx.message.delete()
        with open(f"""resources/Json/Hasi_points.json""") as f:
            data = json.load(f)

        if str(ctx.message.author.id) in data.keys():
            await ctx.message.author.send(f"""You have: {data[str(ctx.message.author.id)]} points""")
        else:
            await ctx.message.author.send(f"""You have not been added to the points list.""")

    @commands.command()
    async def give_points(self, ctx):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)
        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        parts = ctx.message.content.split(" ")
        if not len(parts) == 3:
            error = await ctx.send(f"""Error: format = ^^give_points (@person) (amount)""")
            await asyncio.sleep(10)
            await error.delete()
            return

        with open(f"""resources/Json/Hasi_points.json""") as f:
            data = json.load(f)
        person_id = parts[1].strip("<@!>")
        logger.info(f"""{ctx.message.author} gave {self.client.get_user(int(person_id))} {parts[2]} points\n""")
        guild = self.client.get_guild(self.guild_id)
        temp = guild.get_member(int(person_id))

        if not person_id in data.keys():
            data[person_id] = int(parts[2])
        else:
            data[person_id] += int(parts[2])

        message = f"""Given {temp.display_name} ({temp}) {parts[2]} points\n"""
        message += f"""New total is {data[person_id]}"""

        await ctx.message.author.send(message)

        with open(f"""resources/Json/Hasi_points.json""", "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def remove_points(self, ctx):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)
        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        parts = ctx.message.content.split(" ")
        if not len(parts) == 3:
            error = await ctx.send(f"""Error: format = ^^remove_points (@person) (amount)""")
            await asyncio.sleep(10)
            await error.delete()
            return

        with open(f"""resources/Json/Hasi_points.json""") as f:
            data = json.load(f)

        person_id = parts[1].strip("<@!>")
        if not person_id in data.keys():
            error_message = await ctx.send(f"""person not in list""")
            await asyncio.sleep(10)
            await error_message.delete()
            return

        logger.info(f"""{ctx.message.author} removed {parts[2]} from {self.client.get_user(int(person_id))}\n""")

        guild = self.client.get_guild(self.guild_id)
        temp = guild.get_member(int(person_id))
        message = f"""```\nBefore:\n"""
        message += f"""{temp.display_name} ({temp}) || {data[person_id]}\n"""
        message += f"""```"""

        if int(parts[2]) < data[person_id]:
            data[person_id] -= int(parts[int(2)])
        else:
            data[person_id] = 0

        message += f"""```\nNow:\n"""
        message += f"""{temp.display_name} ({temp}) || {data[person_id]}\n"""
        message += f"""```"""

        await ctx.message.author.send(message)

        with open(f"""resources/Json/Hasi_points.json""", "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def remove_person(self, ctx):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)

        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        parts = ctx.message.content.split(" ")
        if not len(parts) == 3:
            error = await ctx.send(f"""Error: format = ^^remove_person (Time) (@person)""")
            await asyncio.sleep(10)
            await error.delete()
            return

        if not parts[1] in self.hasi_info.keys():
            error_message = await ctx.send(f"""{parts[1]} is not a key. Type in ^^all_keys to see keys.""")
            await asyncio.sleep(10)
            await error_message.delete()
            return

        person = int(parts[2].strip("<@!>"))
        self.hasi_points[parts[1]].remove(int(person))

    @commands.command()
    async def update_points(self, ctx):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)

        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        parts = ctx.message.content.split(" ")
        if not len(parts) == 3:
            error = await ctx.send(f"""Error: format = ^^update_points (Time) (amount)""")
            await asyncio.sleep(10)
            await error.delete()
            return

        if not parts[1] in self.hasi_points.keys():
            error_message = await ctx.send(f"""{parts[1]} is not a key. Type in ^^all_keys to see keys.""")
            await asyncio.sleep(10)
            await error_message.delete()
            return

        if len(self.hasi_points[parts[1]]) == 0:
            error_message = await ctx.send(f"""list {parts[1]} for points is empty.""")
            await asyncio.sleep(10)
            await error_message.delete()
            return

        logger.info(f"""{ctx.message.author} updated points for time {parts[1]}. Gave {parts[2]} points""")

        with open(f"""resources/Json/Hasi_points.json""") as f:
            data = json.load(f)

        for i in self.hasi_points[parts[1]]:
            if str(i) in data.keys():
                data[str(i)] += int(parts[2])
            else:
                data[str(i)] = int(parts[2])
        self.hasi_points.pop(parts[1])

        with open(f"""resources/Json/Hasi_points.json""", "w") as f:
            json.dump(data, f, indent=4)

        await ctx.message.author.send("Successful adding points")
        logger.info(f"""updated points successful\n""")

    @commands.command()
    async def start_raffle(self, ctx):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)

        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        logger.info(f"""{ctx.message.author} started the raffle.""")

        with open(f"""resources/Json/Hasi_points.json""") as f:
            data = json.load(f)

        for i in data.keys():
            if data[i] > 9:
                temp = (int(i), (data[i] // 10))
                self.raffle_pending.append(temp)

        guild = self.client.get_guild(self.guild_id)
        for i in self.raffle_pending:
            try:
                temp = guild.get_member(i[0])
                if not temp is None:
                    logger.info(f"""sending {temp.display_name} a message""")
                    await temp.send(f"""You have enough points to have {i[1]} lives. Type ^^yes 1 - {i[1]} to have that many lives in the raffle.""")
                    logger.info("successful.")
            except Exception:
                logger.info(f"""Failed to send {temp.display_name} a message. {Exception.__name__}""")
                pass

        logger.info(f"""Finish sending messages for raffle.\n""")

    @commands.command()
    async def yes(self, ctx):
        if len(self.raffle_pending) == 0:
            return

        for person in self.raffle_pending:
            if ctx.message.author.id == person[0]:
                parts = ctx.message.content.split(" ")
                if len(parts) != 2:
                    await ctx.send("Error: ^^yes (amount)")
                    return

                if int(parts[1]) < 1:
                    await ctx.send(f"""Cannot put less than 1.""")
                    return

                for i in self.raffle_pending:
                    if ctx.message.author.id == i[0]:
                        if i[1] >= int(parts[1]):
                            temp = (int(i[0]), int(parts[1]))
                            logger.info(f"""Adding ({self.client.get_user(int(temp[0]))} {temp[1]}) to the raffle.""")
                            self.raffle_list.append(temp)
                            self.raffle_pending.remove(i)
                            logger.info(f"""successful\n""")
                            break
                        else:
                            await ctx.send(f"""You do not have {parts[1]} points. Try again.""")
                            return

                with open(f"""resources/Json/Hasi_points.json""") as f:
                    data = json.load(f)

                data[str(ctx.message.author.id)] -= int(parts[1]) * 10

                await ctx.send(f"""You are a part of the raffle with {parts[1]} lives.""")

                with open(f"""resources/Json/Hasi_points.json""", "w") as f:
                    data = json.dump(data, f, indent=4)
                return

    @commands.command()
    async def raffle_print(self, ctx):
        await ctx.message.delete()

        is_authorized = self.is_authorized(ctx)

        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        message = f"""```\nRaffle Name:\n"""
        guild = self.client.get_guild(self.guild_id)
        for i in self.raffle_list:
            temp = guild.get_member(i[0])
            message += f"""{temp.display_name} || {temp} lives {i[1]}\n"""
        message += f"""```"""

        await ctx.message.author.send(message)

    @commands.command()
    async def close_raffle(self, ctx):
        is_authorized = self.is_authorized(ctx)

        if not is_authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        logger.info(f"""{ctx.message.author} closed the raffle.\n""")

        if len(self.raffle_list) == 0:
            await ctx.message.author.send(f"""No one signed up.""")
            self.raffle_pending.clear()
            self.raffle_list.clear()
        else:
            await self.raffle_print(ctx)
            self.raffle_list.clear()
            self.raffle_pending.clear()

    @commands.command()
    async def get_hasi_logs(self, ctx):
        await ctx.message.delete()

        authorized = self.is_authorized(ctx)

        if not authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        logger.info(f"{ctx.message.author} grabbed the logs.")

        file = f"Log/Hasidim.log"
        await ctx.message.author.send(file=discord.File(file))
        logger.info(f"Successful\n")

    @commands.command()
    async def clear_hasi_logs(self, ctx):
        await ctx.message.delete()

        authorized = self.is_authorized(ctx)

        if not authorized:
            error = await ctx.send(f"""Do not have permission. Ask an officer.""")
            await asyncio.sleep(10)
            await error.delete()
            return

        await ctx.message.author.send(f"cleared hasidim logs.")

        with open("Log/Hasidim.log", "w") as f:
            pass

    @commands.command()
    async def fake_lineup(self, ctx, args):
        await ctx.message.delete()

        logger.info(f"{ctx.message.author} used the fake_lineup command.")

        if not str(args) in self.hasi_info.keys():
            error = await ctx.send(f"{args} is not a key")
            await asyncio.sleep(10)
            await error.delete()
            return
        guild = self.client.get_guild(self.guild_id)
        names = []
        for i in self.hasi_info[str(args)][1]:
            member = guild.get_member(i)
            names.append(member.display_name)
        with open(f"resources/Text/Lineup_template.txt", "r") as f:
            template = f.readlines()

        lineup = f""
        for i in template:
            lineup += str(i)

        while len(names) != 0:
            temp = random.choice(names)
            lineup = lineup.replace("X", str(temp), 1)
            names.remove(temp)
        await ctx.message.author.send(lineup)

    def is_authorized(self, ctx):
        for i in ctx.message.author.roles:
            if i.id in self.authorized_role or ctx.message.author.id in self.authorized_user:
                return True
        return False


def setup(client):
    client.add_cog(Hasidim(client))