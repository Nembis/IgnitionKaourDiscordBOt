import discord
from discord.ext import commands
import datetime

class VIPReminder(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_id = 685559233378517033
        self.message_id = 702334181241520180
        self.emojis = ["<a:pp:625481509339660308>", "<:dye:280954745932480512>",
                       "<a:fullrecovery:599326674701516876>", "<:Holy_Water_of_Lymilark:702347411598737442>",
                       "<:Remote_Bank_Coupon:702347371714969682>", "<:Unlimited_Shadow_Mission_Pass:702347444956168283>",
                       "<:Speech_Bubble_Sticker:702347467890622485>"]

    @commands.command()
    async def test(self, ctx):
        await ctx.message.delete()
        channel = self.client.get_channel(self.channel_id)
        msg = await channel.fetch_message(self.message_id)
        for i in msg.reactions:
            print("emoji")
            print(i.f)
            item = await i.users().flatten()
            print("names")
            for j in item:
                print(j.display_name)

    @commands.command()
    async def new_test(self, ctx):
        channel = self.client.get_channel(self.channel_id)
        msg = await channel.fetch_message(self.message_id)
        for i in msg.reactions:
            print(str(i.emoji))
            if str(i.emoji) in self.emojis:
                print("yes")
            else:
                print("no")

    @commands.command()
    async def p_message(self, ctx):
        print(await self.find_message())

    async def find_message(self):
        channel = self.client.get_channel(self.channel_id)
        msg = await channel.fetch_message(self.message_id)
        if msg is None:
            print("false")
            return False
        else:
            print("true")
            return True


def setup(client):
    client.add_cog(VIPReminder(client))