import discord
from discord.ext import commands
import requests
import json
import os
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks
import asyncio
import random
from random import choice as rand_choice
import string
import datetime
import time
from collections import OrderedDict

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"
BOTCOMMANDER_ROLES =  ["Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]

rules_text = """**Here are some Legend Family Discord server rules.**\n
• Respect others' opinions. If you disagree, please do so in a constructive manner. 
• This is an English only server, please use any other languages in a private message.
• Do not spam, and avoid ever using @myclanname without permission from clan managers or deputies.
• No advertisement of any kind, e.g. clans, websites, discord invites.
• Use #bot-spam for bot features, e.g. **!deck** or **!payday**
• Respect and do not subvert moderators and managers.
• A good rule is to talk to people as if you were talking to them face to face.
• There are more rules that vary from clan to clan. Ask your clan leader for the rules of your clan.\n
**Violation of these roles will lead to punishment including temporary guest role reduced access, temporary kick from server, or permanent kick from server, depending on the severity and/or frequency of the offense**"""

commands_text =  """Here are some of the Legend Family Bot commands, you can use them in the #bot-spam channel.\n
**!clashProfile** - to view your Clash Royale stats.
**!chests** - to view your upcoming chests you will receive.
**!tourney** - to instantly recieve an open tournament that is available to join.
**!topmembers** - shows the top ranked players in our family.
**!payday** - receive your 300 credits every 30 minutes.
**!heist** - Play a heist with a crew in #heist channel.
**!buy** - Take a look at what you can purchase with your credits.
**!balance** - To check your current bank balance.
**!profile** - view your server profile.
**!deck** - make and save your deck.
**!legend** - to see status of all Legend Family clans.
**!rep @user** - give reputation points to users.
**!remindme** - Use this command to make the bot remind you of something in the future.
**!trivia** - start a trivia of your choice. Bot will ask you questions, you will get points of answering them.
**!play** - Listen to songs, type with command with the song name inside a voice channel. (!skip, !pause, !resume, !playlist).\n
**!invite** - Get the invite link for the server to share with your friends.\n
**!report** - Report a user to the moderators for breaking the rules.\n
**!coaching** - To request a coaching session.\n
**You can type !help here to see the full commands list**"""

info_text = """You will find several channels on our Discord Server\n
**#global-chat**: to discuss about the game.
**#tourneys**: Dozens of tournaments posted everyday. 
**#news**: important info about family.
**#deck-recommendation**: decks discussion.
**#off-topic**: you can chat about anything unrelated to clash royale here.
**#bots-spam**: play bot commands, You can mute the channels you don't need in DISCORD settings.
**#friends-forever**: Post your Clash friend invite link or add others.
"""
cw_info = """We organize **Legend Wars** every weekend, which aims to determine **which clan is the strongest**. 

The **idea** is simple: A private tournament that anyone may join **within LeGeND and the alliance. **
Score is calculated in a way that allows every participant to contribute to help their clan win.  We sum the earned tournament trophies of the members of each clan to calculate a clan score, clan with highest clan score is declared the **winner**! 

There are 2 factors to win: convince more players to participate within your clan and earn more tournament trophies. Both are **equally important**. We publish tourneys and passwords at same time, so we give equal chances to each clan and player. 

Every Sunday, there will be a **special Gizer Legend War** where various clans outside and inside the family will join a tournament and the top clan will recieve $5 from Gizer. 

Each and every participant will recieve discord credits for getting trophies for their clan. The more trophies you can collect, the more credits you will get. Credits can used in LeGeND shop to buy various items.

**All clans** will be closed/full to avoid any leaks, nobody will be allowed to join.

**3 golden Rules for Legend Wars:** We respect the Opponent (no BMing if you win), we play to have fun (no obligation to participate), and don't join if you think you cannot play.
"""

credits_info = """**WHAT ARE CREDITS?**
Credits are a virtual currency in LeGeND Discord, you earn credits by playing in Legend Wars, donating, and playing mini games in discord. To use your credits, you can buy items using !buy.

• Every 30 minutes, you can get free credits by typing !payday in #bot-spam channel.
• Every Sunday, you receive something called a "Weekly Payout". Which converts all your week's clan donations into credits. So the more active you are in a clan, the more credits you get.
• We have Legend Wars every weekend, participating in these clan wars also give you tons of credits according to your tournament trophies.
• You can also win credits by playing #heist and #challenges.
• You can play Clash Royale #duels to bet on your skills in friend battles.
• Last but not least, you can get easy credits by just chatting on discord. The more you chat, the more credits you accumulate.

You can type !buy here to look at different ways you can spend these credits.
"""

esports_info = """The LeGeND Esports Team is recruiting all active and aspiring players!

With the goal of encouraging competitive play in the family, there is a monthly ranked season system on the Esports Team Server where players compete to play on LeGeND Esports A Team and B team to represent the family in various North American events. Our strongest players will compete side by side with the very best in leagues such as CCTS, CPL, and even RPL!

While we have a clan called LeGeND Esports!, the team operates separately from the clan, and sends members from any family clan to events.

But please remember that this is a more professional setting than the rest of the family and poor behaviour will not be tolerated. 

Please note that if you just lurk in the server and not participate for a long period of time you will be kicked off the server.

https://discord.gg/CN47Tkx
"""

coc_bs = """We also play **Clash of Clans**, and we would like to invite to you join our clans.

• **LeGeND Raiders! (#JQJRGVJU)** - https://discord.gg/BG7wMFw

You can send a request to join with the message "from LEGEND". Join the discord server when you are accepted.
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
        self.clash = dataIO.load_json('cogs/tags.json')
        self.c = dataIO.load_json('cogs/clans.json')
        self.settings = dataIO.load_json('data/legend/settings.json')
        self.auth = dataIO.load_json('cogs/auth.json')
        self.welcome = dataIO.load_json('data/legend/welcome.json')
        self.bank = dataIO.load_json('data/economy/bank.json')
        self.seen = dataIO.load_json('data/seen/seen.json')

    async def updateClash(self):
        self.clash = dataIO.load_json('cogs/tags.json')
        self.c = dataIO.load_json('cogs/clans.json')

    async def updateSeen(self):
        self.seen = dataIO.load_json('data/seen/seen.json')
        
    def save_data(self):
        """Saves the json"""
        dataIO.save_json('cogs/clans.json', self.c)
        
    def save_settings(self):
        """Saves the json"""
        dataIO.save_json('data/legend/settings.json', self.settings)
        
    async def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
       return ''.join(random.choice(chars) for _ in range(size))
    
    def clanArray(self):
        return self.c.keys()
    
    def numClans(self):
        return len(self.c.keys())    

    def getAuth(self):
        return {"auth" : self.auth['token']}
    
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
            #await asyncio.sleep(3)
        except:
            pass
    
    @commands.group(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def clans(self, ctx):
        """Base command for managing clash royale clans. [p]help clans for details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @clans.command(pass_context=True, name="register")
    @checks.admin_or_permissions(administrator=True)
    async def clans_register(self, ctx, clankey, ctag, role: discord.Role, nickname):
        """Register a clan for tracking"""
        toregister = {
            'tag': ctag,
            'role': role.name,
            'role_id': role.id,
            'name': nickname,   # Not good, will fix later
            'nickname' : nickname,
            'waiting': [],
            'personalbest': 0,
            'bonustitle': "",
            'discord': None
            }

        clankey = clankey.lower()
        
        self.c[clankey] = toregister
        self.save_data()
        await self.bot.say("Success")
        
    @clans.command(pass_context=True, name="delete")
    @checks.admin_or_permissions(administrator=True)
    async def clans_delete(self, ctx, clankey):
        """Remove a clan from tracking"""
        clankey = clankey.lower()
        if self.c.pop(clankey, None):
            self.save_data()
            await self.bot.say("Success")
            return
        await self.bot.say("Failed")
    
    @clans.command(pass_context=True, name="pb")
    @checks.admin_or_permissions(administrator=True)
    async def clans_pb(self, ctx, clankey, pb: int):
        """Set a Personal Best requirement for a clan"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['personalbest'] = pb
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return 
        
        self.save_data()        
        await self.bot.say("Success")

    @clans.command(pass_context=True, name="bonus")
    @checks.admin_or_permissions(administrator=True)
    async def clans_bonus(self, ctx, clankey, *bonus):
        """Add bonus information to title of clan (i.e. Age: 21+)"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['bonustitle'] = " ".join(bonus)
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+",".join(key for key in self.c.keys()))
            return 
        
        self.save_data()
        await self.bot.say("Success")
    
    @clans.command(pass_context=True, name="discord")
    @checks.admin_or_permissions(administrator=True)
    async def clans_discord(self, ctx, clankey, discordinv):
        """Add discord invite link"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['discord'] = discordinv
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+",".join(key for key in self.c.keys()))
            return 
        
        self.save_data()
        await self.bot.say("Success")        

    @clans.command(pass_context=True, name="log")
    @checks.admin_or_permissions(administrator=True)
    async def clans_log(self, ctx, clankey, channel : discord.Channel):
        """Add discord invite link"""
        clankey = clankey.lower()

        try:
            server = ctx.message.server

            if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
                await self.bot.say("I do not have permissions to send messages to {0.mention}".format(channel))
                return

            if channel is None:
                await self.bot.say("I can't find the specified channel. It might have been deleted.")

            self.c[clankey]['log_channel'] = channel.id
            self.save_data()

            await self.bot.send_message(channel, "I will now send log messages to {0.mention}".format(channel))
            await self.bot.say("Clash log channel for {} is now set to {}".format(clankey, channel))

        except KeyError:
            await self.bot.say("Please use a valid clanname : "+",".join(key for key in self.c.keys()))
            return 
        except discord.errors.Forbidden:
            await self.bot.say("No permission to send messages to that channel")
        

    @clans.command(pass_context=True, name="private")
    @checks.admin_or_permissions(administrator=True)
    async def clans_private(self, ctx, clankey):
        """Toggle Private approval of new recruits"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['approval'] = not self.c[clankey]['approval']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+",".join(key for key in self.c.keys()))
            return 
        
        self.save_data()
        await self.bot.say("Private Approval now is set to " + str(self.c[clankey]['approval']))
        
    @clans.command(pass_context=True, name="family")
    @checks.admin_or_permissions(administrator=True)
    async def clans_family(self, ctx, url, *FamilyName):
        """Add Clan Family name and link"""
        
        self.settings['url'] = url
        self.settings['family'] = " ".join(FamilyName)

        self.save_settings()
        await self.bot.say("Success")

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
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Member", "Co-Leader", "Hub Officer", "Clan Deputy", "Clan Manager"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

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
                await self.bot.type()
                profiletag = self.clash[member.id]['tag']
                profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
                trophies = profiledata['trophies']
                maxtrophies = profiledata['stats']['maxTrophies']

                if profiledata['clan'] is None:
                    clanname = "*None*"
                else: 
                    clanname = profiledata['clan']['name']

                ign = profiledata['name']
                maxmembers = 50
            except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
            except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return
            except:
                await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
                return

        try:
            await self.bot.type()
            clans = requests.get('https://api.royaleapi.com/clan/'+','.join(self.c[clan]["tag"] for clan in self.c)+'?exclude=members', headers=self.getAuth(), timeout=25).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
        except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return
                
        clans = sorted(clans, key=lambda clanned: (clanned['requiredScore'], clanned['score']), reverse=True)
       
        embed=discord.Embed(color=0xFAA61A)
        if "url" in self.settings and "family" in self.settings:
            embed.set_author(name=self.settings['family'], url=self.settings['url'], icon_url="https://i.imgur.com/dtSMITE.jpg")
        else:
            embed.set_author(name="LeGeND Family Clans", url="http://royaleapi.com/clan/family/legend", icon_url="https://i.imgur.com/dtSMITE.jpg")

        embed.set_footer(text=credits, icon_url=creditIcon)

        foundClan = False
        totalMembers = 0
        totalWaiting = 0
        for x in range(0, len(clans)):
            numWaiting = 0
            personalbest = 0
            bonustitle = None
            
            for clankey in self.clanArray():
                if self.c[clankey]['tag'] == clans[x]['tag']:
                    numWaiting = len(self.c[clankey]['waiting'])
                    personalbest = self.c[clankey]['personalbest']
                    bonustitle = self.c[clankey]['bonustitle']
                    emoji = self.c[clankey]['emoji']
                    warTrophies = self.c[clankey]['warTrophies']
                    totalWaiting += numWaiting
                    break

            if numWaiting > 0:
                title = "["+str(numWaiting)+" Waiting] "
            else:
                title = ""

            totalMembers += clans[x]['memberCount']
            if clans[x]['memberCount'] < 50:
                showMembers = str(clans[x]['memberCount']) + "/50"
            else:
                showMembers = "**FULL**   "

            if str(clans[x]['type']) != 'invite only':
                title += "["+str(clans[x]['type']).title()+"] "

            title += clans[x]['name'] + " (#" + clans[x]['tag'] + ") "
            
            if personalbest > 0:
                title += "PB: "+str(personalbest)+"+  "
                clans[x]['maxtrophies'] = personalbest
            
            if bonustitle is not None:
                title += bonustitle  

            desc = "{} {}      <:crtrophy:448609948008579073> {}+     <:wartrophy:448609141796241408> {}   <:openlink:448611387040595979> [Open](https://legendclans.com/clanInfo/{})".format(emoji, showMembers, str(clans[x]['requiredScore']), str(warTrophies), clans[x]['tag'])

            if (member is None) or ((clans[x]['requiredScore'] <= trophies) and (maxtrophies > personalbest) and (trophies - clans[x]['requiredScore'] < 1200) and (clans[x]['type'] != 'closed')):
                foundClan = True
                embed.add_field(name=title, value=desc, inline=False)

        if foundClan is False:
            embed.add_field(name="uh oh!", value="There are no clans available for you at the moment, please type !legend to see all clans.", inline=False)

        embed.description = "Our Family is made up of " + str(self.numClans()) + " clans with a total of " + str(totalMembers) + " members. We have " + str((self.numClans()*50)-totalMembers) + " spots left and " + str(totalWaiting) + " members in waiting lists."
        await self.bot.say(embed=embed)

        if member is not None:
            await self.bot.say("Hello **{}**, above are all the clans you are allowed to join, based on your statistics. Which clan would you like to join? \n\n**Name:** {} (#{})\n**Trophies:** {}/{}\n**Clan:** {}\n```WARNING: PLEASE DO NOT REQUEST TO JOIN ANY CLANS IF YOU HAVE NOT YET RECIEVED YOUR RECRUIT CODE!```".format(ign, ign, profiletag, str(trophies), str(maxtrophies), clanname))

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def approve(self, ctx, member: discord.Member, clankey):
        """Send instructions to people joining a clan"""
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_name = self.c[clankey]['name'] 
            clan_role = self.c[clankey]['role'] 
            clan_pb = self.c[clankey]['personalbest']
            clan_approval = self.c[clankey]['approval']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        leftClan = False
        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            clandata = requests.get('https://api.royaleapi.com/clan/{}'.format(clan_tag), headers=self.getAuth(), timeout=10).json()
            ign = profiledata['name']
            if profiledata['clan'] is None:
                leftClan = True
                clantag = ""
                clanname = ""
            else: 
                clantag = profiledata['clan']['tag']
                clanname = profiledata['clan']['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
            return

        membership = True
        for clankeys in self.clanArray():
            if self.c[clankeys]['tag'] == clantag:
                membership = False
                savekey = clankeys
                break

        if membership:

            trophies = profiledata['trophies']
            maxtrophies = profiledata['stats']['maxTrophies']

            if (clandata['memberCount'] == 50):
                await self.bot.say("Approval failed, the clan is Full.")
                return

            if ((trophies < clandata['requiredScore']) and (maxtrophies < clan_pb)):
                await self.bot.say("Approval failed, you don't meet the trophy requirements.")
                return

            if (clandata['type'] == "closed"):
                await self.bot.say("Approval failed, the clan is currently closed.")
                return

            if clan_approval:
                if clan_role in [y.name.lower() for y in member.roles]:
                    await self.bot.say("Approval failed, only an {} staff can approve new recruits for this clan.".format(clan_name))
                return

            if not leftClan:
                await self.bot.say("Approval failed, You have not yet left your current clan. Would you like me to check again in 2 minutes? (Yes/No)")

                answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)

                if answer is None:
                    return
                elif "yes" not in answer.content.lower():
                    return

                await self.bot.say("Okay, I will retry this command in 2 minutes.")
                await asyncio.sleep(120)

                message = ctx.message
                message.content = ctx.prefix + "approve {} {}".format(member.mention, clankey)
                await self.bot.process_commands(message)
                return

            if len(self.c[clankey]['waiting']) > 0:
                if member.id in self.c[clankey]['waiting']:

                    canWait = (50 - clandata['memberCount']) -1

                    if self.c[clankey]['waiting'].index(member.id) > canWait:
                        await self.bot.say("Approval failed, you are not first in queue for the waiting list on this server.")
                        return
                    
                    self.c[clankey]['waiting'].remove(member.id)
                    self.save_data()
                    
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

            try:
                recruitCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

                await self.bot.send_message(member, 
                    "Congratulations, You have been approved to join **"+ clan_name + " (#" + clan_tag + ")**.\n\n\n" +
                    "Your **RECRUIT CODE** is: ``" + recruitCode + "`` \n"+
                    "Send this code in the join request message.\n\n"+
                    "Click this link to join the clan: https://legendclans.com/clanInfo/"+ clan_tag +"\n\n" +
                    "That's it! Now wait for your clan leadership to accept you. \n" +
                    "If you do not see a 'request to join' button, make sure you leave your current clan and check the trophy requirements. \n\n" + 
                    "**IMPORTANT**: Once your clan leadership has accepted your request, let a staff member in discord know that you have been accepted. They will then unlock all the member channels for you."
                    )
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
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        isMember = await self._is_member(member)
        if isMember:
            await self.bot.say("Error, " + member.mention + " is not a new member.")
            return

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            if profiledata['clan'] is None:
                clantag = ""
                clanname = ""
            else: 
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
            await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
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
            
        membership = False
        for clankey in self.clanArray():
            if self.c[clankey]['tag'] == clantag:
                membership = True
                savekey = clankey
                break

        if membership:

            try:
                if self.c[savekey]['discord'] is not None:
                    joinLink = "https://discord.gg/" + str(self.c[savekey]['discord'])
                    await self.bot.send_message(member, 
                        "Hi There! Congratulations on getting accepted into our family. We have unlocked all the member channels for you in LeGeND Discord Server. Now you have to carefuly read this message and follow the steps mentioned below: \n\n"+
                        "Please click on the link below to join your clan Discord server. \n\n"+
                        clanname + ": " + joinLink + "\n\n" +
                        "Please do not leave our main or clan servers while you are in the clan. Thank you."
                        )
                else:
                    
                   await self.bot.send_message(member, 
                       "Hi There! Congratulations on getting accepted into our family. We have unlocked all the member channels for you in LeGeND Discord Server. \n\n"+
                       "Please do not leave our Discord server while you are in the clan. Thank you."
                       )
            except discord.errors.Forbidden:
                    await self.bot.say("Membership failed, {} please fix your privacy settings, we are unable to send you Direct Messages.".format(member.mention))
                    return

            if member.id in self.c[savekey]['waiting']:
                self.c[savekey]['waiting'].remove(member.id)
                self.save_data()

            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[savekey]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say(
                        "I don’t have permission to change nick for this user.")
                else:
                    mymessage += "Nickname changed to **{}**\n".format(newname)


            role_names = [self.c[savekey]['role'], 'Member']
            try:
                await self._add_roles(member, role_names)
                mymessage += "**" + self.c[savekey]['role'] + "** and **Member** roles added."
            except discord.Forbidden:
                await self.bot.say(
                    "{} does not have permission to edit {}’s roles.".format(
                        author.display_name, member.display_name))
            except discord.HTTPException:
                await self.bot.say("failed to add {}.").format(', '.join(role_names))

            await self.bot.say(mymessage)

            welcomeMsg = rand_choice(self.welcome["GREETING"])
            await self.bot.send_message(discord.Object(id='374596069989810178'), welcomeMsg.format(member, server))

            await self._remove_roles(member, ['Guest'])

            roleName = discord.utils.get(server.roles, name=role_names[0])
            await self.bot.send_message(discord.Object(id='375839851955748874'), '**' + ctx.message.author.display_name + '** recruited ' + '**' + ign + ' (#'+ profiletag + ')** to ' + roleName.mention)

            await asyncio.sleep(300)
            await self.bot.send_message(member,rules_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,commands_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,info_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,cw_info)
            
            await asyncio.sleep(300)
            await self.bot.send_message(member,credits_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member,coc_bs)

            #await asyncio.sleep(300)
            #await self.bot.send_message(member,esports_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member,social_info)
        else:
            await self.bot.say("You must be accepted into a clan before I can give you clan roles. Would you like me to check again in 2 minutes? (Yes/No)")

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
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        clankey = clankey.lower()
        offline = False

        try:
            clan_tag = self.c[clankey]['tag']
            clan_name = self.c[clankey]['name'] 
            clan_role = self.c[clankey]['role']
            clan_pb = self.c[clankey]['personalbest'] 
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            clandata = requests.get('https://api.royaleapi.com/clan/{}'.format(clan_tag), headers=self.getAuth(), timeout=10).json()
            ign = profiledata['name']
            if profiledata['clan'] is None:
                clantag = ""
                clanname = ""
            else: 
                clantag = profiledata['clan']['tag']
                clanname = profiledata['clan']['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Warning: cannot reach Clash Royale Servers. Using offline waiting list.")
            offline = True
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
            return


        if not offline:
            trophies = profiledata['trophies']
            maxtrophies = profiledata['stats']['maxTrophies']

            if ((trophies < clandata['requiredScore']) and (maxtrophies < clan_pb)):
                await self.bot.say("Cannot add you to the waiting list, you don't meet the trophy requirements.")
                return

        if member.id not in self.c[clankey]['waiting']:
            self.c[clankey]['waiting'].append(member.id)
            self.save_data()
        else:
            await self.bot.say("You are already in a waiting list for this clan.")
            return

        role = discord.utils.get(server.roles, name="Waiting")
        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise
        await self.bot.say(member.mention + " You have been added to the waiting list for **"+ clan_name + "**. We will mention you when a spot is available.")

        roleName = discord.utils.get(server.roles, name=self.c[clankey]['role'])
        await self.bot.send_message(discord.Object(id='375839851955748874'), "**{} (#{})** added to the waiting list for {}".format(ign, profiletag, roleName.mention))

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def remove(self, ctx, member: discord.Member, clankey):
        """Delete people from the waiting list for a clan"""
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_name = self.c[clankey]['name'] 
            clan_role = self.c[clankey]['role'] 
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        try:
            await self.updateClash()
            self.c[clankey]['waiting'].remove(member.id)
            self.save_data()

            role = discord.utils.get(server.roles, name="Waiting")
            try:
                await self.bot.remove_roles(member, role)
            except discord.Forbidden:
                raise
            except discord.HTTPException:
                raise
            await self.bot.say(member.mention + " has been removed from the waiting list for **"+ clan_name + "**.")
        except ValueError:
            await self.bot.say("Recruit not found in the waiting list.")

    @commands.command(pass_context=True, no_pm=True, aliases=["waitlist","wait"])
    async def waitinglist(self, ctx):
        """Show status of the waiting list."""

        message = ""
        counterClans = 0
        counterPlayers = 0

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        await self.bot.type()
        await self.updateClash()

        embed=discord.Embed(color=0xFAA61A)

        for indexC, clan in enumerate(self.c):
            if self.c[clan]["waiting"]:
                counterClans += 1
                message = ""
                for index, userID in enumerate(self.c[clan]["waiting"]):
                    user = discord.utils.get(ctx.message.server.members, id = userID)
                    try:
                        message += str(index+1) + ". " + user.display_name + "\n"
                        counterPlayers += 1
                    except AttributeError:
                        self.c[clan]['waiting'].remove(userID)
                        self.save_data()
                        message += str(index+1) + ". " + "*user not found*" + "\n"
                embed.add_field(name=self.c[clan]["name"], value=message, inline=False)
        
        if not message:
            await self.bot.say("The waiting list is empty")
        else:
            embed.description = "We have " + str(counterPlayers) + " people waiting for " + str(counterClans) + " clans."
            embed.set_author(name="LeGeND Family Waiting List", icon_url="https://i.imgur.com/dtSMITE.jpg")
            embed.set_footer(text=credits, icon_url=creditIcon)
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def changenick(self, ctx, member: discord.Member = None):   
        """ Change nickname of a user of their IGN + Clan"""

        server = ctx.message.server
        author = ctx.message.author

        if member is None:
            member = ctx.message.author

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
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
            await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
            return

        membership = False
        for clankey in self.clanArray():
            if self.c[clankey]['tag'] == clantag:
                membership = True
                savekey = clankey
                break

        if membership:
    
            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[savekey]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                else:
                     await self.bot.say("Nickname changed to ** {} **\n".format(newname))
        else:
            await self.bot.say("You are not even in any of our clans, what are you doing here?")

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def audit(self, ctx, clankey):
        """ Check to see if your clan members are setup properly in discord."""
        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_role = self.c[clankey]['role'] 
            clan_name = self.c[clankey]['name'] 
            clan_nickname = self.c[clankey]['nickname'] 
            clan_role_id = self.c[clankey]['role_id']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        await self.bot.type()

        try:
            clandata = requests.get('https://api.royaleapi.com/clan/{}'.format(clan_tag), headers=self.getAuth(), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
 
        await self.updateClash()
        await self.updateSeen()

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
        d_members_without_name = []
        d_members_inactive = []
        cr_clanSettings = []

        for d_member in d_members:
            try:
                player_tag = self.clash[d_member.id]['tag']

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
                dc_member = None
                for key in self.clash:
                    if self.clash[key]['tag'] == player_tag:
                        dc_member = server.get_member(key)
                        break
                    else:
                        continue

                if role not in dc_member.roles:
                    d_members_without_role.append(dc_member.display_name)

                if (cr_members_name[index] not in dc_member.display_name) or (clan_nickname not in dc_member.display_name):
                    d_members_without_name.append(dc_member.display_name)
            except AttributeError:
                cr_members_with_no_player_tag.append(cr_members_name[index])
                continue

        clanReq = clandata['requiredScore']
        for index, player_trophy in enumerate(cr_members_trophy):
            if player_trophy < clanReq:
                cr_members_with_less_trophies.append(cr_members_name[index])

        cr_clanSettings.append(clandata['badge']['id'] == 16000002)
        cr_clanSettings.append(clandata['location']['name'] == "International")
        cr_clanSettings.append("LeGeND Family🔥14 Clans🔥LegendClans.com🔥Daily Tourneys🔥Weekly LeGeND War🔥discord.me/legendfamily🔥" in clandata['description'])
        cr_clanSettings.append(clandata['type'] != "closed")

        message = ""

        if False in cr_clanSettings:
            message += "\n\n:warning: Problems in clan settings for **" + clan_name + "**:```"

            if cr_clanSettings[0] is False: message += "\n• Clan Badge is incorrect."
            if cr_clanSettings[1] is False: message += "\n• Clan Location is incorrect."
            if cr_clanSettings[2] is False: message += "\n• Clan description is incorrect."
            if cr_clanSettings[3] is False: message += "\n• Clan is closed."

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
    async def topmembers_trophies(self, role : str = None):
        """Show Family Ladder LeaderBoard"""
        number = 10
        if number > 100:
            await self.bot.say("Sorry! the number must be below 100.")
            return
        

        if "family" in self.settings:
            familyname = self.settings['family']
        else:
            familyname = "LeGeND Family"

        if role not in ["leader","coleader","elder", "member", None]:
            await self.bot.say("Invalid role!")
            return
        if role != None:
            filterroles = True
            await self.bot.say("**{0} Ladder LeaderBoard** ({1}s)".format(familyname, role))
        else:
            await self.bot.say("**{} Ladder LeaderBoard**".format(familyname))
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
        
        if role == None:
            message = "```\n"
            for x in range(0, number):
                clantag = players['data'][x]['clan_tag']
                for i in self.c:
                    if clantag == self.c[i]['tag']:
                        clanname = self.c[i]['nickname']
                message += (str(x + 1) + ".").ljust(4) + " [" + str(players['data'][x]['trophies']) + "]  " + players['data'][x]['name'] + " (" + clanname + ") " + "\n"
                if (x+1) % 40 == 0:
                    message += "```"
                    await self.bot.say(message)
                    message = "```\n"
            message += "```"
            
        else:
            message = "```\n"
            amount = 0
            for x in range(0, len(players['data'])):
                clanrole = players['data'][x]['role'].replace("-", "").lower()
                clantag = players['data'][x]['clan_tag']
                for i in self.c:
                    if clantag == self.c[i]['tag']:
                        clanname = self.c[i]['nickname']
                            
                if role == clanrole:
                    message += (str(amount + 1) + ".").ljust(4) + " [" + str(players['data'][x]['trophies']) + "]  " + players['data'][x]['name'] + " (" + clanname + ") " +  "\n"
                    amount += 1
                    if amount == number:
                        break
                    if (amount+1) % 40 == 0:
                        message += "```"
                        await self.bot.say(message)
                        message = "```\n"
            message += "```"
        await self.bot.say(message)
        
    @topmembers.command(name="donations")
    async def topmembers_donations(self, role : str = None):
        """Show Family Donations LeaderBoard"""
        number = 10
        if number > 100:
            await self.bot.say("Sorry! the number must be below 100.")
            return
        
        if "family" in self.settings:
            familyname = self.settings['family']
        else:
            familyname = "LeGeND Family"

        if role not in ["leader","coleader","elder", "member", None]:
            await self.bot.say("Invalid role!")
            return
        if role != None:
            filterroles = True
            await self.bot.say("**{0} Donations LeaderBoard** ({1}s)".format(familyname, role))
        else:
            await self.bot.say("**{0} Donations LeaderBoard**".format(familyname))
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
        
        if role == None:
            message = "```\n"
            for x in range(0, number):
                clantag = players['data'][x]['clan_tag']
                for i in self.c:
                    if clantag == self.c[i]['tag']:
                        clanname = self.c[i]['nickname']
                message += (str(x + 1) + ".").ljust(4) + (" [" + str(players['data'][x]['donations']) + "]  ").ljust(9) + players['data'][x]['name'] + " (" + clanname + ") " + "\n"
                if (x+1) % 40 == 0:
                    message += "```"
                    await self.bot.say(message)
                    message = "```\n"
            message += "```"
        else:
            message = "```\n"
            amount = 0
            for x in range(0, len(players['data'])):
                clanrole = players['data'][x]['role'].replace("-", "").lower()
                clantag = players['data'][x]['clan_tag']
                for i in self.c:
                    if clantag == self.c[i]['tag']:
                        clanname = self.c[i]['nickname']
                            
                if role == clanrole:
                    message += (str(amount + 1) + ".").ljust(4) + (" [" + str(players['data'][x]['donations']) + "]  ").ljust(9) + players['data'][x]['name'] + " (" + clanname + ") " +  "\n"
                    amount += 1
                    if amount == number:
                        break
                    if (amount+1) % 40 == 0:
                        message += "```"
                        await self.bot.say(message)
                        message = "```\n"
            message += "```"  
        await self.bot.say(message)
        
    @commands.command()
    async def topclans(self):
        """Show top 10 international clans"""
        
        await self.bot.type()
        try:
            topclans = requests.get("https://api.royaleapi.com/top/clans/_int", headers = self.getAuth(), timeout = 10).json()
            msg = "```python\n"
        
            for x in range(10):
                msg += ((str(topclans[x]["rank"]) + ".").ljust(4) + topclans[x]["name"] + "\n")
            for i in range(10, len(topclans)):
                for j in self.c:
                    if topclans[i]["tag"] == self.c[j]["tag"]:
                        msg += ((str(topclans[i]["rank"]) + ".").ljust(4) + topclans[i]["name"] + "\n")    
            msg += "```"
        
            await self.bot.say("**Top clans in Local International Leaderboard**" + msg)
        except:
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def guest(self, ctx, member: discord.Member):
        """Toggle waiting Role for members"""
        server = ctx.message.server
        author = ctx.message.author

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            ign = profiledata['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
            return

        try:
            newname = ign + " | Guest"
            await self.bot.change_nickname(member, newname)
        except discord.HTTPException:
            await self.bot.say("I don’t have permission to change nick for this user.")
            return

        role = discord.utils.get(server.roles, name="Guest")
        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

        await self.bot.send_message(member,guest_rules)
        await self.bot.say("{} Role Added to {}".format(role.name, member.display_name))

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def inactive(self, ctx, member: discord.Member):
        """Use this command after kicking people from clan"""

        server = ctx.message.server
        author = ctx.message.author
        legendServer = ["374596069989810176"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the LeGeND Family Server")
            return

        rolesToRemove = ["Member"]
        for x in self.c:
            rolesToRemove.append(self.c[x]['role'])

        await self._remove_roles(member, rolesToRemove)
        await self.bot.change_nickname(member, None)

        await self.bot.say("Member and clan roles removed.\nNickname has been reset.")

    @commands.command()
    async def gmt(self):
        """Get the currect GMT time"""
        await self.bot.say(datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M GMT"))

    @commands.command(pass_context=True, no_pm=True)
    async def mm5(self, ctx):
        """ Enter the Qualifier stage for Monthly Mayhem 5"""

        server = ctx.message.server
        member = ctx.message.author
        channel = ctx.message.channel

        await self.bot.say("Sorry big boi, its too late to register now, see you next Month.")
        return

        legendServer = ["393045385662431251"]

        if server.id not in legendServer:
            await self.bot.say("This command can only be executed in the Titan Monthly Mayhem Server: https://discord.gg/ZmeubX7")
            return

        if channel.name != "bot-spam":
            await self.bot.say("You cannot run this command in this channel. Please run this command at #bot-spam")
            return

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('https://api.royaleapi.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            if profiledata['clan'] is None:
                clantag = ""
                clanname = ""
            else: 
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
            await self.bot.say("You must assosiate a tag with this member first using ``!save #tag @member``")
            return

        membership = False
        for clankey in self.clanArray():
            if self.c[clankey]['tag'] == clantag:
                membership = True
                savekey = clankey
                break

        if membership:

            if profiledata['stats']['level'] < 8:
                await self.bot.say("You cannot join the Qualifier Stage as you are not yet level 8 in Clash Royale.")

            await self.bot.say(member.mention + " Have you read and understood how the Monthly Mayhem 5 Qualifier will work and have read and noted the dates and times of the Qualifier tournaments? (Yes/No)")
            answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)
            if answer is None:
                await self.bot.say(member.mention + ' Ok then, I guess its time to read the announcement again.')
                return
            elif "yes" not in answer.content.lower():
                await self.bot.say(member.mention + ' Registration failed.')
                return
    
            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[savekey]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                    return
                else:
                    await self.bot.say("Welcome to Monthly Mayhem 5. Nickname changed to ** {} **\n".format(newname))

            role = discord.utils.get(server.roles, name="MM5")
            try:
                await self.bot.add_roles(member, role)
            except discord.Forbidden:
                raise
            except discord.HTTPException:
                raise
            await self.bot.say("{} Role Added to {}".format(role.name, member.display_name))

        else:
            await self.bot.say("You are not even in any of our clans, what are you doing here?")

    @commands.command(pass_context=True, no_pm=True)
    async def cwstats(self, ctx, tag):
        """Tournament/Clanwar Statistics generator"""

        server = ctx.message.server
        author = ctx.message.author
        
        await self.updateClash()
        await self.bot.type()

        tag = tag.strip('#').upper().replace('O', '0')
        check = ['P', 'Y', 'L', 'Q', 'G', 'R', 'J', 'C', 'U', 'V', '0', '2', '8', '9']

        if any(i not in check for i in tag):
            await self.bot.say("The ID you provided has invalid characters. Please try again.")
            return

        try:
            tourney = requests.get('https://api.royaleapi.com/tournaments/'+tag, headers=self.getAuth(), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return

        clanwar_dict = {}
        
        for y in range(0, len(tourney['members'])):

            tourney_score = tourney['members'][y]['score']

            if 'clan' not in tourney['members'][y]:
                tourney_clan = "OTHERS"
            else:
                tourney_clan = tourney['members'][y]['clan']['name']

            if tourney_clan not in clanwar_dict:
                clanwar_dict[tourney_clan] = {}
                clanwar_dict[tourney_clan]['score'] = 0
                clanwar_dict[tourney_clan]['participants'] = 0

            clanwar_dict[tourney_clan]['score'] += tourney_score
            clanwar_dict[tourney_clan]['participants'] += 1

        message =  "\n**{}**```{}\t{}\t{}\n".format(tourney['name'], "CLAN".ljust(17), "SCORE".ljust(9), "PARTICIPANTS")
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
    f = "cogs/tags.json"
    if not fileIO(f, "check"):
        print("Creating empty tags.json...")
        fileIO(f, "save", {"0" : {"tag" : "DONOTREMOVE"}})

    f = "cogs/clans.json"
    if not fileIO(f, "check"):
        print("Creating empty clans.json...")
        fileIO(f, "save", {})

    f = "cogs/auth.json"
    if not fileIO(f, "check"):
        print("enter your RoyaleAPI token in auth.json...")
        fileIO(f, "save", {"token" : "enter your RoyaleAPI token here!"})
        
    f = "data/legend/settings.json"
    if not fileIO(f, "check"):
        print("Creating empty settings.json...")
        fileIO(f, "save", {})      

    f = "data/seen/seen.json"
    if not fileIO(f, "check"):
        print("Creating empty seen.json...")
        fileIO(f, "save", {})
        
def check_clans():
    c = dataIO.load_json('cogs/clans.json')
    for clankey in c.keys():
        if 'waiting' not in c[clankey]:
            c[clankey]['waiting'] = []
        if 'bonustitle' not in c[clankey]:
            c[clankey]['bonustitle'] = ""
        if 'personalbest' not in c[clankey]:
            c[clankey]['personalbest'] = 0 
        if 'warTrophies' not in c[clankey]:
            c[clankey]['warTrophies'] = 0 
        if 'approval' not in c[clankey]:
            c[clankey]['approval'] = False
        if 'log_channel' not in c[clankey]:
            c[clankey]['log_channel'] = None
    dataIO.save_json('cogs/clans.json', c)

def check_auth():
    c = dataIO.load_json('cogs/auth.json')
    if 'token' not in c:
        c['token'] = ""
    dataIO.save_json('cogs/auth.json', c)
    
def setup(bot):
    check_folders()
    check_files()
    check_clans()
    check_auth()
    bot.add_cog(legend(bot))
