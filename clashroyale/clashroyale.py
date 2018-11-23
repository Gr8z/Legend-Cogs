import discord
from discord.ext import commands
import time
import clashroyale as clashroyaleAPI
import itertools
import re
from datetime import datetime

BOTCOMMANDER_ROLES = ["Family Representative", "Clan Manager",
                      "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"


class clashroyale:
    """Live statistics for Clash Royale"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.clans = self.bot.get_cog('crtools').clans
        self.constants = self.bot.get_cog('crtools').constants
        self.clash = clashroyaleAPI.OfficialAPI(self.auth.getOfficialToken(), is_async=True)

    def grouper(self, iterable, n):
        args = [iter(iterable)] * n
        return itertools.zip_longest(*args)

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

    async def cleanTime(self, time):
        """Converts time to timestamp"""
        return int(datetime.strptime(time, '%Y%m%dT%H%M%S.%fZ').timestamp()) + 7200

    def camelToString(self, label):
        """Convert from camel case to normal"""
        return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', label)

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name.replace(" ", "").replace("-", "").replace(".", ""):
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    async def getClanEmoji(self, tag):
        """Check if emoji exists for the clan"""
        clankey = await self.clans.getClanKey(tag.strip("#"))
        if clankey is not None:
            return await self.clans.getClanData(clankey, 'emoji')
        return self.emoji("clan")

    def getLeagueEmoji(self, trophies):
        """Get clan war League Emoji"""
        mapLeagues = {
            "legendleague": [3000, 9000],
            "gold3league": [2500, 2999],
            "gold2league": [2000, 2499],
            "goldleague": [1500, 1999],
            "silver3league": [1200, 1499],
            "silver2league": [900, 1199],
            "silverleague": [600, 899],
            "bronze3league": [400, 599],
            "bronze2league": [200, 399],
            "bronzeleague": [0, 199]
        }
        for league in mapLeagues.keys():
            if mapLeagues[league][0] <= trophies <= mapLeagues[league][1]:
                return self.emoji(league)

    def getArenaEmoji(self, trophies):
        """Get Arena and League Emoji"""
        arenaMap = {
            "arena1": [0, 399],
            "arena2": [400, 799],
            "arena3": [800, 1099],
            "arena4": [1100, 1399],
            "arena5": [1400, 1699],
            "arena6": [1700, 1999],
            "arena7": [2000, 2299],
            "arena8": [2300, 2599],
            "arena9": [2600, 2999],
            "arena10": [3000, 3399],
            "arena11": [3400, 3799],
            "arena12": [3800, 3999],
            "league1": [4000, 4299],
            "league2": [4300, 4599],
            "league3": [4600, 4899],
            "league4": [4900, 5199],
            "league5": [5200, 5499],
            "league6": [5500, 5799],
            "league7": [5800, 6099],
            "league8": [6100, 6399],
            "league9": [6400, 9999]
        }
        for arena in arenaMap.keys():
            if arenaMap[arena][0] <= trophies <= arenaMap[arena][1]:
                return self.emoji(arena)

    async def getClanLeader(self, members):
        """Return clan leader from a list of members"""
        for member in members:
            if member.role == "leader":
                arenaFormat = member.arena.name.replace(' ', '').lower()
                return "{} {}".format(self.emoji(arenaFormat), member.name)

    async def getCreaterName(self, tag, members: list):
        """Return clan leader from a list of members"""
        for member in members:
            if member.tag == tag:
                return member.name
        return ""

    async def sec2tme(self, sec):
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

    async def clanwarReadiness(self, cards):
        """Calculate clanwar readiness"""
        readiness = {}
        leagueLevels = {
            "legendary": 12,
            "gold": 11,
            "silver": 10,
            "bronze": 9
        }

        for league in leagueLevels.keys():
            readiness[league] = {"name": league.capitalize(),
                                 "percent": 0,
                                 "cards": [],
                                 "levels": str(leagueLevels[league])}
            for card in cards:
                if await self.constants.get_new_level(card) >= leagueLevels[league]:
                    readiness[league]["cards"].append(card.name)

            readiness[league]["percent"] = int((len(readiness[league]["cards"]) / len(cards)) * 100)

        readiness["gold"]["cards"] = list(set(readiness["gold"]["cards"]) -
                                          set(readiness["legendary"]["cards"]))
        readiness["silver"]["cards"] = list(set(readiness["silver"]["cards"]) -
                                            set(readiness["gold"]["cards"]) -
                                            set(readiness["legendary"]["cards"]))
        readiness["bronze"]["cards"] = list(set(readiness["bronze"]["cards"]) -
                                            set(readiness["silver"]["cards"]) -
                                            set(readiness["gold"]["cards"]) -
                                            set(readiness["legendary"]["cards"]))

        return readiness

    @commands.command(pass_context=True, aliases=['clashprofile'])
    async def clashProfile(self, ctx, member: discord.Member=None):
        """View your Clash Royale Profile Data and Statstics."""

        member = member or ctx.message.author

        await self.bot.type()
        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
        except KeyError:
            return await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))

        arenaFormat = profiledata.arena.name.replace(' ', '').lower()

        embed = discord.Embed(color=0xFAA61A)
        embed.set_author(name=profiledata.name + " ("+profiledata.tag+")",
                         icon_url=await self.constants.get_clan_image(profiledata),
                         url="https://royaleapi.com/player/"+profiledata.tag.strip("#"))
        embed.set_thumbnail(url="https://royaleapi.github.io/cr-api-assets/arenas/{}.png".format(arenaFormat))
        embed.add_field(name="Trophies", value="{} {:,}".format(self.emoji(arenaFormat), profiledata.trophies), inline=True)
        embed.add_field(name="Highest Trophies", value="{} {:,}".format(self.getArenaEmoji(profiledata.best_trophies),
                                                                        profiledata.best_trophies), inline=True)
        embed.add_field(name="Level", value=self.emoji("level{}".format(profiledata.expLevel)), inline=True)
        if profiledata.clan is not None:
            embed.add_field(name="Clan {}".format(profiledata.role.capitalize()),
                            value="{} {}".format(await self.getClanEmoji(profiledata.clan.tag), profiledata.clan.name), inline=True)
        embed.add_field(name="Cards Found", value="{} {}/89".format(self.emoji("card"), len(profiledata.cards)), inline=True)
        embed.add_field(name="Favourite Card", value="{} {}".format(self.emoji(profiledata.current_favourite_card.name),
                                                                    profiledata.current_favourite_card.name), inline=True)
        embed.add_field(name="Games Played", value="{} {:,}".format(self.emoji("battle"), profiledata.battle_count), inline=True)
        embed.add_field(name="Tourney Games Played", value="{} {:,}".format(self.emoji("tourney"), profiledata.tournament_battle_count), inline=True)
        embed.add_field(name="Wins/Draws/Losses", value="{:,}/{:,}/{:,}".format(profiledata.wins,
                                                                                profiledata.battle_count-profiledata.wins-profiledata.losses,
                                                                                profiledata.losses), inline=True)
        embed.add_field(name="War Day Wins", value="{} {}".format(self.emoji("warwin"), profiledata.war_day_wins), inline=True)
        embed.add_field(name="Three Crown Wins", value="{} {:,}".format(self.emoji("3crown"), profiledata.three_crown_wins), inline=True)
        embed.add_field(name="Total Donations", value="{} {:,}".format(self.emoji("card"), profiledata.total_donations), inline=True)
        embed.add_field(name="Donations Recieved", value="{} {:,}".format(self.emoji("card"), profiledata.clan_cards_collected), inline=True)
        embed.add_field(name="Challenge Max Wins", value="{} {}".format(self.emoji("tourney"), profiledata.challenge_max_wins), inline=True)
        embed.add_field(name="Challenge Cards Won", value="{} {:,}".format(self.emoji("cards"), profiledata.challenge_cards_won), inline=True)
        embed.add_field(name="Tournament Cards Won", value="{} {:,}".format(self.emoji("cards"), profiledata.tournament_cards_won), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def chests(self, ctx, member: discord.Member=None):
        """View your upcoming chest cycle for Clash Royale."""

        member = member or ctx.message.author

        await self.bot.type()
        try:
            profiletag = await self.tags.getTag(member.id)
            chestdata = (await self.clash.get_player_chests(profiletag)).get("items")
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
        except KeyError:
            return await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))

        mapEmoji = {
            'Silver Chest': 'silver',
            'Golden Chest': 'gold',
            'Giant Chest': 'giant',
            'Epic Chest': 'epic',
            'Super Magical Chest': 'super',
            'Magical Chest': 'magic',
            'Legendary Chest': 'legendary'
        }

        valuechestText, specialChestText = "", ""
        for chest in chestdata:
            if chest.index < 9:
                valuechestText += self.emoji(mapEmoji[chest.name]) + " "
            else:
                emojiChest = self.emoji(mapEmoji[chest.name])
                specialChestText += "{} +{} ".format(emojiChest, chest.index + 1)

        embed = discord.Embed(title="", color=0xFAA61A, description="Your Upcoming chests.")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/380832387195469826.png")
        embed.set_author(name="{} (#{})".format(member.name, profiletag))
        embed.add_field(name="Upcoming Chests", value=valuechestText, inline=False)
        embed.add_field(name="Special Chests", value=specialChestText, inline=False)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, aliases=['clashdeck'])
    async def clashDeck(self, ctx, member: discord.Member=None):
        """View yours or other's clash royale Deck"""

        member = member or ctx.message.author

        await self.bot.type()

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
        except KeyError:
            return await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))

        message = ctx.message
        message.content = ctx.prefix + "deck gl " + await self.constants.decklink_url(profiledata.current_deck)
        message.author = member

        await self.bot.process_commands(message)

    @commands.command(pass_context=True, aliases=['cwr'])
    async def clanwarreadiness(self, ctx, member: discord.Member=None):
        """View yours or other's clash royale CWR"""

        member = member or ctx.message.author

        await self.bot.type()

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            leagues = await self.clanwarReadiness(profiledata.cards)
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
        except KeyError:
            return await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))

        embed = discord.Embed(color=0xFAA61A, description="Clan War Readiness")
        embed.set_author(name=profiledata.name + " ("+profiledata.tag+")",
                         icon_url=await self.constants.get_clan_image(profiledata),
                         url="https://royaleapi.com/player/"+profiledata.tag.strip("#"))
        embed.add_field(name="War Day Wins", value="{} {}".format(self.emoji("warwin"), profiledata.war_day_wins), inline=True)
        embed.add_field(name="War Cards Collected", value="{} {}".format(self.emoji("card"), profiledata.clan_cards_collected), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        for league in leagues.keys():
            f_title = "{} League (Lvl {}) - {}%".format(leagues[league]["name"], leagues[league]["levels"], leagues[league]["percent"])
            groups = self.grouper(leagues[league]["cards"], 30)
            for index, cards in enumerate(groups):
                value = ""
                for card in cards:
                    if card is not None:
                        value += self.emoji(card)
                embed.add_field(name=f_title if index == 0 else '\u200b', value=value, inline=False)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def clan(self, ctx, clantag):
        """View Clash Royale Clan statistics and information """

        await self.bot.type()

        clantag = await self.tags.formatTag(clantag)

        if not await self.tags.verifyTag(clantag):
            return await self.bot.say("The ID you provided has invalid characters. Please try again.")

        try:
            clandata = await self.clash.get_clan(clantag)
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")

        embed = discord.Embed(description=clandata.description, color=0xFAA61A)
        embed.set_author(name=clandata.name + " ("+clandata.tag+")",
                         icon_url=await self.constants.get_clan_image(clandata),
                         url="https://legendclans.com/clanInfo/"+clandata.tag.strip("#"))
        embed.set_thumbnail(url=await self.constants.get_clan_image(clandata))
        embed.add_field(name="Members", value="{} {}/50".format(self.emoji("members"), clandata.get("members")), inline=True)
        embed.add_field(name="Leader", value=await self.getClanLeader(clandata.member_list), inline=True)
        embed.add_field(name="Donations", value="{} {:,}".format(self.emoji("cards"), clandata.donations_per_week), inline=True)
        embed.add_field(name="Score", value="{} {:,}".format(self.emoji("PB"), clandata.clan_score), inline=True)
        embed.add_field(name="War Trophies",
                        value="{} {:,}".format(self.getLeagueEmoji(clandata.clan_war_trophies), clandata.clan_war_trophies), inline=True)
        embed.add_field(name="Required Trophies",
                        value="{} {:,}".format(self.emoji("crtrophy"), clandata.required_trophies), inline=True)
        embed.add_field(name="Status", value=":envelope_with_arrow: {}".format(self.camelToString(clandata.type).capitalize()), inline=True)
        if clandata.location.is_country:
            embed.add_field(name="Country",
                            value=":flag_{}: {}".format(await self.constants.get_region_key(clandata.location.id),
                                                        clandata.location.name), inline=True)
        else:
            embed.add_field(name="Location", value=":earth_americas: {}".format(clandata.location.name), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, aliases=['cw'])
    async def tournament(self, ctx, tag, password=None):
        """View Clash Royale Tournament Information """

        await self.bot.type()

        tag = await self.tags.formatTag(tag)

        if not await self.tags.verifyTag(tag):
            return await self.bot.say("The ID you provided has invalid characters. Please try again.")

        try:
            tourneydata = await self.clash.get_tournament(tag)
        except clashroyaleAPI.NotFoundError:
            return await self.bot.say("Error: Tournament not found. Please double check your #TAG")
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")

        maxPlayers = tourneydata.max_capacity
        cards = self.getCards(maxPlayers)
        coins = self.getCoins(maxPlayers)

        embed = discord.Embed(title="Click this link to join the Tournament in Clash Royale!",
                              url="https://legendclans.com/tournaments?id={}&pass={}".format(tag, password), color=0xFAA61A)
        embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

        embed.set_author(name="{} ({})".format(tourneydata.name, tourneydata.tag),
                         url="https://royaleapi.com/tournament/" + tourneydata.tag.strip("#"))

        embed.add_field(name="Players", value="{} {}/{}".format(self.emoji("members"),
                                                                tourneydata.capacity,
                                                                maxPlayers), inline=True)
        embed.add_field(name="Status", value=self.camelToString(tourneydata.status).capitalize(), inline=True)

        tourneydata.open = True if tourneydata.type == "open" else False
        if not tourneydata.open:
            if password is not None:
                embed.add_field(name="Password", value="```{}```".format(password), inline=True)
            else:
                return await self.bot.say("Error: Please enter a tournament password.")

        await self.bot.delete_message(ctx.message)

        if tourneydata.status != "ended":
            tourneydata.created_time = await self.cleanTime(tourneydata.created_time)
            if tourneydata.status != "inProgress":
                startTime = await self.sec2tme((tourneydata.created_time + tourneydata.preparation_duration) - int(time.time()))
                embed.add_field(name="Starts In", value=startTime, inline=True)

            endTime = await self.sec2tme((tourneydata.created_time + tourneydata.preparation_duration + tourneydata.duration) - int(time.time()))
            embed.add_field(name="Ends In", value=endTime, inline=True)

        embed.add_field(name="Hosted By", value=await self.getCreaterName(tourneydata.creator_tag, tourneydata.members_list), inline=True)

        if tourneydata.first_place_card_prize > 0:
            embed.add_field(name="Top prize", value="{} {}     {} {}".format(self.emoji("tournamentcards"),
                                                                             cards,
                                                                             self.emoji("coin"),
                                                                             coins), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def save(self, ctx, profiletag: str, member: discord.Member=None):
        """ save your Clash Royale Profile Tag

        Example:
            [p]save #CRRYTPTT @GR8
            [p]save #CRRYRPCC
        """

        server = ctx.message.server
        author = ctx.message.author

        profiletag = await self.tags.formatTag(profiletag)

        if not await self.tags.verifyTag(profiletag):
            return await self.bot.say("The ID you provided has invalid characters. Please try again.")

        await self.bot.type()

        allowed = False
        if member is None:
            allowed = True
        elif member.id == author.id:
            allowed = True
        else:
            botcommander_roles = [discord.utils.get(server.roles, name=r) for r in BOTCOMMANDER_ROLES]
            botcommander_roles = set(botcommander_roles)
            author_roles = set(author.roles)
            if len(author_roles.intersection(botcommander_roles)):
                allowed = True

        if not allowed:
            return await self.bot.say("You dont have enough permissions to set tags for others.")

        member = member or ctx.message.author

        try:
            profiledata = await self.clash.get_player(profiletag)

            checkUser = await self.tags.getUser(server.members, profiletag)
            if checkUser is not None:
                return await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")

            await self.tags.linkTag(profiletag, member.id)

            embed = discord.Embed(color=discord.Color.green())
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed.set_author(name='{} (#{}) has been successfully saved.'.format(profiledata.name, profiletag),
                             icon_url=avatar)
            await self.bot.say(embed=embed)
        except clashroyaleAPI.NotFoundError:
            return await self.bot.say("We cannot find your ID in our database, please try again.")
        except clashroyaleAPI.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")


def setup(bot):
    bot.add_cog(clashroyale(bot))
