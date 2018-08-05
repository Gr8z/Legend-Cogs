import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
from cogs.utils import checks

tags_path = "data/crtools/tags.json"
auth_path = "data/crtools/auth.json"
clans_path = "data/crtools/clans.json"
constants_path = "data/crtools/constants.json"

default_clans = {'defualt': {'tag': '9PJYVVL2', 'role': 'everyone', 'name': 'defualt',
                             'nickname': 'defualt', 'discord': None, 'waiting': [], 'members': {},
                             'bonustitle': '', 'personalbest': 0, 'warTrophies': 0, 'approval': False,
                             'log_channel': None, 'warlog_channel': None, 'emoji': '', 'cwr': 0}}


class constants:
    """constants Management"""
    def __init__(self):
        self.constants = dataIO.load_json(constants_path)
        self.images = 'https://royaleapi.github.io/cr-api-assets/'

    async def card_to_key(self, name):
        """Card key to decklink id."""
        for card in self.constants["cards"]:
            if name == card["name"]:
                return str(card["id"])
        return None

    async def get_region_key(self, num):
        """Get a region's key name."""
        for region in self.constants["region"]:
            if num == region["id"]:
                return region["key"]
        return None

    async def decklink_url(self, deck, war=False):
        """Decklink URL."""
        ids = []
        for card in deck:
            ids.append(await self.card_to_key(card["name"]))
        url = 'https://link.clashroyale.com/deck/en?deck=' + ';'.join(ids)
        if war:
            url += '&ID=CRRYRPCC&war=1'
        return url

    async def get_clan_image(self, p):
        """Get clan badge URL from badge ID"""
        try:
            badge_id = p.clan.badge_id
        except AttributeError:
            try:
                badge_id = p.badge_id
            except AttributeError:
                return 'https://i.imgur.com/Y3uXsgj.png'

        if badge_id is None:
            return 'https://i.imgur.com/Y3uXsgj.png'

        for i in self.constants["alliance_badges"]:
            if i["id"] == badge_id:
                return self.images + 'badges/' + i["name"] + '.png'


class tags:
    """Tags Management"""
    def __init__(self):
        self.tags = dataIO.load_json(tags_path)

    async def verifyTag(self, tag):
        """Check if a player/can tag is valid"""
        check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

        if any(i not in check for i in tag):
            return False

        return True

    async def formatTag(self, tag):
        """Sanitize and format CR Tag"""
        return tag.strip('#').upper().replace('O', '0')

    async def linkTag(self, tag, userID):
        """Link a player tag to a discord User"""
        tag = await self.formatTag(tag)

        self.tags.update({userID: {'tag': tag}})
        dataIO.save_json(tags_path, self.tags)

    async def unlinkTag(self, userID):
        """Unlink a player tag to a discord User"""
        if self.c.pop(str(userID), None):
            dataIO.save_json(tags_path, self.tags)
            return True
        return False

    async def getTag(self, userID):
        """Get a user's CR Tag"""
        return self.tags[userID]['tag']

    async def getUser(self, serverUsers, tag):
        """Get User from CR Tag"""
        for user in serverUsers:
            if user.id in self.tags:
                player_tag = self.tags[user.id]['tag']
                if player_tag == await self.formatTag(tag):
                    return user
        return None


class auth:
    """RoyaleAPI key management"""
    def __init__(self):
        self.auth = dataIO.load_json(auth_path)

    async def addToken(self, key):
        """Add a RoyaleAPI Token"""
        self.auth['RoyaleAPI'] = key
        dataIO.save_json(auth_path, self.auth)

    async def addTokenBS(self, key):
        """Add a brawlstars-api Token"""
        self.auth['brawlstars-api'] = key
        dataIO.save_json(auth_path, self.auth)

    async def addTokenOfficial(self, key):
        """Add a api.clashroyal.com Token"""
        self.auth['OfficialAPI'] = key
        dataIO.save_json(auth_path, self.auth)

    def getToken(self):
        """Get RoyaleAPI Token"""
        return self.auth['RoyaleAPI']

    def getOfficialToken(self):
        """Get OfficialAPI Token"""
        return self.auth['OfficialAPI']

    def getBSToken(self):
        """Get brawlstars-api Token"""
        return self.auth['brawlstars-api']


class clans:
    """Clan Family Management"""
    def __init__(self):
        self.clans = dataIO.load_json(clans_path)

    async def getClans(self):
        """Return clan array"""
        return self.clans

    async def getClanData(self, clankey, data):
        """Return clan array"""
        return self.clans[clankey][data]

    async def getClanMemberData(self, clankey, memberkey, data):
        """Return clan member's dict"""
        return self.clans[clankey]['members'][memberkey][data]

    async def numClans(self):
        """Return the number of clans"""
        return len(self.clans.keys())

    def keysClans(self):
        """Get keys of all the clans"""
        return self.clans.keys()

    def keysClanMembers(self, clankey):
        """Get keys of all the clan members"""
        return self.clans[clankey]['members'].keys()

    async def namesClans(self):
        """Get name of all the clans"""
        return ", ".join(key for key in self.keysClans())

    async def tagsClans(self):
        """Get tags of all the clans"""
        return [self.clans[clan]["tag"] for clan in self.clans]

    async def rolesClans(self):
        """Get roles of all the clans"""
        roles = ["Member"]
        for x in self.clans:
            roles.append(self.clans[x]['role'])
        return roles

    async def verifyMembership(self, clantag):
        """Check if a clan is part of the family"""
        for clankey in self.keysClans():
            if self.clans[clankey]['tag'] == clantag:
                return True
        return False

    async def getClanKey(self, clantag):
        """Get a clan key from a clan tag."""
        for clankey in self.keysClans():
            if self.clans[clankey]['tag'] == clantag:
                return clankey
        return None

    async def numWaiting(self, clankey):
        """Get a clan's wating list length from a clan key."""
        return len(self.clans[clankey]['waiting'])

    async def setWarTrophies(self, clankey, trophies):
        """Set a clan's wartrophies"""
        self.clans[clankey]['warTrophies'] = trophies
        dataIO.save_json(clans_path, self.clans)

    async def setWarstats(self, clankey, tag, trophies, cards):
        """Set a clan member's wins and cards"""
        self.clans[clankey]['members'][tag]['WarDayWins'] = trophies
        self.clans[clankey]['members'][tag]['cardsEarned'] = cards
        dataIO.save_json(clans_path, self.clans)

    async def getMemberWins(self, clankey, tag):
        """Get a member's war day wins from the week"""
        return self.clans[clankey]['members'][tag]['WarDayWins']

    async def getMemberCards(self, clankey, tag):
        """Get a member's cardsEarned from the week"""
        return self.clans[clankey]['members'][tag]['cardsEarned']

    async def addWaitingMember(self, clankey, memberID):
        """Add a user to a clan's waiting list"""
        if memberID not in self.clans[clankey]['waiting']:
            self.clans[clankey]['waiting'].append(memberID)
            dataIO.save_json(clans_path, self.clans)
            return True
        else:
            return False

    async def delWaitingMember(self, clankey, memberID):
        """Remove a user to a clan's waiting list"""
        if memberID in self.clans[clankey]['waiting']:
            self.clans[clankey]['waiting'].remove(memberID)
            dataIO.save_json(clans_path, self.clans)

            return True
        else:
            return False

    async def checkWaitingMember(self, clankey, memberID):
        """check if a user is in a waiting list"""
        return memberID in self.clans[clankey]['waiting']

    async def getWaitingIndex(self, clankey, memberID):
        """Get the waiting position from a clan's waiting list"""
        return self.clans[clankey]['waiting'].index(memberID)

    async def delClan(self, clankey):
        """delete a clan from the family"""
        if self.clans.pop(clankey, None):
            dataIO.save_json(clans_path, self.clans)
            return True
        return False

    async def setPBTrophies(self, clankey, trophies):
        """Set a clan's PB Trohies"""
        self.clans[clankey]['personalbest'] = trophies
        dataIO.save_json(clans_path, self.clans)

    async def setCWR(self, clankey, cwr):
        """Set a clan's CWR"""
        self.clans[clankey]['cwr'] = cwr
        dataIO.save_json(clans_path, self.clans)

    async def setBonus(self, clankey, bonus):
        """Set a clan's Bonus Statement"""
        self.clans[clankey]['bonustitle'] = bonus
        dataIO.save_json(clans_path, self.clans)

    async def setLogChannel(self, clankey, channel):
        """Set a clan's log channel"""
        self.clans[clankey]['log_channel'] = channel
        dataIO.save_json(clans_path, self.clans)

    async def setWarLogChannel(self, clankey, channel):
        """Set a clan's warlog channel"""
        self.clans[clankey]['warlog_channel'] = channel
        dataIO.save_json(clans_path, self.clans)

    async def addMember(self, clankey, name, tag):
        """Add a member to the clan"""
        self.clans[clankey]['members'][tag] = {}
        self.clans[clankey]['members'][tag]["tag"] = tag
        self.clans[clankey]['members'][tag]["name"] = name
        self.clans[clankey]['members'][tag]["WarDayWins"] = 0
        self.clans[clankey]['members'][tag]["cardsEarned"] = 0
        dataIO.save_json(clans_path, self.clans)

    async def delMember(self, clankey, tag):
        """Remove a member to the clan"""
        self.clans[clankey]['members'].pop(tag, None)
        dataIO.save_json(clans_path, self.clans)

    async def togglePrivate(self, clankey):
        """oggle Private approval of new recruits"""
        self.clans[clankey]['approval'] = not self.clans[clankey]['approval']
        dataIO.save_json(clans_path, self.clans)

        return self.clans[clankey]['approval']


class crtools:
    """Clash Royale Tools"""
    def __init__(self, bot):
        self.bot = bot
        self.tags = tags()
        self.clans = clans()
        self.auth = auth()
        self.constants = constants()

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def settoken(self, *, key):
        """Input your Clash Royale API Token from RoyaleAPI.com"""
        await self.auth.addToken(key)
        await self.bot.say("RoyaleAPI Token set")

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def settokenbs(self, *, key):
        """Input your BrawlStars API Token"""
        await self.auth.addTokenBS(key)
        await self.bot.say("brawlstars-api Token set")

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def settokencr(self, *, key):
        """Input your Official CR API Token"""
        await self.auth.addTokenOfficial(key)
        await self.bot.say("OfficialAPI Token set")

    @commands.group(pass_context=True, name="clans")
    @checks.mod_or_permissions(administrator=True)
    async def _clans(self, ctx):
        """Base command for managing clash royale clans. [p]help clans for details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_clans.command(pass_context=True, name="delete")
    @checks.is_owner()
    async def clans_delete(self, ctx, clankey):
        """Remove a clan from tracking"""
        clankey = clankey.lower()
        if await self.clans.delClan(clankey):
            await self.bot.say("Success")
            return
        else:
            await self.bot.say("Failed")

    @_clans.command(pass_context=True, name="pb")
    async def clans_pb(self, ctx, clankey, pb: int):
        """Set a Personal Best requirement for a clan"""
        clankey = clankey.lower()
        try:
            await self.clans.setPBTrophies(clankey, pb)
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        await self.bot.say("Success")

    @_clans.command(pass_context=True, name="cwr")
    async def clans_cwr(self, ctx, clankey, percent: int):
        """Set a CWR requirement for a clan"""
        clankey = clankey.lower()
        try:
            await self.clans.setCWR(clankey, percent)
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        await self.bot.say("Success")

    @_clans.command(pass_context=True, name="bonus")
    async def clans_bonus(self, ctx, clankey, *bonus):
        """Add bonus information to title of clan (i.e. Age: 21+)"""
        clankey = clankey.lower()
        try:
            await self.clans.setBonus(clankey, " ".join(bonus))
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        await self.bot.say("Success")

    @_clans.command(pass_context=True, name="log")
    async def clans_log(self, ctx, clankey, channel: discord.Channel):
        """Set Clan's Log channel to track in's and outs"""
        clankey = clankey.lower()
        try:
            server = ctx.message.server

            if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
                await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))
                return

            if channel is None:
                await self.bot.say("I can't find the specified channel. It might have been deleted.")

            await self.clans.setLogChannel(clankey, channel.id)

            await self.bot.send_message(channel, "I will now send log messages to {0.mention}".format(channel))
            await self.bot.say("Clash log channel for {} is now set to {}".format(clankey, channel))

        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return
        except discord.errors.Forbidden:
            await self.bot.say("No permission to send messages to that channel")

    @_clans.command(pass_context=True, name="war")
    async def clans_warlog(self, ctx, clankey, channel: discord.Channel):
        """Set Clan's War Log channel to track wins"""
        clankey = clankey.lower()
        try:
            server = ctx.message.server

            if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
                await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))
                return

            if channel is None:
                await self.bot.say("I can't find the specified channel. It might have been deleted.")

            await self.clans.setWarLogChannel(clankey, channel.id)

            await self.bot.send_message(channel, "I will now send war log messages to {0.mention}".format(channel))
            await self.bot.say("Clash war log channel for {} is now set to {}".format(clankey, channel))

        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return
        except discord.errors.Forbidden:
            await self.bot.say("No permission to send messages to that channel")

    @_clans.command(pass_context=True, name="private")
    async def clans_private(self, ctx, clankey):
        """Toggle Private approval of new recruits"""
        clankey = clankey.lower()
        try:
            await self.bot.say("Private Approval now is set to " + str(await self.clans.togglePrivate(clankey)))
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return


def check_folders():
    if not os.path.exists("data/crtools"):
        print("Creating data/crtools folder...")
        os.makedirs("data/crtools")


def check_files():
    if not fileIO(tags_path, "check"):
        print("Creating empty tags.json...")
        fileIO(tags_path, "save", {"0": {"tag": "DONOTREMOVE"}})

    if not fileIO(auth_path, "check"):
        print("enter your RoyaleAPI token in data/crtools/auth.json...")
        fileIO(auth_path, "save", {"token": "enter your RoyaleAPI token here!"})

    if not fileIO(clans_path, "check"):
        print("Creating empty clans.json...")
        fileIO(clans_path, "save", default_clans)


def check_auth():
    c = dataIO.load_json(auth_path)
    if 'RoyaleAPI' not in c:
        c['RoyaleAPI'] = "enter your RoyaleAPI token here!"
    dataIO.save_json(auth_path, c)


def setup(bot):
    check_folders()
    check_files()
    check_auth()
    bot.add_cog(crtools(bot))
