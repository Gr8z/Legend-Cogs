import discord
from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO, fileIO
from __main__ import send_cmd_help
import os
import io
import asyncio
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import clashroyale
from datetime import datetime, timedelta
import time

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"


class warlog:
    """Clash Royale Clan War log"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = self.bot.get_cog('crtools').auth
        self.clans = self.bot.get_cog('crtools').clans
        self.clash = clashroyale.RoyaleAPI(self.auth.getToken(), is_async=True)

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

    async def last_day(self, d, day_name):
        days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday',
                        'thursday', 'friday', 'saturday']
        target_day = days_of_week.index(day_name.lower())
        delta_day = target_day - d.isoweekday()
        if delta_day >= 0:
            delta_day -= 7
        return int((d + timedelta(days=delta_day)).strftime('%s'))

    async def genImage(self, leagueName, trophies, rank, clanName, participants, wins, crowns):

        font1 = ImageFont.truetype("data/warlog/ClashRoyale.ttf", 27)
        font2 = ImageFont.truetype("data/warlog/ClashRoyale.ttf", 37)
        font3 = ImageFont.truetype("data/warlog/ClashRoyale.ttf", 41)

        img = Image.open("data/warlog/images/warlog.jpg")
        draw = ImageDraw.Draw(img)

        league = Image.open("data/warlog/images/{}.png".format(leagueName))
        img.paste(league, (410, 55), league)  # league

        draw.text((493, 75), "{:,}".format(int(trophies)), (255, 255, 255), font=font1)  # Trophies

        # thin border
        x, y = 284, 192
        fillcolor = "white"
        shadowcolor = "black"
        draw.text((x - 2, y - 2), rank, font=font2, fill=shadowcolor)
        draw.text((x + 2, y - 2), rank, font=font2, fill=shadowcolor)
        draw.text((x - 2, y + 2), rank, font=font2, fill=shadowcolor)
        draw.text((x + 2, y + 2), rank, font=font2, fill=shadowcolor)

        draw.text((x, y), rank, font=font2, fill=fillcolor)  # Rank

        draw.text((347, 194), clanName, (255, 255, 255), font=font3)  # Clan Name

        draw.text((682, 340), participants, (255, 255, 255), font=font1)  # Participants
        draw.text((682, 457), wins, (255, 255, 255), font=font1)  # Wins
        draw.text((682, 575), crowns, (255, 255, 255), font=font1)  # Crowns

        # scale down and return
        scale = 0.5
        scaled_size = tuple([x * scale for x in img.size])
        img.thumbnail(scaled_size)

        return img

    async def getWarData(self, channel):

        for clankey in self.clans.keysClans():

            try:
                clanwars = await self.clash.get_clan_war_log(await self.clans.getClanData(clankey, 'tag'))
            except clashroyale.RequestError:
                return

            standings = clanwars[0].standings
            clanRank = await self.findRank(standings, "tag", await self.clans.getClanData(clankey, 'tag'))
            warTrophies = standings[clanRank].war_trophies

            if await self.clans.getClanData(clankey, 'warTrophies') != warTrophies:

                clanLeague = await self.getLeague(warTrophies)

                image = await self.genImage(clanLeague,
                                            str(warTrophies),
                                            str(clanRank + 1),
                                            standings[clanRank].name,
                                            str(standings[clanRank].participants),
                                            str(standings[clanRank].wins),
                                            str(standings[clanRank].crowns))
                filename = "warlog-{}.png".format(clankey)
                clanChannel = await self.clans.getClanData(clankey, 'warlog_channel')

                with io.BytesIO() as f:
                    image.save(f, "PNG")
                    f.seek(0)
                    await self.bot.send_file(channel, f, filename=filename)

                with io.BytesIO() as f:
                    image.save(f, "PNG")
                    f.seek(0)
                    if clanChannel is not None:
                        await self.bot.send_file(discord.Object(id=clanChannel), f, filename=filename)

                for memberkey in self.clans.keysClanMembers(clankey):
                    WarDayWins = 0
                    cardsEarned = 0
                    tag = await self.clans.getClanMemberData(clankey, memberkey, 'tag')
                    for index, war in enumerate(clanwars):
                        if index == 5:
                            break
                        if war.created_date > await self.last_day(datetime.today(), 'sunday'):
                            for participant in war.participants:
                                if participant.tag == tag:
                                    WarDayWins += participant.wins
                                    cardsEarned += participant.cardsEarned

                    await self.clans.setWarstats(clankey, tag, WarDayWins, cardsEarned)

                await self.clans.setWarTrophies(clankey, warTrophies)

            await asyncio.sleep(1)

    @commands.command(pass_context=True)
    async def warlog(self, ctx):
        """Track Clan wars"""
        channel = ctx.message.channel
        await self.getWarData(channel)


def setup(bot):
    bot.add_cog(warlog(bot))
