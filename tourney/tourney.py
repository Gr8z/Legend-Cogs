import discord
from discord.ext import commands
import asyncio
import time
import clashroyale

lastTag = '0'
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

BOTCOMMANDER_ROLES = ["Family Representative", "Clan Manager", "Clan Deputy",
                      "Co-Leader", "Hub Officer", "admin", "Member", "guest"]


class tournament:
    """tournament!"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = self.bot.get_cog('crtools').auth
        self.clash = clashroyale.RoyaleAPI(self.auth.getToken(), is_async=True)
        self.clashAPI = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)

    def getCards(self, maxPlayers):
        """Converts maxPlayers to Cards"""
        cards = {
            "50": 25,
            "100": 100,
            "200": 400,
            "1000": 2000
        }
        return cards[str(maxPlayers)]

    def getCoins(self, maxPlayers):
        """Converts maxPlayers to Coins"""
        coins = {
            "50": 175,
            "100": 700,
            "200": 2800,
            "1000": 14000
        }
        return coins[str(maxPlayers)]

    def sec2tme(self, sec):
        """Converts seconds to readable time"""
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)

        if h is 0:
            if m is 0:
                return "{} seconds".format(s)
            else:
                return "{} minutes, {} secs".format(m, s)
        else:
            return "{} hour, {} mins".format(h, m)

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name:
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    # Returns a list with tournaments
    async def getTopTourney(self):

        global lastTag
        try:
            openTourney = await self.clash.get_joinable_tournaments()
        except clashroyale.RequestError:
            return None

        for tourney in openTourney:

            tag = tourney.tag
            joined = tourney.current_players
            maxplayers = tourney.max_players
            createTime = tourney.create_time

            if (((int(time.time()) - createTime) < 10800) and (maxplayers > 50) and ((joined + 4) < maxplayers) and (tag != lastTag)):

                try:
                    tourneyAPI = await self.clashAPI.get_tournament(tag)
                    joined = tourneyAPI.capacity
                    maxplayers = tourneyAPI.max_capacity
                    tourneyAPI.open = True if tourneyAPI.type == "open" else False
                except clashroyale.RequestError:
                    return None

                if ((maxplayers > 50) and ((joined + 4) < maxplayers) and (tourneyAPI.status != "ended") and (tourneyAPI.open) and (tourneyAPI.first_place_card_prize > 0)):
                    lastTag = tag
                    return tourneyAPI

        return None

    # Returns a list with tournaments
    async def getRandomTourney(self):

        try:
            openTourney = await self.clash.get_joinable_tournaments()
        except clashroyale.RequestError:
            return None

        for tourney in openTourney:

            tag = tourney.tag
            joined = tourney.current_players
            maxplayers = tourney.max_players
            createTime = tourney.create_time

            if (((int(time.time()) - createTime) < 10800) and ((joined + 1) < maxplayers)):

                try:
                    tourneyAPI = await self.clashAPI.get_tournament(tag)
                    joined = tourneyAPI.capacity
                    maxplayers = tourneyAPI.max_capacity
                    tourneyAPI.open = True if tourneyAPI.type == "open" else False
                except clashroyale.RequestError:
                    return None

                if ((joined < maxplayers) and (tourneyAPI.status != "ended") and (tourneyAPI.open) and (tourneyAPI.first_place_card_prize > 0)):
                    return tourneyAPI

        return None

    # checks for a tourney every 5 minutes
    async def checkTourney(self):
        server = [x for x in self.bot.servers if x.id == "374596069989810176"][0]
        role_name = "Tournaments"
        if role_name is not None:
            tour_role = discord.utils.get(server.roles, name=role_name)
            if tour_role is None:
                await self.bot.create_role(server, name=role_name)
                tour_role = discord.utils.get(server.roles, name=role_name)

        while self is self.bot.get_cog("tournament"):
            tourneydata = await self.getTopTourney()
            if tourneydata is not None:
                maxPlayers = tourneydata.max_players
                cards = self.getCards(maxPlayers)
                coins = self.getCoins(maxPlayers)

                embed = discord.Embed(title="Click this link to join the Tournament in Clash Royale!",
                                      url="https://legendclans.com/tournaments?id={}".format(tourneydata.tag),
                                      color=0xFAA61A)
                embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

                embed.set_author(name="{} (#{})".format(tourneydata.name, tourneydata.tag),
                                 url="https://royaleapi.com/tournament/" + tourneydata.tag)

                embed.add_field(name="Players", value="{} {}/{}".format(self.emoji("members"),
                                tourneydata.current_players, maxPlayers), inline=True)
                embed.add_field(name="Status", value=tourneydata.status.title(), inline=True)

                if tourneydata.status != "inProgress":
                    startTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time) - int(time.time()))
                    embed.add_field(name="Starts In", value=startTime, inline=True)

                endTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time + tourneydata.duration) - int(time.time()))
                embed.add_field(name="Ends In", value=endTime, inline=True)

                embed.add_field(name="Top prize", value="{} {}     {} {}".format(self.emoji("tournamentcards"),
                                                                                 cards,
                                                                                 self.emoji("coin"),
                                                                                 coins), inline=True)
                embed.set_footer(text=credits, icon_url=creditIcon)

                await self.bot.edit_role(server, tour_role, mentionable=True)
                await self.bot.send_message(discord.Object(id='374597050530136064'),
                                            content="{}. Type ``!r tournaments`` to turn on tournament notifications.".format(tour_role.mention),
                                            embed=embed)
                await self.bot.edit_role(server, tour_role, mentionable=False)
                await asyncio.sleep(900)
            await asyncio.sleep(120)

    @commands.command()
    @commands.cooldown(3, 60, commands.BucketType.server)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def tourney(self):
        """ Get a open tournament"""

        await self.bot.type()

        tourneydata = await self.getRandomTourney()

        if tourneydata is not None:
            maxPlayers = tourneydata.max_players
            cards = self.getCards(maxPlayers)
            coins = self.getCoins(maxPlayers)

            embed = discord.Embed(title="Click this link to join the Tournament in Clash Royale!", url="https://legendclans.com/tournaments?id={}".format(tourneydata.tag), color=0xFAA61A)
            embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

            embed.set_author(name="{} (#{})".format(tourneydata.name, tourneydata.tag), url="https://royaleapi.com/tournament/" + tourneydata.tag)

            embed.add_field(name="Players", value="{} {}/{}".format(self.emoji("members"), tourneydata.current_players, maxPlayers), inline=True)
            embed.add_field(name="Status", value=tourneydata.status.title(), inline=True)

            if tourneydata.status != "inProgress":
                startTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time) - int(time.time()))
                embed.add_field(name="Starts In", value=startTime, inline=True)

            endTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time + tourneydata.duration) - int(time.time()))
            embed.add_field(name="Ends In", value=endTime, inline=True)

            embed.add_field(name="Top prize", value="{} {}     {} {}".format(self.emoji("tournamentcards"), cards, self.emoji("coin"), coins), inline=True)
            embed.set_footer(text=credits, icon_url=creditIcon)
            await self.bot.say(embed=embed)
        else:
            return await self.bot.say("Found nothing, please try again after a few minutes!")


def setup(bot):
    n = tournament(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.checkTourney())
    bot.add_cog(n)
