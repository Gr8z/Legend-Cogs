import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
from __main__ import send_cmd_help
import time
import clashroyale as clashroyaleAPI

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
        self.clash = clashroyaleAPI.Client(self.auth.getToken(), is_async=True)

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

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name:
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    async def getClanEmoji(self, tag):
        """Check if emoji exists for the clan"""
        clankey = await self.clans.getClanKey(tag)
        if clankey is not None:
            return await self.clans.getClanData(clankey, 'emoji')
        return self.emoji("clan")

    def getLeagueEmoji(self, trophies):
        """Get clan war League Emoji"""
        if trophies >= 3000:
            return self.emoji("legendleague")
        elif trophies >= 1500:
            return self.emoji("goldleague")
        elif trophies >= 600:
            return self.emoji("silverleague")
        else:
            return self.emoji("bronzeleague")

    async def getClanWarTrophies(self, tag):
        """Check if war trophies exists for the clan"""
        clankey = await self.clans.getClanKey(tag)
        if clankey is not None:
            return await self.clans.getClanData(clankey, 'warTrophies')
        return None

    async def getClanLeader(self, members):
        """Return clan leader from a list of members"""
        for member in members:
            if member.role == "leader":
                arenaFormat = member.arena.arena.replace(' ', '').lower()
                return "{} {}".format(self.emoji(arenaFormat), member.name)

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

    @commands.command(pass_context=True, aliases=['clashprofile'])
    async def clashProfile(self, ctx, member: discord.Member=None):
        """View your Clash Royale Profile Data and Statstics."""

        member = member or ctx.message.author

        await self.bot.type()
        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
        except clashroyaleAPI.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))
            return

        if profiledata.clan is None:
            clanurl = "https://i.imgur.com/4EH5hUn.png"
        else:
            clanurl = profiledata.clan.badge.image

        arenaFormat = profiledata.arena.arena.replace(' ', '').lower()

        embed = discord.Embed(color=0xFAA61A)
        embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", icon_url=clanurl, url="https://royaleapi.com/player/"+profiledata.tag)
        embed.set_thumbnail(url="https://royaleapi.github.io/cr-api-assets/arenas/{}.png".format(arenaFormat))
        embed.add_field(name="Trophies", value="{} {:,}".format(self.emoji(arenaFormat), profiledata.trophies), inline=True)
        embed.add_field(name="Highest Trophies", value="{} {:,}".format(self.emoji(arenaFormat), profiledata.stats.max_trophies), inline=True)
        embed.add_field(name="Level", value="{} {}".format(self.emoji("level"), profiledata.stats.level), inline=True)
        if profiledata.clan is not None:
            embed.add_field(name="Clan {}".format(profiledata.clan.role.capitalize()),
                            value="{} {}".format(await self.getClanEmoji(profiledata.clan.tag), profiledata.clan.name), inline=True)
        embed.add_field(name="Cards Found", value="{} {}/86".format(self.emoji("card"), profiledata.stats.cards_found), inline=True)
        embed.add_field(name="Favourite Card", value="{} {}".format(self.emoji(profiledata.stats.favorite_card.name.replace(" ", "")),
                                                                    profiledata.stats.favorite_card.name), inline=True)
        embed.add_field(name="Games Played", value="{} {:,}".format(self.emoji("battle"), profiledata.games.total), inline=True)
        embed.add_field(name="Tourney Games Played", value="{} {:,}".format(self.emoji("tourney"), profiledata.games.tournament_games), inline=True)
        embed.add_field(name="Wins/Draws/Losses", value="{:,}/{:,}/{:,}".format(profiledata.games.wins, profiledata.games.draws,
                                                                                profiledata.games.losses), inline=True)
        embed.add_field(name="War Day Wins", value="{} {}".format(self.emoji("warwin"), profiledata.games.war_day_wins), inline=True)
        embed.add_field(name="Three Crown Wins", value="{} {:,}".format(self.emoji("3crown"), profiledata.stats.three_crown_wins), inline=True)
        embed.add_field(name="Total Donations", value="{} {:,}".format(self.emoji("card"), profiledata.stats.total_donations), inline=True)
        embed.add_field(name="Donations Recieved", value="{} {:,}".format(self.emoji("card"), profiledata.stats.clan_cards_collected), inline=True)
        embed.add_field(name="Challenge Max Wins", value="{} {}".format(self.emoji("tourney"), profiledata.stats.challenge_max_wins), inline=True)
        embed.add_field(name="Challenge Cards Won", value="{} {:,}".format(self.emoji("cards"), profiledata.stats.challenge_cards_won), inline=True)
        embed.add_field(name="Tournament Cards Won", value="{} {:,}".format(self.emoji("cards"), profiledata.stats.tournament_cards_won), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def chests(self, ctx, member: discord.Member=None):
        """View your upcoming chest cycle for Clash Royale."""

        member = member or ctx.message.author

        await self.bot.type()
        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player_chests(profiletag)
        except clashroyaleAPI.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))
            return

        mapEmoji = {
            'silver': 'silver'
            'gold': 'gold'
            'giant': 'giant'
            'epic': 'epic'
            'super magical': 'super'
            'magical': 'magic'
            'legendary': 'legendary'
        }

        valuechestText = ' '.join(profiledata.upcoming)
        for chest in mapEmoji.keys():
            valuechestText = valuechestText.replace(chest, self.emoji(mapEmoji[chest]))

        chestList = [
            "{} +{}".format(self.emoji("giant"), profiledata.giant+1),
            "{} +{}".format(self.emoji("epic"), profiledata.epic+1),
            "{} +{}".format(self.emoji("magic"), profiledata.magical+1),
            "{} +{}".format(self.emoji("super"), profiledata.super_magical+1),
            "{} +{}".format(self.emoji("legendary"), profiledata.legendary+1),
        ]

        embed = discord.Embed(title="", color=0xFAA61A, description="Your Upcoming chests.")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/385784630227369985.png")
        embed.set_author(name="{} (#{})".format(member.name, profiletag))
        embed.add_field(name="Upcoming Chests", value=valuechestText, inline=False)
        embed.add_field(name="Special Chests", value=" ".join(chestList), inline=False)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, aliases=['clashdeck'])
    async def clashDeck(self, ctx, member: discord.Member=None):
        """View yours or other's clash royale Deck"""

        member = member or ctx.message.author

        await self.bot.type()

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag, keys="deckLink")
        except clashroyaleAPI.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You need to first save your profile using ``{}save #GAMETAG``".format(ctx.prefix))
            return

        message = ctx.message
        message.content = ctx.prefix + "deck gl " + profiledata.deck_link
        message.author = member

        await self.bot.process_commands(message)

    @commands.command(pass_context=True)
    async def clan(self, ctx, clantag):
        """View Clash Royale Clan statistics and information """

        await self.bot.type()

        try:
            clandata = await self.clash.get_clan(clantag)
        except clashroyaleAPI.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        embed = discord.Embed(description=clandata.description, color=0xFAA61A)
        embed.set_author(name=clandata.name + " (#"+clandata.tag+")",
                         icon_url=clandata.badge.image,
                         url="https://legendclans.com/clanInfo/"+clandata.tag)
        embed.set_thumbnail(url=clandata.badge.image)
        embed.add_field(name="Members", value="{} {}/50".format(self.emoji("members"), clandata.member_count), inline=True)
        embed.add_field(name="Leader", value=await self.getClanLeader(clandata.members), inline=True)
        embed.add_field(name="Donations", value="{} {:,}".format(self.emoji("cards"), clandata.donations), inline=True)
        embed.add_field(name="Score", value="{} {:,}".format(self.emoji("PB"), clandata.score), inline=True)

        warTrophies = await self.getClanWarTrophies(clandata.tag)
        if warTrophies is not None:
            embed.add_field(name="War Trophies",
                            value="{} {:,}".format(self.getLeagueEmoji(warTrophies), warTrophies), inline=True)

        embed.add_field(name="Required Trophies",
                        value="{} {:,}".format(self.emoji("crtrophy"), clandata.required_score), inline=True)
        embed.add_field(name="Status", value=":envelope_with_arrow: {}".format(clandata.type.title()), inline=True)
        if clandata.location.is_country:
            embed.add_field(name="Country",
                            value=":flag_{}: {}".format(clandata.location.code.lower(), clandata.location.name), inline=True)
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
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

        await self.bot.delete_message(ctx.message)

        try:
            tourneydata = await self.clash.get_tournament(tag)
        except clashroyaleAPI.RequestError:
            await self.bot.say("Error: Tournament not found. Please double check your #TAG")
            return

        maxPlayers = tourneydata.max_players
        cards = self.getCards(maxPlayers)
        coins = self.getCoins(maxPlayers)

        embed = discord.Embed(title="Click this link to join the Tournament in Clash Royale!",
                              url="https://legendclans.com/tournaments?id={}&pass={}".format(tag, password), color=0xFAA61A)
        embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

        embed.set_author(name="{} (#{})".format(tourneydata.name, tourneydata.tag),
                         url="https://royaleapi.com/tournament/" + tourneydata.tag)

        embed.add_field(name="Players", value="{} {}/{}".format(self.emoji("members"),
                                                                tourneydata.current_players,
                                                                maxPlayers), inline=True)
        embed.add_field(name="Status", value=tourneydata.status.title(), inline=True)

        if not tourneydata.open:
            if password is not None:
                embed.add_field(name="Password", value="```{}```".format(password), inline=True)
            else:
                await self.bot.say("Error: Please enter a tournament password.")
                return

        if tourneydata.status != "ended":

            if tourneydata.status != "inProgress":
                startTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time) - int(time.time()))
                embed.add_field(name="Starts In", value=startTime, inline=True)

            endTime = self.sec2tme((tourneydata.create_time + tourneydata.prep_time + tourneydata.duration) - int(time.time()))
            embed.add_field(name="Ends In", value=endTime, inline=True)

        embed.add_field(name="Hosted By", value=tourneydata.creator.name, inline=True)
        embed.add_field(name="Top prize", value="{} {}     {} {}".format(self.emoji("tournamentcards"),
                                                                         cards,
                                                                         self.emoji("coin"),
                                                                         coins), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
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
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

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
            await self.bot.say("You dont have enough permissions to set tags for others.")
            return

        member = member or ctx.message.author

        try:
            profiledata = await self.clash.get_player(profiletag)

            checkUser = await self.tags.getUser(server.members, profiletag)
            if checkUser is not None:
                await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")
                return

            await self.tags.linkTag(profiletag, member.id)

            embed = discord.Embed(color=discord.Color.green())
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed.set_author(name='{} (#{}) has been successfully saved.'.format(profiledata.name, profiletag),
                             icon_url=avatar)
            await self.bot.say(embed=embed)
        except clashroyaleAPI.NotFoundError:
            await self.bot.say("We cannot find your ID in our database, please try again.")
            return
        except clashroyaleAPI.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return


def setup(bot):
    bot.add_cog(clashroyale(bot))
