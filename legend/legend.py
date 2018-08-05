import discord
from discord.ext import commands
import os
from .utils.dataIO import dataIO, fileIO
import asyncio
import random
from random import choice as rand_choice
import string
import datetime
import time
from collections import OrderedDict
import clashroyale
import requests

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"
BOTCOMMANDER_ROLES = ["Family Representative", "Clan Manager",
                      "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]

rules_text = """**Here are some Legend Family Discord server rules.**\n
• No Hateful, obscene, offensive, racist, sexual or violent words allowed in chat or images.
• Respect others' opinions. If you disagree, please do so in a constructive manner.
• This is an English only server, please use any other languages in a private message.
• Do not spam, and avoid ever using @myclanname without permission from clan managers or deputies.
• No advertisement of any kind, e.g. clans, websites, discord invites.
• Use #bot-spam for bot features, e.g. !deck or !payday
• Obtaining credits or reputations using unethical ways like cheating or trading is strictly forbidden
• Respect and do not subvert moderators and managers.
• A good rule is to talk to people as if you were talking to them face to face.
• There are more rules that vary from clan to clan. Ask your clan leader for the rules of your clan.\n
**Clan Transfer**\n
• If you are transferring from one Legend Family clan to another, please contact your destination clan's clan leader first, 
and wait for the all clear from that clan leader. We are all for members being wherever they want to be, but it helps us keep track of what is going on, and helps us make sure you get accepted.
• If you are leaving the clan for another reason, please talk with your leader first when possible. As a clan leader it helps to know if you're leaving for good, if you're leaving to do 2v2 with a few friends for a while, or if you're leaving for an eSport event.\n
**Violation of these roles will lead to punishment including temporary guest role reduced access, temporary kick from server, or permanent kick from server, depending on the severity and/or frequency of the offense**"""

commands_text = """Here are some of the Legend Family Bot commands, you can use them in the #bot-spam channel.\n
**!clashProfile** - to view your Clash Royale stats.
**!clashDeck** - to view your Clash Royale current deck.
**!chests** - to view your upcoming chests you will receive.
**!cwr** - to view your clan war readiness for your card levels.
**!tourney** - to instantly recieve an open tournament that is available to join.
**!topmembers** - shows the top ranked players in our family.
**!payday** - receive your 300 credits every 30 minutes.
**!heist** - Play a heist with a crew in #heist channel.
**!duel** - Challenge someone for a duel and win credits in #duels channel.
**!buy** - Take a look at what you can purchase with your credits.
**!balance** - To check your current bank balance.
**!profile** - view your server profile.
**!deck** - make and save your deck.
**!legend** - to see status of all Legend Family clans.
**!rep @user** - give reputation points to users.
**!remindme** - Use this command to make the bot remind you of something in the future.
**!trivia** - start a trivia of your choice. Bot will ask you questions, you will get points of answering them.
**!play** - Listen to songs, type with command with the song name inside a voice channel. (!skip, !pause, !resume, !playlist).
**!invite** - Get the invite link for the server to share with your friends.
**!report** - Report a user to the moderators for breaking the rules.
**!coaching** - To request a coaching session.\n
**You can type !help here to see the full commands list**"""

info_text = """You will find several channels on our Discord Server\n
**#global-chat**: to discuss about the game.
**#tourneys**: Dozens of tournaments posted everyday.
**#news**: important info about family.
**#giveaways**: Win Discord credits and game keys every day.
**#deck-recommendation**: decks discussion.
**#off-topic**: you can chat about anything unrelated to clash royale here.
**#bots-spam**: Use bot commands, You can mute the channels you don't need in DISCORD settings.
**#heist**: Play Heist mini game with a crew and get lots of credits.
**#duels**: Challenge or accept duel offers for a Clash Royale Battle.
**#challenges**: Word and number challenge games with other members. Answer all the questions before any one else to win.
**#friends-forever**: Post your Clash friend invite link or add others.
"""
cw_info = """We organize **Legend Wars** every weekend, which aims to determine **which clan is the strongest**.

The **idea** is simple: A private tournament that anyone may join **within Legend Family and the alliance.**
Score is calculated in a way that allows every participant to contribute to help their clan win.  We sum the earned tournament trophies of the members of each clan to calculate a clan score, clan with highest clan score is declared the **winner**!

There are 2 factors to win: convince more players to participate within your clan and earn more tournament trophies. Both are **equally important**. We publish tourneys and passwords at same time, so we give equal chances to each clan and player.

The Top player in each war will recieve $10. However, each and every participant will recieve discord credits for getting trophies for their clan. The more trophies you can collect, the more credits you will get. Credits can used in LeGeND shop to buy various items.

**All clans** will be closed/full to avoid any leaks, nobody will be allowed to join.

**3 golden Rules for Legend Wars:** We respect the Opponent (no BMing if you win), we play to have fun (no obligation to participate), and don't join if you think you cannot play.
"""

credits_info = """**WHAT ARE CREDITS?**
Credits are a virtual currency in LeGeND Discord, you earn credits by playing in Legend Wars, donating, and playing mini games in discord. To use your credits, you can buy items using !buy.

• Every 30 minutes, you can get free credits by typing !payday in #bot-spam channel.
• Every Sunday, you receive something called a "Weekly Payout". Which converts all your week's clan donations, War Cards collected and War wins into credits. So the more active you are in a clan, the more credits you get.
• We have Legend Wars every weekend, participating in these wars also give you tons of credits according to your tournament trophies.
• You can also win credits by playing #heist and #challenges.
• You can play Clash Royale #duels to bet on your skills in friend battles.
• Last but not least, you can get easy credits by just chatting on discord. The more you chat, the more credits you accumulate.

You can type !buy here to look at different ways you can spend these credits.
"""

esports_info = """**The LeGeND eSports Team** is recruiting all active and aspiring players!

With the goal of encouraging competitive play in the family, there is a LeGeND eSports **Americas** and **Eurasia** team to represent the family in various events. Our strongest players will compete side by side with the very best in leagues such as **CCTS, CPL, and even RPL**!

While we have a clan called LeGeND eSports!, the team operates separately from the clan, and sends members from our family to events.

But please remember that this is a more professional setting than the rest of the family and **poor behaviour will not be tolerated**. 

Join now: https://discord.gg/ck8nGEN

Please note that if you just lurk in the server and not participate for a long period of time you will be kicked off the server.
"""

coc_bs = """We also play **Clash of Clans** and **Brawl Stars**, we would like to invite to you join them if you play either of these supercell games.

• Clash of Clans - **LeGeND Raiders! (#JQJRGVJU)** - https://discord.gg/BG7wMFw
• Brawl Stars - **LeGeND Platoon! (#QVLUCGP)**

You can send a request to join with the message "from LEGEND". Let us know when you have joined so we can unlock clan channels for you.
"""

social_info = """Stay Social! Come and follow us on these platforms to stay up to date on the latest news and announcements.

https://twitter.com/TheLegendClans
https://www.facebook.com/LegendClans
https://www.instagram.com/legendclans

Visit our website to see live clan statistics:
https://legendclans.com
"""

guest_rules = """Welcome to the **Legend Family** Discord server. As a guest, you agree to follow the following rules:

• Respect others' opinions. If you disagree, please do so in a constructive manner.
• This is an English only server, please use any other languages in a private message.
• Do not spam, and avoid ever using @clanname without permission from clan managers or deputies.
• No advertisement of any kind, e.g. clans, websites, discord invites.
• Use #bot-spam for bot features, e.g. !deck or !payday
• Respect and do not subvert moderators and managers.
• A good rule is to talk to people as if you were talking to them face to face.

Failure to follow these rules will get you kicked from the server. Repeat offenders will be banned.

You can chat with family members and guests in `#global-chat`. For games, you can check out `#heist` `#duels` and `#challenges`.

If you would like to invite your friends to join this server, you may use this Discord invite: <http://discord.gg/T7XdjFS>

Additional help and information: https://legendclans.com

Thanks + enjoy!
"""


class legend:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json('data/legend/settings.json')
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.clans = self.bot.get_cog('crtools').clans
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)
        self.welcome = dataIO.load_json('data/legend/welcome.json')
        self.bank = dataIO.load_json('data/economy/bank.json')
        self.seen = dataIO.load_json('data/seen/seen.json')

    async def updateSeen(self):
        self.seen = dataIO.load_json('data/seen/seen.json')

    def save_settings(self):
        """Saves the json"""
        dataIO.save_json('data/legend/settings.json', self.settings)

    async def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    async def _add_roles(self, member, role_names):
        """Add roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.add_roles(member, *roles)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

    async def _remove_roles(self, member, role_names):
        """Remove roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.remove_roles(member, *roles)
        except:
            pass

    async def _is_commander(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in BOTCOMMANDER_ROLES]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    async def _is_member(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Member",
                                                                                "Co-Leader",
                                                                                "Hub Officer",
                                                                                "Clan Deputy",
                                                                                "Clan Manager"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    async def getLeague(self, trophies):
        if trophies >= 3000:
            return "legend"
        elif trophies >= 1500:
            return "gold"
        elif trophies >= 600:
            return "silver"
        else:
            return "bronze"

    async def getBestLeague(self, cards):
        """Get best leagues using readiness"""
        readiness = await self.clanwarReadiness(cards)

        legend = readiness["legend"]
        gold = readiness["gold"] - legend
        silver = readiness["silver"] - gold - legend
        bronze = readiness["bronze"] - silver - gold - legend

        readinessCount = {"legend": legend, "gold": gold, "silver": silver, "bronze": bronze}
        max_key = max(readinessCount, key=lambda k: readinessCount[k])

        return "{} League ({}%)".format(max_key.capitalize(), readiness[max_key])

    async def getBestPerc(self, cards, league):
        """Get best leagues level perc using readiness"""
        readiness = await self.clanwarReadiness(cards)
        return readiness[league]

    async def clanwarReadiness(self, cards):
        """Calculate clanwar readiness"""
        count = 0
        readiness = {
            "legend": 0,
            "gold": 0,
            "silver": 0,
            "bronze": 0
        }
        leagueLevels = {
            "legend": [12, 10, 7, 4],
            "gold": [11, 9, 6, 3],
            "silver": [10, 8, 5, 2],
            "bronze": [9, 7, 4, 1]
        }

        for card in cards:
            for league in leagueLevels.keys():
                if card.max_level == 13:
                    overlevel = card.level >= leagueLevels[league][0]
                elif card.max_level == 11:
                    overlevel = card.level >= leagueLevels[league][1]
                elif card.max_level == 8:
                    overlevel = card.level >= leagueLevels[league][2]
                elif card.max_level == 5:
                    overlevel = card.level >= leagueLevels[league][3]

                if overlevel:
                    readiness[league] += 1
            count += 1

        for levels in readiness.keys():
            readiness[levels] = int((readiness[levels] / count) * 100)

        return readiness

    @commands.command(pass_context=True)
    async def legend(self, ctx, member: discord.Member=None):
        """ Show Legend clans, can also show clans based on a member's trophies"""

        await self.bot.type()
        if member is None:
            trophies = 9999
            maxtrophies = 9999
            plyrLeagueCWR = 0
        else:
            try:
                await self.bot.type()
                profiletag = await self.tags.getTag(member.id)
                profiledata = await self.clash.get_player(profiletag)
                trophies = profiledata.trophies
                cards = profiledata.cards
                maxtrophies = profiledata.best_trophies
                plyrLeagueCWR = 0

                if profiledata.clan is None:
                    clanname = "*None*"
                else:
                    clanname = profiledata.clan.name

                ign = profiledata.name
            except clashroyale.RequestError:
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
            except KeyError:
                await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
                return

        clandata = []
        for clankey in self.clans.keysClans():
            try:
                clan = await self.clash.get_clan(await self.clans.getClanData(clankey, 'tag'))
                clandata.append(clan)
            except clashroyale.RequestError:
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return

        clandata = sorted(clandata, key=lambda x: (x.required_trophies, x.clan_score), reverse=True)

        embed = discord.Embed(color=0xFAA61A)
        if "url" in self.settings and "family" in self.settings:
            embed.set_author(name=self.settings['family'], url=self.settings['url'],
                             icon_url="https://i.imgur.com/dtSMITE.jpg")
        else:
            embed.set_author(name="Legend Family Clans",
                             url="http://royaleapi.com/clan/family/legend",
                             icon_url="https://i.imgur.com/dtSMITE.jpg")

        embed.set_footer(text=credits, icon_url=creditIcon)

        foundClan = False
        totalMembers = 0
        totalWaiting = 0
        for clan in clandata:
            numWaiting = 0
            personalbest = 0
            bonustitle = None

            clankey = await self.clans.getClanKey(clan.tag.strip("#"))
            numWaiting = await self.clans.numWaiting(clankey)
            personalbest = await self.clans.getClanData(clankey, 'personalbest')
            cwr = await self.clans.getClanData(clankey, 'cwr')
            bonustitle = await self.clans.getClanData(clankey, 'bonustitle')
            emoji = await self.clans.getClanData(clankey, 'emoji')
            warTrophies = await self.clans.getClanData(clankey, 'warTrophies')
            totalWaiting += numWaiting

            if numWaiting > 0:
                title = "["+str(numWaiting)+" Waiting] "
            else:
                title = ""

            member_count = clan.get("members")
            totalMembers += member_count
            if member_count < 50:
                showMembers = str(member_count) + "/50"
            else:
                showMembers = "**FULL**  "

            if str(clan.type) != 'inviteOnly':
                title += "["+str(clan.type).title()+"] "

            title += clan.name + " (" + clan.tag + ") "

            if personalbest > 0:
                title += "PB: "+str(personalbest)+"+  "

            if cwr > 0:
                title += "CWR: "+str(cwr)+"%  "
                if member is not None:
                    plyrLeagueCWR = await self.getBestPerc(cards, await self.getLeague(warTrophies))

            if bonustitle is not None:
                title += bonustitle

            desc = ("{} {}  <:crtrophy:448609948008579073> "
                    "{}+  <:wartrophy:448609141796241408> {}".format(emoji,
                                                                     showMembers,
                                                                     clan.required_trophies,
                                                                     warTrophies))

            if (member is None) or ((clan.required_trophies <= trophies) and
                                    (maxtrophies > personalbest) and
                                    (plyrLeagueCWR >= cwr) and
                                    (trophies - clan.required_trophies < 1200) and
                                    (clan.type != 'closed')):
                foundClan = True
                embed.add_field(name=title, value=desc, inline=False)

        if not foundClan:
            embed.add_field(name="uh oh!",
                            value="There are no clans available for you at the moment, "
                            "please type !legend to see all clans.",
                            inline=False)

        embed.description = ("Our Family is made up of {} "
                             "clans with a total of {} "
                             "members. We have {} spots left "
                             "and {} members in waiting lists.".format(await self.clans.numClans(),
                                                                       totalMembers,
                                                                       (await self.clans.numClans()*50)-totalMembers,
                                                                       totalWaiting))
        await self.bot.say(embed=embed)

        if member is not None:
            await self.bot.say(("Hello **{}**, above are all the clans "
                                "you are allowed to join, based on your statistics. "
                                "Which clan would you like to join? \n\n"
                                "**Name:** {} (#{})\n**Trophies:** {}/{}\n"
                                "**CW Readiness:** {}\n"
                                "**Clan:** {}\n\n"
                                ":warning: **PLEASE DO NOT REQUEST TO "
                                "JOIN ANY CLANS IF YOU HAVE NOT YET "
                                "RECIEVED YOUR RECRUIT CODE!**".format(ign,
                                                                       ign,
                                                                       profiletag,
                                                                       trophies,
                                                                       maxtrophies,
                                                                       await self.getBestLeague(cards),
                                                                       clanname)))

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def approve(self, ctx, member: discord.Member, clankey):
        """Send instructions to people joining a clan"""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = await self.clans.getClanData(clankey, 'tag')
            clan_name = await self.clans.getClanData(clankey, 'name')
            clan_role = await self.clans.getClanData(clankey, 'role')
            clan_pb = await self.clans.getClanData(clankey, 'personalbest')
            clan_cwr = await self.clans.getClanData(clankey, 'cwr')
            clan_approval = await self.clans.getClanData(clankey, 'approval')
            clan_war = await self.clans.getClanData(clankey, 'warTrophies')
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        leftClan = False
        try:
            await self.bot.type()
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            clandata = await self.clash.get_clan(clan_tag)

            ign = profiledata.name
            if profiledata.clan is None:
                leftClan = True
                clantag = ""
            else:
                clantag = profiledata.clan.tag.strip("#")
        except clashroyale.RequestError:
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
        except KeyError:
            await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
            return

        membership = not await self.clans.verifyMembership(clantag)

        if membership:

            trophies = profiledata.trophies
            cards = profiledata.cards
            maxtrophies = profiledata.best_trophies
            plyrLeagueCWR = await self.getBestPerc(cards, await self.getLeague(clan_war))

            if (clandata.get("members") == 50):
                await self.bot.say("Approval failed, the clan is Full.")
                return

            if ((trophies < clandata.required_trophies) and (maxtrophies < clan_pb)):
                await self.bot.say("Approval failed, you don't meet the trophy requirements.")
                return

            if (plyrLeagueCWR < clan_cwr):
                await self.bot.say("Approval failed, you don't meet the CW Readiness requirements.")
                return

            if (clandata.type == "closed"):
                await self.bot.say("Approval failed, the clan is currently closed.")
                return

            if clan_approval:
                if clan_role in [y.name.lower() for y in member.roles]:
                    await self.bot.say("Approval failed, only {} staff can approve new recruits for this clan.".format(clan_name))
                return

            if await self.clans.numWaiting(clankey) > 0:
                if await self.clans.checkWaitingMember(clankey, member.id):
                    canWait = (50 - clandata.get("members")) - 1

                    if await self.clans.getWaitingIndex(clankey, member.id) > canWait:
                        await self.bot.say("Approval failed, you are not first in queue for the waiting list on this server.")
                        return

                    await self.clans.delWaitingMember(clankey, member.id)

                    role = discord.utils.get(server.roles, name="Waiting")
                    try:
                        await self.bot.remove_roles(member, role)
                    except discord.Forbidden:
                        raise
                    except discord.HTTPException:
                        raise
                else:
                    await self.bot.say("Approval failed, there is a waiting queue for this clan. Please first join the waiting list.")
                    return

            if not leftClan:
                warning = ("\n\n:warning: **PLEASE DO NOT REQUEST TO "
                           "JOIN ANY CLANS IF YOU HAVE NOT YET "
                           "RECIEVED YOUR RECRUIT CODE!**")
                await self.bot.say(("{} Please leave your current clan now. "
                                    "Your recruit code will arrive in 3 minutes.{}".format(member.mention, warning)))
                await asyncio.sleep(180)

            try:
                recruitCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

                await self.bot.send_message(member, "Congratulations, You have been approved to join **" + clan_name +
                                                    " (#" + clan_tag + ")**.\n\n\n" +
                                                    "Your **RECRUIT CODE** is: ``" + recruitCode + "`` \n" +
                                                    "Send this code in the join request message.\n\n" +
                                                    "Click this link to join the clan: https://legendclans.com/clanInfo/" +
                                                    clan_tag + "\n\n" +
                                                    "That's it! Now wait for your clan leadership to accept you. \n" +
                                                    "If you do not see a 'request to join' button, make sure you leave " +
                                                    "your current clan and check the trophy requirements. \n\n" +
                                                    "**IMPORTANT**: Once your clan leadership has accepted your request, " +
                                                    "let a staff member in discord know that you have been accepted. " +
                                                    "They will then unlock all the member channels for you.")
                await self.bot.say(member.mention + " has been approved for **" + clan_name + "**. Please check your DM for instructions on how to join.")

                try:
                    newname = ign + " (Approved)"
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")

                roleName = discord.utils.get(server.roles, name=clan_role)

                embed = discord.Embed(color=0x0080ff)
                embed.set_author(name="New Recruit", icon_url="https://i.imgur.com/dtSMITE.jpg")
                embed.add_field(name="Name", value=ign, inline=True)
                embed.add_field(name="Recruit Code", value=recruitCode, inline=True)
                embed.add_field(name="Clan", value=clan_name, inline=True)
                embed.set_footer(text=credits, icon_url=creditIcon)

                await self.bot.send_message(discord.Object(id='375839851955748874'), content=roleName.mention, embed=embed)
            except discord.errors.Forbidden:
                await self.bot.say("Approval failed, {} please fix your privacy settings, we are unable to send you Direct Messages.".format(member.mention))
        else:
            await self.bot.say("Approval failed, You are already a part of a clan in the family.")

    @commands.command(pass_context=True, no_pm=True)
    async def newmember(self, ctx, member: discord.Member):
        """Setup nickname, roles and invite links for a new member"""

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        isMember = await self._is_member(member)
        if isMember:
            await self.bot.say("Error, " + member.mention + " is not a new member.")
            return

        try:
            await self.bot.type()
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            if profiledata.clan is None:
                clantag = ""
                clanname = ""
            else:
                clantag = profiledata.clan.tag.strip("#")
                clanname = profiledata.clan.name

            ign = profiledata.name
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
            return

        allowed = False
        if member is None:
            allowed = True
        elif member.id == author.id:
            allowed = True
        else:
            allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to use this command on others.")
            return

        membership = await self.clans.verifyMembership(clantag)

        if membership:

            try:
                savekey = await self.clans.getClanKey(clantag)
                invite = await self.clans.getClanData(savekey, 'discord')
                if invite is not None:
                    joinLink = "https://discord.gg/" + str(invite)
                    await self.bot.send_message(member, "Hi There! Congratulations on getting accepted into our family. " +
                                                        "We have unlocked all the member channels for you in LeGeND Discord Server. " +
                                                        "Now you have to carefuly read this message and follow the steps mentioned below: \n\n" +
                                                        "Please click on the link below to join your clan Discord server. \n\n" +
                                                        clanname + ": " + joinLink + "\n\n" +
                                                        "Please do not leave our main or clan servers while you are in the clan. Thank you.")
                else:

                    await self.bot.send_message(member, "Hi There! Congratulations on getting accepted into our family. "
                                                        "We have unlocked all the member channels for you in LeGeND Discord Server. \n\n" +
                                                        "Please do not leave our Discord server while you are in the clan. Thank you.")
            except discord.errors.Forbidden:
                await self.bot.say(("Membership failed, {} please fix your privacy settings, "
                                    "we are unable to send you Direct Messages.".format(member.mention)))
                return

            await self.clans.delWaitingMember(savekey, member.id)

            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = await self.clans.getClanData(savekey, 'nickname')
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                else:
                    mymessage += "Nickname changed to **{}**\n".format(newname)

            role_names = [await self.clans.getClanData(savekey, 'role'), 'Member']
            try:
                await self._add_roles(member, role_names)
                mymessage += "**" + await self.clans.getClanData(savekey, 'role') + "** and **Member** roles added."
            except discord.Forbidden:
                await self.bot.say(
                    "{} does not have permission to edit {}’s roles.".format(
                        author.display_name, member.display_name))
            except discord.HTTPException:
                await self.bot.say("failed to add {}.".format(', '.join(role_names)))

            await self.bot.say(mymessage)

            welcomeMsg = rand_choice(self.welcome["GREETING"])
            await self.bot.send_message(discord.Object(id='374596069989810178'), welcomeMsg.format(member, server))

            await self._remove_roles(member, ['Guest'])

            roleName = discord.utils.get(server.roles, name=role_names[0])
            await self.bot.send_message(discord.Object(id='375839851955748874'),
                                        "**{}** recruited **{} (#{})** to {}".format(ctx.message.author.display_name,
                                                                                     ign,
                                                                                     profiletag,
                                                                                     roleName.mention))
            await asyncio.sleep(300)
            await self.bot.send_message(member, rules_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member, commands_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member, info_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member, cw_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member, credits_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member, coc_bs)

            await asyncio.sleep(300)
            await self.bot.send_message(member, esports_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member, social_info)
        else:
            await self.bot.say("You must be accepted into a clan before I can give you clan roles. "
                               "Would you like me to check again in 2 minutes? (Yes/No)")

            answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)

            if answer is None:
                return
            elif "yes" not in answer.content.lower():
                return

            await self.bot.say("Okay, I will retry this command in 2 minutes.")
            await asyncio.sleep(120)
            message = ctx.message
            message.content = ctx.prefix + "newmember {}".format(member.mention)
            await self.bot.process_commands(message)

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def waiting(self, ctx, member: discord.Member, clankey):
        """Add people to the waiting list for a clan"""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = await self.clans.getClanData(clankey, 'tag')
            clan_name = await self.clans.getClanData(clankey, 'name')
            clan_pb = await self.clans.getClanData(clankey, 'personalbest')
            clan_cwr = await self.clans.getClanData(clankey, 'cwr')
            clan_war = await self.clans.getClanData(clankey, 'warTrophies')
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        try:
            await self.bot.type()
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            clandata = await self.clash.get_clan(clan_tag)

            ign = profiledata.name
            trophies = profiledata.trophies
            cards = profiledata.cards
            maxtrophies = profiledata.best_trophies

            plyrLeagueCWR = await self.getBestPerc(cards, await self.getLeague(clan_war))
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
            return

        if ((trophies < clandata.required_trophies) and (maxtrophies < clan_pb)):
            await self.bot.say("Cannot add you to the waiting list, you don't meet the trophy requirements.")
            return

        if (plyrLeagueCWR < clan_cwr):
                await self.bot.say("Cannot add you to the waiting lists, you don't meet the CW Readiness requirements.")
                return

        if not await self.clans.addWaitingMember(clankey, member.id):
            await self.bot.say("You are already in a waiting list for this clan.")
            return

        role = discord.utils.get(server.roles, name="Waiting")
        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise
        await self.bot.say(member.mention + " You have been added to the waiting list for **" +
                           clan_name +
                           "**. We will mention you when a spot is available.")

        roleName = discord.utils.get(server.roles, name=await self.clans.getClanData(clankey, 'role'))
        await self.bot.send_message(discord.Object(id='375839851955748874'), "**{} (#{})** added to the waiting list for {}".format(ign, profiletag, roleName.mention))

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def remove(self, ctx, member: discord.Member, clankey):
        """Delete people from the waiting list for a clan"""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_name = await self.clans.getClanData(clankey, 'name')
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        try:
            await self.clans.delWaitingMember(clankey, member.id)

            role = discord.utils.get(server.roles, name="Waiting")
            try:
                await self.bot.remove_roles(member, role)
            except discord.Forbidden:
                raise
            except discord.HTTPException:
                raise
            await self.bot.say(member.mention + " has been removed from the waiting list for **" + clan_name + "**.")
        except ValueError:
            await self.bot.say("Recruit not found in the waiting list.")

    @commands.command(pass_context=True, no_pm=True, aliases=["waitlist", "wait"])
    async def waitinglist(self, ctx):
        """Show status of the waiting list."""

        message = ""
        counterClans = 0
        counterPlayers = 0

        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        await self.bot.type()

        embed = discord.Embed(color=0xFAA61A)

        for clan in self.clans.keysClans():
            if await self.clans.numWaiting(clan) > 0:
                counterClans += 1
                message = ""
                for index, userID in enumerate(await self.clans.getClanData(clan, 'waiting')):
                    user = discord.utils.get(ctx.message.server.members, id=userID)
                    try:
                        message += str(index+1) + ". " + user.display_name + "\n"
                        counterPlayers += 1
                    except AttributeError:
                        await self.clans.delWaitingMember(clan, userID)
                        message += str(index+1) + ". " + "*user not found*" + "\n"
                embed.add_field(name=await self.clans.getClanData(clan, 'name'), value=message, inline=False)

        if not message:
            await self.bot.say("The waiting list is empty")
        else:
            embed.description = "We have " + str(counterPlayers) + " people waiting for " + str(counterClans) + " clans."
            embed.set_author(name="Legend Family Waiting List", icon_url="https://i.imgur.com/dtSMITE.jpg")
            embed.set_footer(text=credits, icon_url=creditIcon)
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def changenick(self, ctx, member: discord.Member=None):
        """ Change nickname of a user of their IGN + Clan"""

        member = member or ctx.message.author

        try:
            await self.bot.type()
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            if profiledata.clan is None:
                clantag = "none"
            else:
                clantag = profiledata.clan.tag.strip("#")
            ign = profiledata.name
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
            return

        membership = await self.clans.verifyMembership(clantag)

        if membership:
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    savekey = await self.clans.getClanKey(clantag)
                    newclanname = await self.clans.getClanData(savekey, 'nickname')
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                else:
                    await self.bot.say("Nickname changed to ** {} **\n".format(newname))
        else:
            await self.bot.say("This command is only available for family members.")

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def audit(self, ctx, clankey):
        """ Check to see if your clan members are setup properly in discord."""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = await self.clans.getClanData(clankey, 'tag')
            clan_role = await self.clans.getClanData(clankey, 'role')
            clan_name = await self.clans.getClanData(clankey, 'name')
            clan_nickname = await self.clans.getClanData(clankey, 'nickname')
            clan_role = await self.clans.getClanData(clankey, 'role')
        except KeyError:
            await self.bot.say("Please use a valid clanname: {}".format(await self.clans.namesClans()))
            return

        await self.bot.type()

        try:
            clandata = await self.clash.get_clan(clan_tag)
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        await self.updateSeen()

        cr_members_name = []
        cr_members_tag = []
        cr_members_trophy = []
        for member in clandata.member_list:
            cr_members_name.append(member.name)
            cr_members_tag.append(member.tag.strip("#"))
            cr_members_trophy.append(member.trophies)

        role = discord.utils.get(server.roles, name=clan_role)
        d_members = [m for m in server.members if role in m.roles]
        d_members = sorted(d_members, key=lambda x: x.display_name.lower())

        cr_members_with_no_player_tag = []
        cr_members_with_less_trophies = []
        d_members_with_no_player_tag = []
        d_members_not_in_clan = []
        d_members_without_role = []
        d_members_without_name = []
        d_members_inactive = []
        cr_clanSettings = []

        for d_member in d_members:
            try:
                player_tag = await self.tags.getTag(d_member.id)

                if player_tag not in cr_members_tag:
                    d_members_not_in_clan.append(d_member.display_name)

                try:
                    if self.seen[legendServer[0]][d_member.id]['TIMESTAMP'] < time.time() - 691200:
                        d_members_inactive.append(d_member.display_name)
                except:
                    pass
            except KeyError:
                d_members_with_no_player_tag.append(d_member.display_name)
                continue

        for index, player_tag in enumerate(cr_members_tag):
            try:
                dc_member = await self.tags.getUser(server.members, player_tag)

                if role not in dc_member.roles:
                    d_members_without_role.append(dc_member.display_name)

                if (cr_members_name[index] not in dc_member.display_name) or (clan_nickname not in dc_member.display_name):
                    d_members_without_name.append(dc_member.display_name)
            except AttributeError:
                cr_members_with_no_player_tag.append(cr_members_name[index])
                continue

        clanReq = clandata.required_trophies
        for index, player_trophy in enumerate(cr_members_trophy):
            if player_trophy < clanReq:
                cr_members_with_less_trophies.append(cr_members_name[index])

        cr_clanSettings.append(clandata.badge_id == 16000002)
        cr_clanSettings.append(clandata.location.name == "International")
        cr_clanSettings.append("Legend Family🔥14 Clans🔥LegendClans.com🔥Events & Prizes🔥Apply at legendclans.com/discord🔥" in clandata.description)
        cr_clanSettings.append(clandata.type != "closed")

        message = ""

        if False in cr_clanSettings:
            message += "\n\n:warning: Problems in clan settings for **" + clan_name + "**:```"

            if not cr_clanSettings[0]: message += "\n• Clan Badge is incorrect."
            if not cr_clanSettings[1]: message += "\n• Clan Location is incorrect."
            if not cr_clanSettings[2]: message += "\n• Clan description is incorrect."
            if not cr_clanSettings[3]: message += "\n• Clan is closed."

            message += "```"

        if cr_members_with_no_player_tag:
            message += "\n\n:warning: **("+str(len(cr_members_with_no_player_tag))+")** Players in **" + clan_name + "**, but have **NOT** joined discord: ```• "
            message += "\n• ".join(cr_members_with_no_player_tag)
            message += "```"

        if d_members_with_no_player_tag:
            message += "\n\n:warning: **("+str(len(d_members_with_no_player_tag))+")** Players with **" + clan_name + "** role, but have **NO** tags saved: ```• "
            message += "\n• ".join(d_members_with_no_player_tag)
            message += "```"

        if d_members_not_in_clan:
            message += "\n\n:warning: **("+str(len(d_members_not_in_clan))+")** Players with **" + clan_name + "** role, but have **NOT** joined the clan: ```• "
            message += "\n• ".join(d_members_not_in_clan)
            message += "```"

        if d_members_without_role:
            message += "\n\n:warning: **("+str(len(d_members_without_role))+")** Players in **" + clan_name + "**, but **DO NOT** have the clan role: ```• "
            message += "\n• ".join(d_members_without_role)
            message += "```"

        if d_members_without_name:
            message += "\n\n:warning: **("+str(len(d_members_without_name))+")** Players in **" + clan_name + "**, but have an **INCORRECT** nickname: ```• "
            message += "\n• ".join(d_members_without_name)
            message += "```"

        if cr_members_with_less_trophies:
            message += "\n\n:warning: **("+str(len(cr_members_with_less_trophies))+")** Players in **" + clan_name + "**, but **DO NOT** meet the trophy requirements: ```• "
            message += "\n• ".join(cr_members_with_less_trophies)
            message += "```"

        if d_members_inactive:
            message += "\n\n:warning: **("+str(len(d_members_inactive))+")** Players in **" + clan_name + "**, but **NOT** active on Discord: ```• "
            message += "\n• ".join(d_members_inactive)
            message += "```"

        if message == "":
            message += "Congratulations, your clan has no problems found so far. Kudos!"

        await self.bot.say(message)

    @commands.group(pass_context=True)
    async def topmembers(self, ctx):
        """Base command for showing top members"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @topmembers.command(name="trophies")
    async def topmembers_trophies(self, role: str=None):
        """Show Family Ladder LeaderBoard"""
        number = 10
        if number > 100:
            await self.bot.say("Sorry! the number must be below 100.")
            return

        if "family" in self.settings:
            familyname = self.settings['family']
        else:
            familyname = "Legend Family"

        if role is None:
            title = "{} leaderboard - Trophies".format(familyname)
        else:
            role = role.replace("-", "").strip('s').lower()
            title = "{} {} leaderboard - Trophies".format(familyname, role.capitalize())

        if role not in ["leader", "coleader", "elder", "member", None]:
            await self.bot.say("Invalid role! Please chose between: leader, coleader, and elder.")
            return

        embed = discord.Embed(color=0xFAA61A)
        embed.set_author(name=title,
                         icon_url="https://i.imgur.com/dtSMITE.jpg")

        await self.bot.type()

        try:
            if "url" in self.settings:
                familyurl = '{}/members/datatable'.format(self.settings['url'])
                allplayers = requests.get(familyurl, timeout=15).json()
            else:
                allplayers = requests.get('http://royaleapi.com/clan/family/legend/members/datatable', timeout=15).json()
        except:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        players = dict(allplayers)
        players['data'] = sorted(allplayers['data'], key=lambda x: x['family_rank_score'])

        message = ""
        amount = 0
        for x in range(0, len(players['data'])):
            clanrole = players['data'][x]['role'].replace("-", "").lower()
            clantag = players['data'][x]['clan_tag']
            for i in self.clans.keysClans():
                if clantag == await self.clans.getClanData(i, 'tag'):
                    clanname = await self.clans.getClanData(i, 'nickname')

            if role:
                if role != clanrole:
                    continue

            message += "``{} [{}]`` {} ({})\n".format((str(amount + 1) + ".").ljust(3),
                                                      players['data'][x]['trophies'],
                                                      players['data'][x]['name'],
                                                      clanname)
            amount += 1
            if amount == number:
                break

        embed.description = message
        await self.bot.say(embed=embed)

    @topmembers.command(name="donations")
    async def topmembers_donations(self, role: str=None):
        """Show Family Donations LeaderBoard"""
        number = 10
        if number > 100:
            await self.bot.say("Sorry! the number must be below 100.")
            return

        if "family" in self.settings:
            familyname = self.settings['family']
        else:
            familyname = "Legend Family"

        if role is None:
            title = "{} leaderboard - Donations".format(familyname)
        else:
            role = role.replace("-", "").strip('s').lower()
            title = "{} {} leaderboard - Donations".format(familyname, role.capitalize())

        if role not in ["leader", "coleader", "elder", "member", None]:
            await self.bot.say("Invalid role! Please chose between: leader, coleader, and elder.")
            return

        embed = discord.Embed(color=0xFAA61A)
        embed.set_author(name=title,
                         icon_url="https://i.imgur.com/dtSMITE.jpg")

        await self.bot.type()

        try:
            if "url" in self.settings:
                familyurl = '{}/members/datatable'.format(self.settings['url'])
                allplayers = requests.get(familyurl, timeout=15).json()
            else:
                allplayers = requests.get('http://royaleapi.com/clan/family/legend/members/datatable', timeout=15).json()
        except:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        players = dict(allplayers)
        players['data'] = sorted(allplayers['data'], key=lambda x: x['family_rank_donations'])

        message = ""
        amount = 0
        for x in range(0, len(players['data'])):
            clanrole = players['data'][x]['role'].replace("-", "").lower()
            clantag = players['data'][x]['clan_tag']
            for i in self.clans.keysClans():
                if clantag == await self.clans.getClanData(i, 'tag'):
                    clanname = await self.clans.getClanData(i, 'nickname')

            if role:
                if role != clanrole:
                    continue

            message += "``{} [{}]`` {} ({})\n".format((str(amount + 1) + ".").ljust(3),
                                                      players['data'][x]['donations'],
                                                      players['data'][x]['name'],
                                                      clanname)
            amount += 1
            if amount == number:
                break

        embed.description = message
        await self.bot.say(embed=embed)

    @commands.command()
    async def topclans(self):
        """Show top 10 international clans"""

        await self.bot.type()
        try:
            topclans = await self.clash.get_top_clans('57000006')
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        msg = ""
        for x in range(10):
            msg += "``" + str(topclans.get("items")[x].rank).zfill(3) + "." + "`` " + topclans.get("items")[x].name + "\n"
        for i in range(10, len(topclans.get("items"))):
            for j in self.clans.keysClans():
                if topclans.get("items")[i].tag.strip("#") == await self.clans.getClanData(j, 'tag'):
                    msg += "``" + str(topclans.get("items")[i].rank).zfill(3) + "." + "`` " + topclans.get("items")[i].name + "\n"

        embed = discord.Embed(description=msg, color=0xFAA61A)
        embed.set_author(name="Local International Leaderboard",
                         url="http://royaleapi.com/top/clans/_int",
                         icon_url="https://i.imgur.com/dtSMITE.jpg")
        embed.set_footer(text=credits, icon_url=creditIcon)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def platoon(self, ctx, member: discord.Member):
        """Tpgg;e pPlatoon Role for Brawlers"""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        role = discord.utils.get(server.roles, name="Platoon")
        try:
            if role in member.roles:
                await self.bot.remove_roles(member, role)
                await self.bot.say("{} Role Removed from {}".format(role.name, member.display_name))
            else:
                await self.bot.add_roles(member, role)
                await self.bot.say("{} Role Added to {}".format(role.name, member.display_name))
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def guest(self, ctx, member: discord.Member):
        """Add guest role and change nickname to CR"""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        try:
            await self.bot.type()
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            ign = profiledata.name
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except KeyError:
            await self.bot.say("You must assosiate a tag with this member first using ``{}save #tag @member``".format(ctx.prefix))
            return

        try:
            newname = ign + " | Guest"
            await self.bot.change_nickname(member, newname)
        except discord.HTTPException:
            await self.bot.say("I don’t have permission to change nick for this user.")
            return

        role = discord.utils.get(server.roles, name="Guest")
        try:
            await self.bot.send_message(member, guest_rules)
            await self.bot.say("{} Role Added to {}".format(role.name, member.display_name))
        except discord.errors.Forbidden:
            await self.bot.say("Command failed, {} please fix your privacy settings, we are unable to send you Guest Rules.".format(member.mention))
            return

        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def inactive(self, ctx, member: discord.Member):
        """Use this command after kicking people from clan"""

        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Legend Family Server")
            return

        rolesToRemove = await self.clans.rolesClans()
        rolesToRemove += ["Bait", "Siege", "Cycle", "Control",
                          "Beatdown", "Tournaments", "Giveaways",
                          "Gizer", "Pro Payday", "Rare™", "Epic™",
                          "LeGeNDary™"]

        await self._remove_roles(member, rolesToRemove)
        await self.bot.change_nickname(member, None)

        await self.bot.say("Member and clan roles removed.\nNickname has been reset.")

    @commands.command()
    async def gmt(self):
        """Get the currect GMT time"""
        await self.bot.say(datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M GMT"))

    @commands.command(pass_context=True, no_pm=True)
    async def cwstats(self, ctx, tag):
        """Tournament/Clanwar Statistics generator"""
        await self.bot.type()

        tag = await self.tags.formatTag(tag)

        if not await self.tags.verifyTag(tag):
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

        try:
            tourney = await self.clash.get_tournament(tag)
        except clashroyale.RequestError:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        clanwar_dict = {}
        for member in tourney.members_list:

            tourney_score = member.score

            if not hasattr(member, 'clan'):
                tourney_clan = "OTHERS"
            else:
                tourney_clan = member.clan.name

            if tourney_clan not in clanwar_dict:
                clanwar_dict[tourney_clan] = {}
                clanwar_dict[tourney_clan]['score'] = 0
                clanwar_dict[tourney_clan]['participants'] = 0

            clanwar_dict[tourney_clan]['score'] += tourney_score
            clanwar_dict[tourney_clan]['participants'] += 1

        message = "\n**{}**```{}\t{}\t{}\n".format(tourney.name, "CLAN".ljust(17), "SCORE".ljust(9), "PARTICIPANTS")
        clanwar_dict = OrderedDict(sorted(clanwar_dict.items(), key=lambda x: x[1]['score'], reverse=True))
        for x in clanwar_dict:
            message += "{}\t{}\t{}\n".format(x.ljust(17), str(clanwar_dict[x]['score']).ljust(9), clanwar_dict[x]['participants'])
        message += "```"
        await self.bot.say(message)


def check_folders():
    if not os.path.exists("data/legend"):
        print("Creating data/legend folder...")
        os.makedirs("data/legend")

    if not os.path.exists("data/seen"):
        print("Creating data/seen folder...")
        os.makedirs("data/seen")


def check_files():
    f = "data/legend/settings.json"
    if not fileIO(f, "check"):
        print("Creating empty settings.json...")
        fileIO(f, "save", {})

    f = "data/seen/seen.json"
    if not fileIO(f, "check"):
        print("Creating empty seen.json...")
        fileIO(f, "save", {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(legend(bot))
