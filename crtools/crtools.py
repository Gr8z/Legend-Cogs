import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
from cogs.utils import checks
import re

tags_path = "data/crtools/tags.json"
clans_path = "data/crtools/clans.json"

tags_bs_path = "data/crtools/tags_bs.json"
clubs_path = "data/crtools/clubs.json"

auth_path = "data/crtools/auth.json"
constants_path = "data/crtools/constants.json"

BOTCOMMANDER_ROLES = ["Family Representative", "Clan Manager",
                      "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]

default_clans = {'defualt': {'tag': '9PJYVVL2', 'role': 'everyone', 'name': 'defualt',
                             'nickname': 'defualt', 'discord': None, 'waiting': [], 'members': {},
                             'bonustitle': '', 'personalbest': 0, 'warTrophies': 0, 'approval': False,
                             'log_channel': None, 'warlog_channel': None, 'emoji': '', 'cwr': 0}}

default_clubs = {'defualt': {'tag': 'VUYG8U2', 'role': 'everyone', 'name': 'defualt',
                             'nickname': 'defualt', 'discord': None, 'waiting': [], 'members': {},
                             'bonustitle': '', 'personalbest': 0, 'approval': False,
                             'log_channel': None, 'emoji': ''}}


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

    async def card_to_rarity(self, name):
        """Card name to rarity."""
        for card in self.constants["cards"]:
            if name == card["name"]:
                return card["rarity"]
        return None

    async def get_new_level(self, card):
        """Conver the old card levels to the new ones"""
        newLevel = card.level
        if card.max_level == 11:
            newLevel = card.level + 2
        elif card.max_level == 8:
            newLevel = card.level + 5
        elif card.max_level == 5:
            newLevel = card.level + 8

        return newLevel

    async def get_region_key(self, num):
        """Get a region's key name."""
        for region in self.constants["regions"]:
            if num == region["id"]:
                return region["key"].lower()
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
        self.tags_bs = dataIO.load_json(tags_bs_path)

    async def verifyTag(self, tag):
        """Check if a player/can tag is valid"""
        check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

        if any(i not in check for i in tag):
            return False

        return True

    async def formatTag(self, tag):
        """Sanitize and format CR Tag"""
        return tag.strip('#').upper().replace('O', '0')
        return True

    async def formatName(self, name):
        """Sanitize player Name"""
        p = re.sub(r'<c\d>(.*)<\/c>', '$1', name)
        return p or name

    async def linkTagCR(self, tag, userID):
        """Link a CR player tag to a discord User"""
        tag = await self.formatTag(tag)

        self.tags.update({userID: {'tag': tag}})
        dataIO.save_json(tags_path, self.tags)

    async def unlinkTagCR(self, userID):
        """Unlink a CR player tag to a discord User"""
        if self.tags.pop(str(userID), None):
            dataIO.save_json(tags_path, self.tags)
            return True
        return False

    async def getTagCR(self, userID):
        """Get a user's CR Tag"""
        return self.tags[userID]['tag']

    async def linkTagBS(self, tag, userID):
        """Link a BS player tag to a discord User"""
        tag = await self.formatTag(tag)

        self.tags_bs.update({userID: {'tag': tag}})
        dataIO.save_json(tags_bs_path, self.tags_bs)

    async def unlinkTagBS(self, userID):
        """Unlink a BS player tag to a discord User"""
        if self.tags_bs.pop(str(userID), None):
            dataIO.save_json(tags_bs_path, self.tags_bs)
            return True
        return False

    async def getTagBS(self, userID):
        """Get a user's BS Tag"""
        return self.tags_bs[userID]['tag']

    async def getUserCR(self, serverUsers, tag):
        """Get User from CR Tag"""
        for user in serverUsers:
            if user.id in self.tags:
                player_tag = self.tags[user.id]['tag']
                if player_tag == await self.formatTag(tag):
                    return user
        return None

    async def getUserBS(self, serverUsers, tag):
        """Get User from BS Tag"""
        for user in serverUsers:
            if user.id in self.tags_bs:
                player_tag = self.tags_bs[user.id]['tag']
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
        """Add a BrawlAPI.cf Token"""
        self.auth['BrawlAPI'] = key
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
        return self.auth['BrawlAPI']


class clans:
    """CR Clan Family Management"""
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
        try:
            return self.clans[clankey]['members'][tag]['WarDayWins']
        except KeyError:
            return 0

    async def getMemberCards(self, clankey, tag):
        """Get a member's cardsEarned from the week"""
        try:
            return self.clans[clankey]['members'][tag]['cardsEarned']
        except KeyError:
            return 0

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


class clubs:
    """BS Club Family Management"""
    def __init__(self):
        self.clubs = dataIO.load_json(clubs_path)

    async def getClubs(self):
        """Return club array"""
        return self.clubs

    async def getClubData(self, clubkey, data):
        """Return club array"""
        return self.clubs[clubkey][data]

    async def getClubMemberData(self, clubkey, memberkey, data):
        """Return club member's dict"""
        return self.clubs[clubkey]['members'][memberkey][data]

    async def numClubs(self):
        """Return the number of clubs"""
        return len(self.clubs.keys())

    def keysClubs(self):
        """Get keys of all the clubs"""
        return self.clubs.keys()

    def keysClubMembers(self, clubkey):
        """Get keys of all the club members"""
        return self.clubs[clubkey]['members'].keys()

    async def namesClubs(self):
        """Get name of all the clubs"""
        return ", ".join(key for key in self.keysClubs())

    async def tagsClubs(self):
        """Get tags of all the clubs"""
        return [self.clubs[club]["tag"] for club in self.clubs]

    async def rolesClubs(self):
        """Get roles of all the clubs"""
        roles = ["Member"]
        for x in self.clubs:
            roles.append(self.clubs[x]['role'])
        return roles

    async def verifyMembership(self, clubtag):
        """Check if a club is part of the family"""
        for clubkey in self.keysClubs():
            if self.clubs[clubkey]['tag'] == clubtag:
                return True
        return False

    async def getClubKey(self, clubtag):
        """Get a club key from a club tag."""
        for clubkey in self.keysClubs():
            if self.clubs[clubkey]['tag'] == clubtag:
                return clubkey
        return None

    async def numWaiting(self, clubkey):
        """Get a club's wating list length from a club key."""
        return len(self.clubs[clubkey]['waiting'])

    async def addWaitingMember(self, clubkey, memberID):
        """Add a user to a club's waiting list"""
        if memberID not in self.clubs[clubkey]['waiting']:
            self.clubs[clubkey]['waiting'].append(memberID)
            dataIO.save_json(clubs_path, self.clubs)
            return True
        else:
            return False

    async def delWaitingMember(self, clubkey, memberID):
        """Remove a user to a club's waiting list"""
        if memberID in self.clubs[clubkey]['waiting']:
            self.clubs[clubkey]['waiting'].remove(memberID)
            dataIO.save_json(clubs_path, self.clubs)

            return True
        else:
            return False

    async def checkWaitingMember(self, clubkey, memberID):
        """check if a user is in a waiting list"""
        return memberID in self.clubs[clubkey]['waiting']

    async def getWaitingIndex(self, clubkey, memberID):
        """Get the waiting position from a club's waiting list"""
        return self.clubs[clubkey]['waiting'].index(memberID)

    async def delClub(self, clubkey):
        """delete a club from the family"""
        if self.clubs.pop(clubkey, None):
            dataIO.save_json(clubs_path, self.clubs)
            return True
        return False

    async def setPBTrophies(self, clubkey, trophies):
        """Set a club's PB Trohies"""
        self.clubs[clubkey]['personalbest'] = trophies
        dataIO.save_json(clubs_path, self.clubs)

    async def setBonus(self, clubkey, bonus):
        """Set a club's Bonus Statement"""
        self.clubs[clubkey]['bonustitle'] = bonus
        dataIO.save_json(clubs_path, self.clubs)

    async def setLogChannel(self, clubkey, channel):
        """Set a club's log channel"""
        self.clubs[clubkey]['log_channel'] = channel
        dataIO.save_json(clubs_path, self.clubs)

    async def addMember(self, clubkey, name, tag):
        """Add a member to the club"""
        self.clubs[clubkey]['members'][tag] = {}
        self.clubs[clubkey]['members'][tag]["tag"] = tag
        self.clubs[clubkey]['members'][tag]["name"] = name
        dataIO.save_json(clubs_path, self.clubs)

    async def delMember(self, clubkey, tag):
        """Remove a member to the club"""
        self.clubs[clubkey]['members'].pop(tag, None)
        dataIO.save_json(clubs_path, self.clubs)

    async def togglePrivate(self, clubkey):
        """oggle Private approval of new recruits"""
        self.clubs[clubkey]['approval'] = not self.clubs[clubkey]['approval']
        dataIO.save_json(clubs_path, self.clubs)

        return self.clubs[clubkey]['approval']


class crtools:
    """Clash Royale Tools"""
    def __init__(self, bot):
        self.bot = bot
        self.tags = tags()
        self.clans = clans()
        self.clubs = clubs()
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
        await self.bot.say("BrawlAPI Token set")

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def settokencr(self, *, key):
        """Input your Official CR API Token"""
        await self.auth.addTokenOfficial(key)
        await self.bot.say("OfficialAPI Token set")

    @commands.group(pass_context=True, name="clans")
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
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
            return await self.bot.say("Success")
        else:
            await self.bot.say("Failed")

    @_clans.command(pass_context=True, name="pb")
    async def clans_pb(self, ctx, clankey, pb: int):
        """Set a Personal Best requirement for a clan"""
        clankey = clankey.lower()
        try:
            await self.clans.setPBTrophies(clankey, pb)
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))

        await self.bot.say("Success")

    @_clans.command(pass_context=True, name="cwr")
    async def clans_cwr(self, ctx, clankey, percent: int):
        """Set a CWR requirement for a clan"""
        clankey = clankey.lower()
        try:
            await self.clans.setCWR(clankey, percent)
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))

        await self.bot.say("Success")

    @_clans.command(pass_context=True, name="bonus")
    async def clans_bonus(self, ctx, clankey, *bonus):
        """Add bonus information to title of clan (i.e. Age: 21+)"""
        clankey = clankey.lower()
        try:
            await self.clans.setBonus(clankey, " ".join(bonus))
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))

        await self.bot.say("Success")

    @_clans.command(pass_context=True, name="log")
    async def clans_log(self, ctx, clankey, channel: discord.Channel):
        """Set Clan's Log channel to track in's and outs"""
        clankey = clankey.lower()
        try:
            server = ctx.message.server

            if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
                return await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))

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
                return await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))

            if channel is None:
                await self.bot.say("I can't find the specified channel. It might have been deleted.")

            await self.clans.setWarLogChannel(clankey, channel.id)

            await self.bot.send_message(channel, "I will now send war log messages to {0.mention}".format(channel))
            await self.bot.say("Clash war log channel for {} is now set to {}".format(clankey, channel))

        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
        except discord.errors.Forbidden:
            await self.bot.say("No permission to send messages to that channel")

    @_clans.command(pass_context=True, name="private")
    async def clans_private(self, ctx, clankey):
        """Toggle Private approval of new recruits"""
        clankey = clankey.lower()
        try:
            await self.bot.say("Private Approval now is set to " + str(await self.clans.togglePrivate(clankey)))
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))

    @commands.group(pass_context=True, name="clubs")
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def _clubs(self, ctx):
        """Base command for managing clash royale clubs. [p]help clubs for details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_clubs.command(pass_context=True, name="delete")
    @checks.is_owner()
    async def clubs_delete(self, ctx, clankey):
        """Remove a clan from tracking"""
        clankey = clankey.lower()
        if await self.clubs.delClan(clankey):
            return await self.bot.say("Success")
        else:
            await self.bot.say("Failed")

    @_clubs.command(pass_context=True, name="pb")
    async def clubs_pb(self, ctx, clankey, pb: int):
        """Set a CWR requirement for a clan"""
        clankey = clankey.lower()
        try:
            await self.clubs.setCWR(clankey, pb)
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clubs.namesClubs()))

        await self.bot.say("Success")

    @_clubs.command(pass_context=True, name="bonus")
    async def clubs_bonus(self, ctx, clankey, *bonus):
        """Add bonus information to title of clan (i.e. Age: 21+)"""
        clankey = clankey.lower()
        try:
            await self.clubs.setBonus(clankey, " ".join(bonus))
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clubs.namesClubs()))

        await self.bot.say("Success")

    @_clubs.command(pass_context=True, name="log")
    async def clubs_log(self, ctx, clankey, channel: discord.Channel):
        """Set Clan's Log channel to track in's and outs"""
        clankey = clankey.lower()
        try:
            server = ctx.message.server

            if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
                return await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))

            if channel is None:
                await self.bot.say("I can't find the specified channel. It might have been deleted.")

            await self.clubs.setLogChannel(clankey, channel.id)

            await self.bot.send_message(channel, "I will now send log messages to {0.mention}".format(channel))
            await self.bot.say("Clash log channel for {} is now set to {}".format(clankey, channel))

        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clubs.namesClubs()))
            return
        except discord.errors.Forbidden:
            await self.bot.say("No permission to send messages to that channel")

    @_clubs.command(pass_context=True, name="private")
    async def clubs_private(self, ctx, clankey):
        """Toggle Private approval of new recruits"""
        clankey = clankey.lower()
        try:
            await self.bot.say("Private Approval now is set to " + str(await self.clubs.togglePrivate(clankey)))
        except KeyError:
            return await self.bot.say("Please use a valid clanname: {}".format(await self.clubs.namesClubs()))


def check_folders():
    if not os.path.exists("data/crtools"):
        print("Creating data/crtools folder...")
        os.makedirs("data/crtools")


def check_files():
    if not fileIO(tags_path, "check"):
        print("Creating empty tags.json...")
        fileIO(tags_path, "save", {"0": {"tag": "DONOTREMOVE"}})

    if not fileIO(tags_bs_path, "check"):
        print("Creating empty tags_bs.json...")
        fileIO(tags_bs_path, "save", {"0": {"tag": "DONOTREMOVE"}})

    if not fileIO(auth_path, "check"):
        print("enter your RoyaleAPI token in data/crtools/auth.json...")
        fileIO(auth_path, "save", {"OfficialAPI": "enter your OfficialAPI token here!"})

    if not fileIO(clans_path, "check"):
        print("Creating empty clans.json...")
        fileIO(clans_path, "save", default_clans)

    if not fileIO(clubs_path, "check"):
        print("Creating empty clubs.json...")
        fileIO(clubs_path, "save", default_clubs)


def check_auth():
    c = dataIO.load_json(auth_path)
    if 'RoyaleAPI' not in c:
        c['RoyaleAPI'] = "enter your RoyaleAPI token here!"
    c = dataIO.load_json(auth_path)
    if 'OfficialAPI' not in c:
        c['OfficialAPI'] = "enter your OfficialAPI token here!"
    c = dataIO.load_json(auth_path)
    if 'BrawlAPI' not in c:
        c['BrawlAPI'] = "enter your BrawlAPI token here!"
    dataIO.save_json(auth_path, c)


def setup(bot):
    check_folders()
    check_files()
    check_auth()
    bot.add_cog(crtools(bot))
