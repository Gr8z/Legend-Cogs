import discord
from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO, fileIO
from __main__ import send_cmd_help
import os
import io
import requests
import json
import asyncio
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

class warlog:
    """Clash Royale Clan War log"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = dataIO.load_json('cogs/auth.json')
        self.clans = dataIO.load_json('cogs/clans.json')

    def getAuth(self):
        return {"auth" : self.auth['token']}
    
    def save_clans(self):
        dataIO.save_json('cogs/clans.json', self.clans)

    def update_clans(self):
        self.clans = dataIO.load_json('cogs/clans.json')

    async def getLeague(self, trophies):
        
        if trophies >= 3000:
            return "legend"
        elif trophies >= 1500:
            return "gold"
        elif trophies >= 600:
            return "silver"
        else:
            return "bronze"

    async def findRank(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    async def genImage(self, leagueName, trophies, rank, clanName, participants, wins, crowns):

        font1 = ImageFont.truetype("data/warlog/ClashRoyale.ttf",27)
        font2 = ImageFont.truetype("data/warlog/ClashRoyale.ttf",37)
        font3 = ImageFont.truetype("data/warlog/ClashRoyale.ttf",41)

        img = Image.open("data/warlog/images/warlog.jpg")
        draw = ImageDraw.Draw(img)

        league = Image.open("data/warlog/images/{}.png".format(leagueName))
        img.paste(league, (410, 55), league) # league

        draw.text((493, 75), "{:,}".format(int(trophies)), (255,255,255), font=font1) # Trophies

        # thin border
        x, y = 284, 192
        fillcolor = "white"
        shadowcolor = "black"
        draw.text((x-2, y-2), rank, font=font2, fill=shadowcolor)
        draw.text((x+2, y-2), rank, font=font2, fill=shadowcolor)
        draw.text((x-2, y+2), rank, font=font2, fill=shadowcolor)
        draw.text((x+2, y+2), rank, font=font2, fill=shadowcolor)

        draw.text((x, y), rank, font=font2, fill=fillcolor) # Rank

        draw.text((347, 194), clanName, (255,255,255), font=font3) # Clan Name

        draw.text((682, 340), participants, (255,255,255), font=font1) # Participants
        draw.text((682, 457), wins, (255,255,255), font=font1) # Wins
        draw.text((682, 575), crowns, (255,255,255), font=font1) # Crowns

        # scale down and return
        scale = 0.5
        scaled_size = tuple([x * scale for x in img.size])
        img.thumbnail(scaled_size)

        return img

    async def getWarData(self, channel):

        self.update_clans()

        for clankey in self.clans.keys():

            try:
                clandata = requests.get('https://api.royaleapi.com/clan/{}/warlog'.format(self.clans[clankey]['tag']), headers=self.getAuth(), timeout=10).json()
            except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                return
            except requests.exceptions.RequestException as e:
                print(e)
                return

            standings = clandata[0]['standings']
            clanRank = await self.findRank(standings, "tag", self.clans[clankey]['tag'])
            warTrophies = standings[clanRank]['warTrophies']

            if self.clans[clankey]['warTrophies'] != warTrophies:

                clanLeague = await self.getLeague(warTrophies)

                image = await self.genImage(clanLeague, str(warTrophies), str(clanRank+1), standings[clanRank]['name'], str(standings[clanRank]['participants']), str(standings[clanRank]['wins']), str(standings[clanRank]['crowns']))
                filename = "warlog-{}.png".format(clankey)

                with io.BytesIO() as f:
                    image.save(f, "PNG")
                    f.seek(0)
                    await self.bot.send_file(channel, f, filename=filename)

                self.clans[clankey]['warTrophies'] = warTrophies
                self.save_clans()

            await asyncio.sleep(1)

    @commands.command(pass_context=True)
    async def warlog(self, ctx):
        """Track Clan wars"""

        channel = ctx.message.channel
        await self.getWarData(channel)


def check_clans():
    c = dataIO.load_json('cogs/clans.json')
    for clankey in c.keys():
        if 'members' not in c[clankey]:
            c[clankey]['members'] = []  
    dataIO.save_json('cogs/clans.json', c)

def check_files():
    f = "cogs/auth.json"
    if not fileIO(f, "check"):
        print("enter your RoyaleAPI token in auth.json...")
        fileIO(f, "save", {"token" : "enter your RoyaleAPI token here!"})

def setup(bot):
    check_files()
    check_clans()
    bot.add_cog(warlog(bot))