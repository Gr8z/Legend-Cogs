import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
import asyncio
import urllib.parse as urlparse
import requests
import json
import datetime
from cogs.utils import checks

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

class clanchest:
    """clanchest!"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = dataIO.load_json('cogs/auth.json')
        self.clans = dataIO.load_json('cogs/clans.json')
        self.cc = dataIO.load_json('cogs/clanchest.json')

    def getAuth(self):
        return {"auth" : self.auth['token']}

    async def checkChest(self, ctx):

        currDate = str(datetime.date.today())
        self.cc[currDate] = []
        dataIO.save_json('cogs/clanchest.json', self.cc)

        while self is self.bot.get_cog("clanchest"):

            print("Checking Clan chest...")

            try:
                clans = requests.get('http://api.cr-api.com/clan/'+','.join(self.clans[clan]["tag"] for clan in self.clans)+'?exclude=members', headers=self.getAuth(), timeout=10).json()
                        
                for x in range(0, len(clans)):

                    if clans[x]['clanChest']['status'] == "completed":
                        if clans[x]['name'] not in self.cc[currDate]:
                            print("Clan chest completed for a clan...")
                            self.cc[currDate].append(clans[x]['name'])
                            dataIO.save_json('cogs/clanchest.json', self.cc)

                            if len(self.cc[currDate]) == 1:
                                await self.bot.send_message(discord.Object(id='374597224283504642'), "Look out **{}** is the first one to complete the Clan Chest!".format(self.cc[currDate][0]))

                        if ((len(self.cc[currDate]) > 9) or ((datetime.datetime.today().weekday() == 0) and (datetime.datetime.now().time() > datetime.time(7)))):
                            await self.printChest(ctx, currDate)
                            print("All clans have completed the chests...")
                            return

            except Exception as e:
                print(e)
                pass

            await asyncio.sleep(600)

    async def printChest(self, ctx, currDate):
        
        message = "**Clan Chest Leaderboard ({})**\n```py\n".format(currDate)

        for index, clan in enumerate(self.cc[currDate]):
            message += "{}.  {}\n".format(str(index + 1).zfill(2), clan)

        message += "```"

        await self.bot.send_message(discord.Object(id='374597224283504642'), message)

    @commands.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def clanchesttrack(self, ctx):
        """Start tracking clanchest"""

        await self.bot.say("Clan Chest Tracking started...")

        loop = asyncio.get_event_loop()
        loop.create_task(self.checkChest(ctx))
        
def check_files():
    f = "cogs/clanchest.json"
    if not fileIO(f, "check"):
        print("Creating empty clanchest.json...")
        dataIO.save_json(f, {})

def setup(bot):
    check_files()
    bot.add_cog(clanchest(bot))