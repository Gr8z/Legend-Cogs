import discord
from discord.ext import commands
import requests
import json
import os
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks
import asyncio

creditIcon = "https://cdn.discordapp.com/avatars/112356193820758016/7bd5664d82cc7c9d2ae4704e58990da3.jpg"
credits = "Bot by GR8 | Academy"
numClans = 12
clanArray = ['d8','esports','squad','d82','prime','legion','rising','phantom','plague','d83','academy','dynasty']

rules_text = """**Here are some Legend Family Discord server rules.**\n
• Be respectful of other members. Do not talk them down in any way.
• Respect others' opinions. If you disagree, please do so in a constructive manner.
• Do not spam, and avoid ever using @everyone or @here without permission from clan managers or deputies.
• Be careful with sarcasm: sarcasm with no tone doesn't work via text.
• Respect and do not subvert moderators and managers.
• If you are transferring from one Legend Family clan to another, please contact your destination clan's clan leader first, and wait for the all clear from that clan leader.
• A good rule is to talk to people as if you were talking to them face to face.\n
**Violation of these roles will lead to punishment including temporary guest role reduced access, temporary kick from server, or permanent kick from server, depending on the severity and/or frequency of the offense**"""

commands_text =  """Here are some of the Legend Family Bot commands, you can use them in the #bot_spam channel.\n
**!clashProfile** - to view your Clash Royale stats.
**!chests** - to view your upcoming chests you will receive.
**!clan** - view Our clan statistics and information.
**!offers** - view your upcoming shop offers.
**!tourney** - to instantly recieve an open tournament that is available to join.
**!topmembers** - shows the top ranked players in our family.
**!payday** - receive your daily credits.
**!profile** - view your server profile.
**!deck** - make and save your deck.
**!legend** - to see status of all Legend Family clans.
**!rep @user** - give reputation points to users.
**!remindme** - Use this command to make the bot remind you of something in the future.
**!trivia** - start a trivia of your choice. Bot will ask you questions, you will get points of answering them.
**!queue** -  Listen to songs, type with command with the song name inside a voice channel. (!skip, !pause, !resume, !playlist).\n
**You can type !help here to see the full commands list**"""

info_text = """You will find several channels on our Discord Server\n
**#global-chat**: to discuss about the game.
**#tourneys**: Dozens of tourney's posted everyday. 
**#news**: important info about family.
**#deck-recommendation**: decks discussion.
**#offtopic**: you can chat about anything unrelated to clash royale here.
**#bots-spam**: play bot commands, You can mute the channels you don't need in DISCORD settings.
"""
cw_info = """We organize a **clanwar** every weekend, which aims to determine **which clan is the strongest**. 

The **idea** is simple: A private tournament that anyone may join **within LeGeND and the alliance. **
Score is calculated in a way that allows every participant to contribute to help their clan win.  We sum the earned tournament trophies of the members of each clan to calculate a clan score, clan with highest clan score is declared the **winner**! 

There are 2 factors to win: convince more players to participate within your clan and earn more tournament trophies. Both are **equally important**. We publish tourneys and passwords at same time, so we give equal chances to each clan and player. 

**All clans** will be closed/full to avoid any leaks, nobody will be allowed to join.

**3 golden Rules for clanwars:** We respect the Opponent (no BMing if you win), we play to have fun (no obligation to participate), and don't join if you think you cannot play.
"""

class legend:

    def __init__(self, bot):
        self.bot = bot
        self.clash = dataIO.load_json('cogs/tags.json')
        self.c = dataIO.load_json('data/legend/clans.json')

    async def updateClash(self):
        self.clash = dataIO.load_json('cogs/tags.json')

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

    @commands.command(pass_context=True)
    async def legend(self, ctx, member: discord.Member = None):
        """ Show Legend clans, can also show clans based on a member's trophies"""
        if member is None:
            trophies = 9999
            maxtrophies = 9999
            maxmembers = 51
        else:
            try:
                await self.updateClash()
                profiletag = self.clash[member.id]['tag']
                profiledata = requests.get('http://api.cr-api.com/profile/'+profiletag, timeout=10).json()
                trophies = profiledata['trophies']
                maxtrophies = profiledata['stats']['maxTrophies']
                maxmembers = 50
                await self.bot.say("Hello " + member.mention + ", these are all the clans you are allowed to join, based on your trophies and max trophies.")
            except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
            except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return
            except:
                await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
                return

        try:
            clans = requests.get('http://api.cr-api.com/clan/{},{},{},{},{},{},{},{},{},{},{},{}/info'.format(self.c['d8']['tag'],self.c['esports']['tag'],self.c['squad']['tag'],self.c['d82']['tag'],self.c['prime']['tag'],self.c['legion']['tag'],self.c['rising']['tag'],self.c['dynasty']['tag'],self.c['phantom']['tag'],self.c['plague']['tag'],self.c['d83']['tag'],self.c['academy']['tag']), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
        except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return

        totalMembers = 0
        for x in range(0, numClans):
            totalMembers += clans[x]['memberCount']

        embed=discord.Embed(title="LeGeND Family Clans", description="Our Family is made up of " + str(numClans) + " clans with a total of " + str(totalMembers) + " members.", color=0xf1c747)
        embed.set_thumbnail(url='https://statsroyale.com/images/badges/16000002.png')
        embed.set_footer(text=credits, icon_url=creditIcon)

        foundClan = False
        for x in range(0, numClans):

            if str(clans[x]['typeName']) == 'Invite Only':
                title = ""
            else:
                title = "["+str(clans[x]['typeName'])+"] "

            title += clans[x]['name'] + " (#" + clans[x]['tag'] + ") "

            clans[x]['maxtrophies'] = 0

            if clans[x]['tag'] == self.c['d8']['tag']:
                title += "PB: 4600+"
                clans[x]['maxtrophies'] = 4600

            if clans[x]['tag'] == self.c['esports']['tag']:
                title += "PB: 4300+"
                clans[x]['maxtrophies'] = 4300

            if clans[x]['tag'] == self.c['prime']['tag']:
                title += "Age: 21+"

            desc = ":shield: " + str(clans[x]['memberCount']) + "/50     :trophy: " + str(clans[x]['requiredScore']) + "+     :medal: " +str(clans[x]['score'])
            totalMembers += clans[x]['memberCount']

            if (trophies >= clans[x]['requiredScore']) and (maxtrophies > clans[x]['maxtrophies']) and (clans[x]['memberCount'] < maxmembers):
                foundClan = True
                embed.add_field(name=title, value=desc, inline=False)

        if foundClan is False:
            embed.add_field(name="uh oh!", value="There are no clans available for you at the moment, please type !legend to see all clans.", inline=False)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def newmember(self, ctx, member: discord.Member):
        """Send the newcomer to the legend family server servers and welcome them."""
        try:
            await self.updateClash()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/profile/'+profiletag, timeout=10).json()
            clantag = profiledata['clan']['tag']
            clanname = profiledata['clan']['name']
            ign = profiledata['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        membership = False
        for x in range(0, len(clanArray)):
            if self.c[clanArray[x]]['tag'] == clantag:
                membership = True
                clindex = int(x)
                break

        if membership:

            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[clanArray[clindex]]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say(
                        "I don’t have permission to change nick for this user.")
                else:
                    mymessage += "Nickname changed to **{}**\n".format(newname)


            role_names = [self.c[clanArray[clindex]]['role'], 'Member']
            try:
                await self._add_roles(member, role_names)
                mymessage += "**" + self.c[clanArray[clindex]]['role'] + "** and **Member** roles added."
            except discord.Forbidden:
                await self.bot.say(
                    "{} does not have permission to edit {}’s roles.".format(
                        author.display_name, member.display_name))
            except discord.HTTPException:
                await self.bot.say("failed to add {}.").format(', '.join(role_names))

            await self.bot.say(mymessage)

            if self.c[clanArray[clindex]]['discord'] is not None:
                joinLink = "https://discord.gg/" + str(self.c[clanArray[clindex]]['discord'])
                await self.bot.send_message(member, 
                    "Hi There! Congratulations on getting accepted into our family. Now you have to carefuly read this message and follow the steps mentioned below: \n\n"+
                    "Please click on the link below to join your clan Discord server. \n\n"+
                    clanname + ": " + joinLink + "\n\n" +
                    "Please do not leave our main or clan servers while you are in the clan. Thank you."
                    )
                await self.bot.say(member.mention + " please check your DM. Sending you the invite details for " + clanname)

            
            await asyncio.sleep(300)
            await self.bot.send_message(member,rules_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,commands_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,info_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,cw_info)
        else:
            await self.bot.say("You must be accepted into a clan before I can give you clan roles.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)   
    async def changenick(self, ctx, member: discord.Member = None):   
        """ Change nickname of a user of their IGN + Clan"""

        server = ctx.message.server

        if member is None:
            member = ctx.message.author

        try:
            await self.updateClash()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/profile/'+profiletag, timeout=10).json()
            clantag = profiledata['clan']['tag']
            clanname = profiledata['clan']['name']
            ign = profiledata['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        membership = False
        for x in range(0, len(clanArray)):
            if self.c[clanArray[x]]['tag'] == clantag:
                membership = True
                clindex = int(x)
                break

        if membership:
    
            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[clanArray[clindex]]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                else:
                     await self.bot.say("Nickname changed to **{}**\n".format(newname))
        else:
            await self.bot.say("You are not even in any of our clans, what are you doing here?")

    @commands.command(pass_context=True, no_pm=True)
    async def audit(self, ctx, clankey):
        """ Check to see if your clan members are setup properly in discord."""
        server = ctx.message.server
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_role = self.c[clankey]['role'] 
            clan_role_id = self.c[clankey]['role_id']
        except KeyError:
            await self.bot.say("Please use a valid clanname : d8, esports, squad, d82, prime, legion, rising, phantom, plague, d83, academy")
            return

        try:
            clandata = requests.get('http://api.cr-api.com/clan/{}'.format(clan_tag), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        await self.updateClash()
        await self.bot.type()
        
        cr_members_name = []
        cr_members_tag = []
        cr_members_trophy = []
        for x in range(0, len(clandata['members'])):
            cr_members_name.append(clandata['members'][x]['name'])
            cr_members_tag.append(clandata['members'][x]['tag'])
            cr_members_trophy.append(clandata['members'][x]['trophies'])

        role = discord.utils.get(server.roles, id=clan_role_id)
        d_members = [m for m in server.members if role in m.roles]
        d_members = sorted(d_members, key=lambda x: x.display_name.lower())

        cr_members_with_no_player_tag = []
        cr_members_with_less_trophies = []
        d_members_with_no_player_tag = []
        d_members_not_in_clan = []
        d_members_without_role = []

        for d_member in d_members:
            try:
                player_tag = self.clash[d_member.id]['tag']

                if player_tag not in cr_members_tag:
                    d_members_not_in_clan.append(d_member.display_name)
            except KeyError:
                d_members_with_no_player_tag.append(d_member.display_name)
                continue

        for index, player_tag in enumerate(cr_members_tag):
            try:
                dc_member = None
                for key in self.clash:
                    if self.clash[key]['tag'] == player_tag:
                        dc_member = server.get_member(key)
                        break
                    else:
                        continue

                if role not in dc_member.roles:
                    d_members_without_role.append(dc_member.display_name)
            except AttributeError:
                cr_members_with_no_player_tag.append(cr_members_name[index])
                continue

        clanReq = clandata['requiredScore']
        for index, player_trophy in enumerate(cr_members_trophy):
            if player_trophy < clanReq:
                cr_members_with_less_trophies.append(cr_members_name[index])

        message = ""

        if cr_members_with_no_player_tag:
            message += "\n\n:warning: Players in **" + clan_role + "**, but have **NO** tags saved or have **NOT** joined discord: ```• "
            message += "\n• ".join(cr_members_with_no_player_tag)
            message += "```"

        if d_members_with_no_player_tag:
            message += "\n\n:warning: Players with **" + clan_role + "** role, but have **NO** tags saved: ```• "
            message += "\n• ".join(d_members_with_no_player_tag)
            message += "```"

        if d_members_not_in_clan:
            message += "\n\n:warning: Players with **" + clan_role + "** role, but have **NOT** joined the clan: ```• "
            message += "\n• ".join(d_members_not_in_clan)
            message += "```"

        if d_members_without_role:
            message += "\n\n:warning: Players in **" + clan_role + "**, but **DO NOT** have the clan role: ```• "
            message += "\n• ".join(d_members_without_role)
            message += "```"

        if cr_members_with_less_trophies:
            message += "\n\n:warning: Players in **" + clan_role + "**, but **DO NOT** meet the trophy requirements: ```• "
            message += "\n• ".join(cr_members_with_less_trophies)
            message += "```"

        if message == "":
            message += "Congratulations, your clan has no problems found so far. Kudos!"

        await self.bot.say(message)

    @commands.command()
    async def topmembers(self, number=10):
        """Show Top Legend Family Members"""

        if number > 50:
            await self.bot.say("Sorry! the number must be below 50.")
            return

        await self.bot.say("**LeGeND Family Top Players**")
        await self.bot.type()

        allplayers = requests.get('http://cr-api.com/clan/family/legend/members/datatable', timeout=15).json()
        players = dict(allplayers)
        players['data'] = sorted(allplayers['data'], key=lambda x: x["family_rank_score"])
        
        message = "```py\n"
        for x in range(0, number):
            message += str(x + 1).zfill(2) + ".  [" + str(players['data'][x]['score']) + "]  " + players['data'][x]['name'] + " (" + players['data'][x]['clan_name'] + ") " + "\n"
        message += "```"

        await self.bot.say(message)

def check_folders():
    if not os.path.exists("data/legend"):
        print("Creating data/legend folder...")
        os.makedirs("data/legend")

def check_files():
    f = "cogs/tags.json"
    if not fileIO(f, "check"):
        print("Creating empty tags.json...")
        fileIO(f, "save", [])
    f = "data/legend/clans.json"
    if not fileIO(f, "check"):
        print("Creating empty clans.json...")
        fileIO(f, "save", [])

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(legend(bot))
