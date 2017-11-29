import discord
from discord.ext import commands
import requests
import json
import os
from .utils.dataIO import dataIO
from cogs.utils import checks
import asyncio

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Cog by GR8 | Academy"

rules_text = ""
commands_text =  ""
info_text = ""
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
        self.clash = dataIO.load_json('data/clashroyale/tags.json')
        self.c = dataIO.load_json('data/legend/clans.json')
    
    def numClans(self):
        return len(self.c)
    
    def clanArray(self):
        return self.c.keys()
    
    async def updateClash(self):
        self.clash = dataIO.load_json('data/clashroyale/tags.json')
        
    def save_data(self):
        """Saves the json"""
        dataIO.save_json('data/legend/clans.json', self.c)

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
    @checks.mod_or_permissions(administrator=True)
    async def registerclan(self, ctx, clankey, ctag, role: discord.Role, nickname):
        
        toregister = {
		"tag": ctag,
		"role_id" : role.id,
		"nickname" : nickname
        }
        
        self.c[clankey] = toregister
        self.save_data()
        await self.bot.say("Success")
        
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def deleteclan(self, ctx, clankey):
    
        if self.c.pop(clankey, None):
            self.save_data()
            await self.bot.say("Success")
            return
        await self.bot.say("Failed")


    @commands.command(pass_context=True)
    async def listclans(self, ctx, member: discord.Member = None):
        """ Shows clans, can also show clans based on a member's trophies"""
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
            # getrequest = 'http://api.cr-api.com/clan/'
            # getrequest += ','.join(self.c[clan]["tag"] for clan in self.c)
            # getrequest += '/info'
            clans = requests.get('http://api.cr-api.com/clan/'+','.join(self.c[clan]["tag"] for clan in self.c)+'/info', timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
        except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return
        clans = sorted(clans, key=lambda clanned: clanned['requiredScore'], reverse=True)
        totalMembers = sum(clans[x]['memberCount'] for x in range(len(clans)))
        # totalMembers = sum(clans[x]['memberCount'] for x in clans.keys())
        # for x in range(0, numClans):
            # totalMembers += clans[x]['memberCount']

        embed=discord.Embed(title="Master Clan List", description="Number of clans: " + str(self.numClans()) + " | Number of members: " + str(totalMembers), color=0xf1c747)
        embed.set_thumbnail(url='https://statsroyale.com/images/badges/0.png')
        embed.set_footer(text=credits, icon_url=creditIcon)

        foundClan = False
        for x in range(0, self.numClans()):
        
            # numWaiting = 0

            # for y in range(0, len(clanArray)):
                # if self.c[clanArray[y]]['tag'] == clans[x]['tag']:
                    # numWaiting = len(self.c[clanArray[y]]['waiting'])
                    # break

            # if numWaiting > 0:
                # title = "["+str(numWaiting)+" Waiting] "
            # else:
                # title = ""
                
            if clans[x]['memberCount'] < 50:
                showMembers = str(clans[x]['memberCount']) + "/50"
            else:
                showMembers = "**FULL**   "
            
            if str(clans[x]['typeName']) == 'Invite Only':
                title = ""
            else:
                title = "["+str(clans[x]['typeName'])+"] "

            title += clans[x]['name'] + " (#" + clans[x]['tag'] + ") "

            clans[x]['maxtrophies'] = 0

            desc = ":shield: " + str(clans[x]['memberCount']) + "/50     :trophy: " + str(clans[x]['requiredScore']) + "+     :medal: " +str(clans[x]['score'])
            totalMembers += clans[x]['memberCount']

            if (trophies >= clans[x]['requiredScore']) and (maxtrophies > clans[x]['maxtrophies']) and (clans[x]['memberCount'] < maxmembers):
                foundClan = True
                embed.add_field(name=title, value=desc, inline=False)

        if foundClan is False:
            embed.add_field(name="uh oh!", value="There are no clans available for you at the moment, please type !listclans to see all clans.", inline=False)

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)   
    async def changenick(self, ctx, member: discord.Member = None):   
        """ Change nickname of a user to their IGN + Clan"""

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

        # membership = False
        # for clanlist in range(0, len(self.c)):
            # if self.c[clanArray[x]]['tag'] == clantag:
                # membership = True
                # clindex = int(x)
                # break
        
        reverseC = {self.c[key]['tag']: key for key in self.c.keys()}
        membership = clantag in reverseC.keys()

        if membership:
            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[reverseC[clantag]]['nickname']
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
        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            # clan_role = self.c[clankey]['role'] 
            clan_role_id = self.c[clankey]['role_id']
        except KeyError:
            await self.bot.say("Please use a valid clanname")
            await self.bot.say(', '.join(self.c.keys()))
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
        clan_role = role.name
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
            message += ("\n\n:warning: Players in **" + clan_role 
                        + "**, but have **NO** tags saved or have **NOT** joined discord"
                        + "**("+str(len(cr_members_with_no_player_tag))+")**: ```• ")
            message += "\n• ".join(cr_members_with_no_player_tag)
            message += "```"

        if d_members_with_no_player_tag:
            message += ("\n\n:warning: Players with **" + clan_role 
                    + "** role, but have **NO** tags saved"
                    + "**("+str(len(d_members_with_no_player_tag))+")**: ```• ")
            message += "\n• ".join(d_members_with_no_player_tag)
            message += "```"

        if d_members_not_in_clan:
            message += ("\n\n:warning: Players with **" + clan_role 
                    + "** role, but have **NOT** joined the clan"
                    + "**("+str(len(d_members_not_in_clan))+")**: ```• ")
            message += "\n• ".join(d_members_not_in_clan)
            message += "```"

        if d_members_without_role:
            message += ("\n\n:warning: Players in **" + clan_role 
                    + "**, but **DO NOT** have the clan role"
                    + "**("+str(len(d_members_without_role))+")**: ```• ")
            message += "\n• ".join(d_members_without_role)
            message += "```"

        if cr_members_with_less_trophies:
            message += ("\n\n:warning: Players in **" + clan_role 
                    + "**, but **DO NOT** meet the trophy requirements"
                    + "**("+str(len(cr_members_with_less_trophies))+")**: ```• ")
            message += "\n• ".join(cr_members_with_less_trophies)
            message += "```"

        if message == "":
            message += "Congratulations, your clan has no problems found so far. Kudos!"

        await self.bot.say(message)

    # @commands.command()
    # async def topmembers(self, number=10):
        # """Show Top Members"""

        # if number > 50:
            # await self.bot.say("Sorry! the number must be below 50.")
            # return

        # await self.bot.say("**Top Players**")
        # await self.bot.type()

        # allplayers = requests.get('http://cr-api.com/clan/family/legend/members/datatable', timeout=15).json()
        # players = dict(allplayers)
        # players['data'] = sorted(allplayers['data'], key=lambda x: x["family_rank_score"])
        
        # message = "```py\n"
        # for x in range(0, number):
            # message += str(x + 1).zfill(2) + ".  [" + str(players['data'][x]['score']) + "]  " + players['data'][x]['name'] + " (" + players['data'][x]['clan_name'] + ") " + "\n"
        # message += "```"

        # await self.bot.say(message)

def check_folders():
    if not os.path.exists("data/legend"):
        print("Creating data/legend folder...")
        os.makedirs("data/legend")

def check_files():
    f = "data/clashroyale/tags.json"
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        
    f = "data/clashroyale/mini_tags.json"
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        
    f = "data/legend/clans.json"
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(legend(bot))
