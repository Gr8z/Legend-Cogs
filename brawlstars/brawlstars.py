import discord
from discord.ext import commands
import brawlstats

BOTCOMMANDER_ROLES = ["Family Representative", "Clan Manager",
                      "Club Manager", "Club Deputy", "Vice President",
                      "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Apex"


class brawlstars:
    """Live statistics for Brawl Stars"""

    def __init__(self, bot):
        self.bot = bot
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.clubs = self.bot.get_cog('crtools').clubs
        self.brawl = brawlstats.Client(self.auth.getBSToken(), is_async=False)

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name.replace(" ", "").replace("-", "").replace(".", ""):
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    async def getClanEmoji(self, tag):
        """Check if emoji exists for the clan"""
        clankey = await self.clubs.getBandKey(tag.strip("#"))
        if clankey is not None:
            return await self.clubs.getBandData(clankey, 'emoji')
        return self.emoji("clan")

    def getLeagueEmoji(self, trophies):
        """Get clan war League Emoji"""
        mapLeagues = {
            "starLeague": [10000, 90000],
            "masterLeague": [8000, 9999],
            "crystalLeague": [6000, 7999],
            "diamondLeague": [4000, 5999],
            "goldLeague": [3000, 3999],
            "silverLeague": [2000, 2999],
            "bronzeLeague": [1000, 1999],
            "woodLeague": [0, 999]
        }
        for league in mapLeagues.keys():
            if mapLeagues[league][0] <= trophies <= mapLeagues[league][1]:
                return self.emoji(league)

    async def getClanLeader(self, members):
        """Return clan leader from a list of members"""
        for member in members:
            if member.role == "President":
                return "{} {}".format(self.getLeagueEmoji(member.trophies), await self.tags.formatName(member.name))

    async def getCreaterName(self, tag, members: list):
        """Return clan leader from a list of members"""
        for member in members:
            if member.tag == tag:
                return member.name
        return ""

    @commands.command(pass_context=True, aliases=['brawlprofile'])
    async def brawlProfile(self, ctx, member: discord.Member = None):
        """View your Brawl Stars Profile Data and Statstics."""

        member = member or ctx.message.author

        await self.bot.type()
        try:
            profiletag = await self.tags.getTagBS(member.id)
            profiledata = self.brawl.get_player(profiletag)
        except brawlstats.RequestError as e:
            return await self.bot.say('```\n{}: {}\n```'.format(e.code, e.error))
        except KeyError:
            return await self.bot.say("You need to first save your profile using ``{}bsave #GAMETAG``".format(ctx.prefix))

        embed = discord.Embed(color=0xFAA61A)
        embed.set_author(name="{} (#{})".format(await self.tags.formatName(profiledata.name), profiledata.tag),
                         icon_url=profiledata.club.badge_url if profiledata.club is not None else "",
                         url="https://brawlstats.com/profile/" + profiledata.tag)
        embed.set_thumbnail(url=profiledata.avatar_url)
        embed.add_field(name="Trophies", value="{} {:,}".format(self.getLeagueEmoji(profiledata.trophies), profiledata.trophies), inline=True)
        embed.add_field(name="Highest Trophies", value="{} {:,}".format(self.getLeagueEmoji(profiledata.highest_trophies), profiledata.highest_trophies), inline=True)
        embed.add_field(name="Level", value="{} {:,}".format(self.emoji("xp"), profiledata.exp_level), inline=True)
        if profiledata.club is not None:
            embed.add_field(name="Club {}".format(profiledata.club.role),
                            value=profiledata.club.name, inline=True)
        embed.add_field(name="Brawlers Unlocked", value="{} {}/22".format(self.emoji("default"), profiledata.brawlers_unlocked), inline=True)
        embed.add_field(name="Victories", value="{} {}".format(self.emoji("bountystar"), profiledata.victories), inline=True)
        embed.add_field(name="Solo SD Victories", value="{} {}".format(self.emoji("showdown"), profiledata.solo_showdown_victories), inline=True)
        embed.add_field(name="Duo SD Victories", value="{} {}".format(self.emoji("duoshowdown"), profiledata.duo_showdown_victories), inline=True)
        embed.add_field(name="Best Time as Big Brawler", value="{} {}".format(self.emoji("bossfight"), profiledata.best_time_as_big_brawler), inline=True)
        embed.add_field(name="Best Robo Rumble Time", value="{} {}".format(self.emoji("roborumble"), profiledata.best_robo_rumble_time), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def club(self, ctx, clantag):
        """View Brawl Stars Club statistics and information """

        await self.bot.type()

        clantag = await self.tags.formatTag(clantag)

        if not await self.tags.verifyTag(clantag):
            return await self.bot.say("The ID you provided has invalid characters. Please try again.")

        try:
            clandata = self.brawl.get_club(clantag)
        except brawlstats.RequestError:
            return await self.bot.say("Error: cannot reach Brawl Stars Servers. Please try again later.")

        embed = discord.Embed(description=clandata.description, color=0xFAA61A)
        embed.set_author(name=clandata.name + " (#" + clandata.tag + ")",
                         icon_url=clandata.badge_url,
                         url="https://legendclans.com/clanInfo/" + clandata.tag)
        embed.set_thumbnail(url=clandata.badge_url)
        embed.add_field(name="Members", value="{} {}/100".format(self.emoji("gameroom"), clandata.members_count), inline=True)
        embed.add_field(name="President", value=await self.getClanLeader(clandata.get('members')), inline=True)
        embed.add_field(name="Online", value="{} {:,}".format(self.emoji("online"), clandata.online_members), inline=True)
        embed.add_field(name="Score", value="{} {:,}".format(self.emoji("bstrophy2"), clandata.trophies), inline=True)
        embed.add_field(name="Required Trophies",
                        value="{} {:,}".format(self.emoji("bstrophy"), clandata.required_trophies), inline=True)
        embed.add_field(name="Status", value=":envelope_with_arrow: {}".format(clandata.status), inline=True)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True, aliases=['bssave'])
    async def bsave(self, ctx, profiletag: str, member: discord.Member = None):
        """ save your Brawl Stars Profile Tag

        Example:
            [p]bssave #CRRYTPTT @GR8
            [p]bssave #CRRYRPCC
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
            profiledata = self.brawl.get_player(profiletag)

            checkUser = await self.tags.getUserBS(server.members, profiletag)
            if checkUser is not None:
                return await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")

            await self.tags.linkTagBS(profiletag, member.id)

            embed = discord.Embed(color=discord.Color.green())
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed.set_author(name='{} (#{}) has been successfully saved.'.format(await self.tags.formatName(profiledata.name), profiletag),
                             icon_url=avatar)
            await self.bot.say(embed=embed)
        except brawlstats.NotFoundError:
            return await self.bot.say("We cannot find your ID in our database, please try again.")
        except brawlstats.RequestError:
            return await self.bot.say("Error: cannot reach Brawl Stars Servers. Please try again later.")


def setup(bot):
    bot.add_cog(brawlstars(bot))
