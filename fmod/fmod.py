import discord
from discord.ext import commands
import os
from .utils.dataIO import fileIO, dataIO
from cogs.utils import checks
from __main__ import send_cmd_help
import asyncio
import time
import re
from datetime import datetime
import uuid
from .utils.chat_formatting import pagify, box
try:
    from tabulate import tabulate
except Exception as e:
    raise RuntimeError("You must run `pip3 install tabulate`.") from e


PATH = 'data/fmod/'
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

#stuff for mute time
UNIT_TABLE = {'s': 1, 'm': 60, 'h': 60 * 60, 'd': 60 * 60 * 24}
UNIT_SUF_TABLE = {'sec': (1, ''),
                  'min': (60, ''),
                  'hr': (60 * 60, 's'),
                  'day': (60 * 60 * 24, 's')
                  }

class BadTimeExpr(Exception):
    pass

def _parse_time(time):
    if any(u in time for u in UNIT_TABLE.keys()):
        delim = '([0-9.]*[{}])'.format(''.join(UNIT_TABLE.keys()))
        time = re.split(delim, time)
        time = sum([_timespec_sec(t) for t in time if t != ''])
    elif not time.isdigit():
        raise BadTimeExpr("invalid expression '%s'" % time)
    return int(time)
def _timespec_sec(t):
    timespec = t[-1]
    if timespec.lower() not in UNIT_TABLE:
        raise BadTimeExpr("unknown unit '%c'" % timespec)
    timeint = float(t[:-1])
    return timeint * UNIT_TABLE[timespec]


def _generate_timespec(sec):
    timespec = []

    def sort_key(kt):
        k, t = kt
        return t[0]
    for unit, kt in sorted(UNIT_SUF_TABLE.items(), key=sort_key, reverse=True):
        secs, suf = kt
        q = sec // secs
        if q:
            if q <= 1:
                suf = ''
            timespec.append('%02.d%s%s' % (q, unit, suf))
        sec = sec % secs
    return ', '.join(timespec)

class fmod:
    """A feature packed cog for moderation"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = "data/fmod/settings.json"
        self.settingsload = dataIO.load_json(self.settings)
        self.warnings = "data/fmod/warnings.json"
        self.warningsload = dataIO.load_json(self.warnings)   
        self.handles = {}        
        
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin()
    async def setup(self, ctx):
        """Setup the bot"""
        user = ctx.message.author
        channel = await self.bot.start_private_message(user)
        server = ctx.message.server
        if server.id in self.settingsload:
            await self.bot.send_message(channel, "You currently have data saved. If you would like to change settings please use the `[p]settings` command.")
            return
        else:
            questions = {
                            'Warn Message': None,
                            'Ban Message': None, 
                            'Warn Limit' : None,
                            'Log Channel' : None,
                            'Mute Time' : None,
                            'Mute Role' : None,
                            'Denied Role' : None,
                            'Denied Channel' : None,
                            'DM Warn' : None,
                            'Punishment Roles' : None,
                            'Revoke Message' : None
                        }
            embed = discord.Embed(description = "Welcome to the setup for the fmod cog! You can stop the setup at any time by typing `stop`. By doing this you will CANCEL any information given.\n\n*When you are ready to begin type `start`.*") 
            embedmsg = await self.bot.send_message(channel, embed = embed)
            ready = await self.bot.wait_for_message(channel=channel, author=ctx.message.author, content = 'start')
         
            for a in questions:
                embed = discord.Embed(description = "Welcome to the setup for the fmod cog! You can stop the setup at any time by typing `stop`. *By doing this you will CANCEL any information given.*") 
                if a == 'Warn Message':
                    embed.add_field(name="~~~~", value="**Warn Message** - The message that is sent to the user when they are warned. You can use the following arguments in the message:\n\n```user.mention - mentions the user\nuser.name   - names the user\nuser.id     - gets id of user\nwarn.count  - gets the # of this warn\nwarn.limit  - # of warns allowed```\n\n*Please type your message*", inline = False)
                if a == 'Ban Message':
                    embed.add_field(name="~~~~", value="**Ban Message** - The message that is sent to the user when they are banned.\n\n*Please type your message*", inline = False)
                if a == 'Warn Limit':
                    embed.add_field(name="~~~~", value="**Warn Limit** - The number of warnings before a user is banned.\n\n*Please type the warning number*", inline = False)
                if a == 'Log Channel':
                    embed.add_field(name="~~~~", value="**Log Channel** - The channel where warnings are logged into.\n\n*Please type the channel name*", inline = False)
                if a == 'Mute Time':
                    embed.add_field(name="~~~~", value="**Mute Time** - How long a user is muted for on reaching their first warning.\n\n*Please type the mute time with the relevant time format. (*For minutes 'm', for hours 'h'*)*", inline = False)
                if a == 'Mute Role':
                    embed.add_field(name="~~~~", value="**Mute Role** - The name of the muted role.\n\n*Please type the name of the mute role*", inline = False)
                if a == 'Denied Channel':
                    embed.add_field(name="~~~~", value="**Denied Channel** - The channel the user will be denied access to on using the [p]deny command.\n\n*Please type the channel name.*", inline = False)
                if a == 'Denied Role':
                    embed.add_field(name="~~~~", value="**Denied Role** - The name of the denied role used for disabling access to the denied channel.\n\n*Please type the role name*", inline = False)
                if a == 'Revoke Message':
                    embed.add_field(name="~~~~", value="**Revoke Message** - The message sent when a warning is revoked from a user.\n\n*Please type the message*", inline = False)
                if a == 'DM Warn':
                    embed.add_field(name="~~~~", value="**DM Warn** - Choose if you want warnings to be sent via PM or posted in the channel the warning was executed in.\n\nReply with `true` or `false`", inline = False)
                if a == 'Punishment Roles':
                    embed.add_field(name="~~~~", value="**Punishment Roles** - Choose if you want punishment roles to be added for each warning. (Eg. For 1 warning would have a role with 1 hammer inside. \n\nReply with `true` or `false`", inline = False)
                                       
                await self.bot.edit_message(embedmsg, embed=embed)
                answer = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                if 'stop' in answer.content:
                    await self.bot.send_message(channel, "Stopping....")
                    break
                else:                            
                    while 'Time' in a:                    
                        if "m" in answer.content or "s" in answer.content or "h" in answer.content:
                                questions.update({a : answer.content})
                                break
                        else:
                            await self.bot.send_message(channel, "You've done something wrong! Please make sure that the format is correct!")
                            answer = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)

                    while 'Limit' in a:                    
                        if answer.content.isdigit() == True:
                            questions.update({a : answer.content})
                            break
                        else:
                            await self.bot.send_message(channel, "Please enter a number!")
                            answer = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                    while 'Channel' in a:
                        channelcheck = answer.content
                        chancheck = discord.utils.get(server.channels, name = channelcheck)
                        if chancheck is not None:
                            questions.update({a : answer.content})
                            break
                        else:
                            await self.bot.send_message(channel, "Please enter a valid channel name!")
                            answer = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)   

                    while 'DM' in a or 'Punishment' in a:
                        answering = answer.content
                        if 'true' in answering.lower(): 
                            questions.update({a : True})
                            break                                
                        
                        if 'false' in answering.lower():
                            questions.update({a : False})
                            break
                        else:
                            await self.bot.send_message(channel, "Please enter True or False.")
                            answer = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)   
                            
                    while 'Denied Role' in a or 'Mute Role' in a:                               
                        rolecheck = answer.content
                        rolcheck = discord.utils.get(server.roles, name = rolecheck)
                        if rolcheck is not None:
                            questions.update({a : answer.content})
                            break
                        else:
                            await self.bot.send_message(channel, "Please enter a valid role name!")            
                            answer = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                    while 'Message' in a:
                        questions.update({a : answer.content})
                        break
                    else:
                        questions.update({a : answer.content})

            if not any(x is None for x in questions.values()):
                self.settingsload[server.id] = questions
                dataIO.save_json(self.settings, self.settingsload)
                if 'true' in self.settingsload[server.id]['DM Warn']: 
                    self.settingsload[server.id]['DM Warn'] = True
                else:
                    self.settingsload[server.id]['DM Warn'] = False
                if 'true' in self.settingsload[server.id]['Punishment Roles']:
                    self.settingsload[server.id]['Punishment Roles'] = True
                else:
                    self.settingsload[server.id]['Punishment Roles'] = False
                dataIO.save_json(self.settings, self.settingsload)
                await self.bot.send_message(channel, "Settings saved!")
                await self.currentsettings(ctx, channel, server)
            else:
                pass
    async def currentsettings(self, ctx, channel, server): 
        jsonload = self.settingsload[server.id]
        message = "```\n"
        message += "Warn Message: {Warn Message},\n"
        message += "Ban Message: {Ban Message},\n" 
        message += "Warn Limit : {Warn Limit}, \n"
        message += "Log Channel : {Log Channel}, \n"
        message += "Mute Time : {Mute Time}, \n"
        message += "Mute Role : {Mute Role},\n"
        message += "Denied Role : {Denied Role},\n"
        message += "Denied Channel : {Denied Channel},\n"
        message += "Revoke Message : {Revoke Message},\n"
        message += "DM Warn : {DM Warn},\n"  
        message += "Punishment Roles : {Punishment Roles}"                         
        message += "```"
        await self.bot.send_message(channel, message.format(**jsonload))
           
    @commands.group(no_pm=True, pass_context=True, name='settings')
    @checks.admin() 
    async def _settings(self,ctx):
        """Sets individual settings for the cog"""
        channel = ctx.message.channel
        server = ctx.message.server

        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.currentsettings(ctx, channel, server)
            
    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def muterole(self, ctx, rolename: str):
        """Change the mute role name."""
        server = ctx.message.server
        
        self.settingsload[server.id]["Mute Role"] = rolename
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Muted role name is now: **{}**".format(rolename))

    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def reset(self, ctx):
        """Resets all the settings"""
        server = ctx.message.server
        await self.bot.say("Are you sure you want to reset the settings? Type `yes` to confirm.")
        await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author, content = 'yes')
        del self.settingsload[server.id]
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Settings have been cleared!")
    
    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def mutetime(self, ctx):
        """Change the mute time for the first warning"""
        server = ctx.message.server
        
        await self.bot.say("Please make sure to set the time with the correct time prefix at the end. (*For minutes 'm', for hours 'h'*)\n\nPlease type your timeframe now.")
        muteroletime = await self.bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author)

        if "m" in muteroletime.content or "s" in muteroletime.content or "h" in muteroletime.content:
            self.settingsload[server.id]["Mute Time"] = muteroletime.content
            dataIO.save_json(self.settings,
                             self.settingsload)
            await self.bot.say("Default mute time is now: **{}**".format(muteroletime.content))
        else:
            await self.bot.say("You've done something wrong! Please make sure that the format is correct!")
            return
           

    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def logchannel(self, ctx, channel: str):
        """Change the logging channel."""
        server = ctx.message.server

        self.settingsload[server.id]["Log Channel"] = channel
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Log channel is now: **{}**".format(channel))
            
    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def deniedchannel(self, ctx, channel: str):
        """Change the channel for those that have been denied."""
        server = ctx.message.server

        self.settingsload[server.id]["Denied Channel"] = channel
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Mute channel is now: **{}**".format(channel))            
    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def pm(self, ctx):
        """Enable/disable PM warn"""
        server = ctx.message.server
        if 'DM Warn' not in self.settingsload[server.id]:
            self.settingsload[server.id]['DM Warn'] = False

        p = self.settingsload[server.id]['DM Warn']
        if p:
            self.settingsload[server.id]['DM Warn'] = False
            await self.bot.say("Warnings are now in the channel.")
        elif not p:
            self.settingsload[server.id]['DM Warn'] = True
            await self.bot.say("Warnings are now in DM.")
        dataIO.save_json(self.settings,
                 self.settingsload)

    @_settings.command(no_pm=True, pass_context=True, manage_server=True)
    async def punishrole(self, ctx):
        """Enable/disable hammer emojis per warning."""
        server = ctx.message.server
        true_msg = "Punish emojis per warning enabled."
        false_msg = "Punish emojis per warning disabled."
        if 'Punishment Roles' not in self.settingsload[server.id]:
            self.settingsload[server.id]['Punishment Roles'] = True
            msg = true_msg
        elif self.settingsload[server.id]['Punishment Roles'] == True:
            self.settingsload[server.id]['Punishment Roles'] = False
            msg = false_msg
        elif self.settingsload[server.id]['Punishment Roles'] == False:
            self.settingsload[server.id]['Punishment Roles'] = True
            msg = true_msg
        else:
            msg = "Error."
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say(msg)

    @_settings.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True, manage_server=True)
    async def max(self, ctx, limit: int):
        """Sets the max amount of warnings before banning."""
        server = ctx.message.server

        self.settingsload[server.id]["Warn Limit"] = limit
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Warn limit is now: \n{}".format(limit))

    @_settings.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True, manage_server=True)
    async def revokemsg(self, ctx, *, msg=None):
        """Set the message on warning being revoked."""
        if not msg:
            await self.bot.say("```Set the message on warning being removed.\n\n"
                               "To get a full list of information, use "
                               "**settings message** without any parameters.```")
            return
        server = ctx.message.server

        self.settingsload[server.id]["Revoke Message"] = msg
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Revoke message is now: \n{}".format(msg))
        
    @_settings.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True, manage_server=True)
    async def ban(self, ctx, *, msg=None):
        """Set the ban message."""
        if not msg:
            await self.bot.say("```Set the ban message.\n\n"
                               "To get a full list of information, use "
                               "**settings message** without any parameters.```")
            return
        server = ctx.message.server

        self.settingsload[server.id]["Ban Message"] = msg
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Ban message is now: \n{}".format(msg))
        
    @_settings.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True, manage_server=True)
    async def message(self, ctx, *, msg=None):
        """Set the warning message

        user.mention - mentions the user
        user.name   - names the user
        user.id     - gets id of user
        warn.count  - gets the # of this warn
        warn.limit  - # of warns allowed

        Example:

        **You, user.mention, have received Warning warn.count. After warn.limit,
        you will be banned.**

        You can set it either for every server.
        To set the ban message, use *warnset ban*
        """
        if not msg:
            await self.bot.say("```Set the warning message\n\n"
                               "user.mention - mentions the user\n"
                               "user.name   - names the user\n"
                               "user.id     - gets id of user\n"
                               "warn.count  - gets the # of this warn\n"
                               "warn.limit  - # of warns allowed\n\n"

                               "Example:\n\n"

                               "**You, user.mention, have received Warning "
                               "warn.count. After warn.limit, you will be "
                               "banned.**\n\n"

                               "You can set it either for every server.\n"
                               "To set the ban message, use *warnset ban*\n```")
            return

        server = ctx.message.server
        self.settingsload[server.id]["Warn Message"] = msg
        dataIO.save_json(self.settings,
                         self.settingsload)
        await self.bot.say("Warn message is now: \n{}".format(msg))

    async def filter_message(self, msg, user, count, _max):
        msg = msg.replace("user.mention",
                          user.mention)
        msg = msg.replace("user.name",
                          user.name)
        msg = msg.replace("user.id",
                          user.id)
        msg = msg.replace("warn.count",
                          str(count))
        msg = msg.replace("warn.limit",
                          str(_max))
        return msg
    async def embedlog(self, mod, user, reason, countnum, channel, ID, warntype):
        avatar = user.avatar_url if user.avatar else user.default_avatar_url
        if warntype == 'denied':
            embed=discord.Embed(title="User Denied", color=0xfd9e11)
        elif warntype == 'Ban':
            embed=discord.Embed(title="User Banned", color=0xf01e1e)
        else:
            embed=discord.Embed(title="User Warned", color=0xfd9e11)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Case ID:", value=ID, inline=False)
        embed.add_field(name="User:", value=user, inline=False)
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.add_field(name="Warning Number:", value=countnum, inline=False)
        embed.add_field(name="Attachments:", value='None', inline=False)
        embed.set_footer(text=credits, icon_url=creditIcon)
        react = await self.bot.send_message(channel, embed=embed)
        await self.bot.add_reaction(react, "\U0001f44d")
        await self.bot.add_reaction(react, "\U0001f44e")
        await self.bot.add_reaction(react, "\U0001f937")
        global msgid
        msgid = react.id
    
    @commands.command(no_pm=True, pass_context=True)
    @checks.mod()
    async def warn(self, ctx, user: discord.Member, *, reason: str=None):
        server = ctx.message.server
        author = ctx.message.author
        channel = ctx.message.channel
        can_ban = channel.permissions_for(server.me).ban_members
        can_role = channel.permissions_for(server.me).manage_roles

        if reason is None:
            msg = await self.bot.say("Please enter a reason for the warning!")
            await asyncio.sleep(5)
            await self.bot.delete_message(msg)
            await self.bot.delete_message(ctx.message)
            return

        if can_ban and can_role:
            pass
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.say("Sorry, I can't warn this user.\n"
                               "I am missing the `ban_members` or `manage_roles` permission")
            return
        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        p = self.settingsload[server.id]['DM Warn']
        _max = self.settingsload[server.id]['Warn Limit']
        mutetime = self.settingsload[server.id]['Mute Time']
        msg = self.settingsload[server.id]["Warn Message"]
        ban = self.settingsload[server.id]["Ban Message"]
        
        if server.id not in self.warningsload:
            self.warningsload[server.id] = {}
            dataIO.save_json(self.warnings,
                             self.warningsload)
            if user.id not in self.warningsload[server.id]:
                self.warningsload[server.id][user.id] = {}
                dataIO.save_json(self.warnings,
                                 self.warningsload)
            else:
                pass
        else:
            if user.id not in self.warningsload[server.id]:
                self.warningsload[server.id][user.id] = {}
                dataIO.save_json(self.warnings,
                                 self.warningsload)
            else:
                pass
                
        if "Count" in self.warningsload[server.id][user.id]:
            count = self.warningsload[server.id][user.id]["Count"]
        else:
            count = 0   
        if "ID" in self.warningsload[server.id]:
            ID = self.warningsload[server.id]["ID"]
        else:
            ID = 10000  
        logchannel = self.settingsload[server.id]["Log Channel"]
        channel = discord.utils.get(server.channels, name = logchannel)
        if channel is None:
            msg = await self.bot.say ("I was unable to write to your log channel. Please make sure there is a channel called {} on the server!".format(logchannel))
            return
        else:
            pass
        max = int(_max)    
        #checks for warn number    
        if count == 0:
            count += 1
            self.warningsload[server.id][user.id].update({"Count": count})
            dataIO.save_json(self.warnings,
                             self.warningsload)
            msg = await self.filter_message(msg=msg,
                                            user=user,
                                            count=count,
                                            _max=_max)
            data = discord.Embed(title=server.name, color=0xfd9e11)
            data.add_field(name="Warning",
                           value=msg)
            data.add_field(name="Reason:",
                               value=reason,
                               inline=False)
            data.add_field(name="​​Additional Actions:", value="*In addition to this you have been muted for {} as a result of your actions.*".format(mutetime), inline=False)
            data.set_footer(text=credits, icon_url=creditIcon)
            if p:
                #if dm is on
                await self.bot.send_message(user, embed=data)
                await self.bot.say("Done...")   
            elif not p:
                #if dm is not on
                await self.bot.say(embed=data)
            #run and log
            _max = int(_max)
            countnum = "{}/{}".format(count,_max)
            mod = ctx.message.author
            if 'ID' not in self.warningsload[server.id]:
                self.warningsload[server.id].update({'ID': ID})
                dataIO.save_json(self.warnings,
                             self.warningsload)
            else:
                ID = int(ID)+12
                ID = str(ID)
                self.warningsload[server.id].update({'ID': ID})
                dataIO.save_json(self.warnings,
                             self.warningsload)
            await self._punish_cmd_common(ctx, user, reason=reason)
            await self.embedlog(mod, user, reason, countnum, channel, ID, warntype=True)
            #msgid = ctx.message.id
            if 'Warnings' in self.warningsload[server.id][user.id]:
                pass
            else:
                self.warningsload[server.id][user.id]['Warnings'] = {}
                dataIO.save_json(self.warnings, self.warningsload) 
            self.warningsload[server.id][user.id]["Warnings"][ID] = {
                                        'User': user.id,
                                        'Mod': mod.id,
                                        'Reason': reason,
                                        'Warning Number': countnum,
                                        'Message ID': msgid
                                    }
            dataIO.save_json(self.warnings,
                 self.warningsload) 
            
       
        elif count > 0 and count < max -1:
            count += 1
            self.warningsload[server.id][user.id].update({"Count": count})
            dataIO.save_json(self.warnings,
                             self.warningsload)
            msg = await self.filter_message(msg=msg,
                                            user=user,
                                            count=count,
                                            _max=_max)
            data = discord.Embed(title=server.name, color=0xfd9e11)
            data.add_field(name="Warning",
                           value=msg)
            data.add_field(name="Reason:",
                               value=reason,
                               inline=False)
            data.set_footer(text=credits, icon_url=creditIcon)
            if p:
                #if dm is on
                await self.bot.send_message(user, embed=data) 
                await self.bot.say("Done...")    
            elif not p:
                #if dm is not on
                await self.bot.say(embed=data)
        #run and log
            max = int(_max)  
            countnum = "{}/{}".format(count,_max)
            mod = ctx.message.author
            if 'ID' not in self.warningsload[server.id]:
                self.warningsload[server.id].update({'ID': ID})
                dataIO.save_json(self.warnings,
                             self.warningsload)
            else:
                ID = int(ID)+12
                ID = str(ID)
                self.warningsload[server.id].update({'ID': ID})
                dataIO.save_json(self.warnings,
                             self.warningsload)
            await self.embedlog(mod, user, reason, countnum, channel, ID, warntype=True)
            if 'Warnings' in self.warningsload[server.id][user.id]:
                pass
            else:
                self.warningsload[server.id][user.id]['Warnings'] = {}
                dataIO.save_json(self.warnings, self.warningsload) 
            self.warningsload[server.id][user.id]["Warnings"][ID] = {
                                        'User': user.id,
                                        'Mod': mod.id,
                                        'Reason': reason,
                                        'Warning Number': countnum,
                                        'Message ID': msgid
                                    }
            dataIO.save_json(self.warnings,
                 self.warningsload) 
                 
        else:
            msg = ban
            msg = await self.filter_message(msg=msg,
                                            user=user,
                                            count=count,
                                            _max=_max)
            data = discord.Embed(title=server.name, color=0xf01e1e)
            data.add_field(name="Banned",
                           value=msg)
            data.add_field(name="Reason:",
                               value=reason,
                               inline=False)
            data.set_footer(text=credits, icon_url=creditIcon)
            if p:
                #if dm is on
                await self.bot.send_message(user, embed=data)
                await self.bot.say("Max warning reached, user banned.")    
            elif not p:
                #if dm is not on
                await self.bot.say(embed=data)
        #run and log
            countnum = "Banned"
            mod = ctx.message.author
            if 'ID' not in self.warningsload[server.id]:
                self.warningsload[server.id].update({'ID': ID})
                dataIO.save_json(self.warnings,
                             self.warningsload)
            else:
                ID = int(ID)+12
                ID = str(ID)
                self.warningsload[server.id].update({'ID': ID})
                dataIO.save_json(self.warnings,
                             self.warningsload)
            await self.embedlog(mod, user, reason, countnum, channel, ID, warntype='Ban')
            #msgid = ctx.message.id
            if 'Warnings' in self.warningsload[server.id][user.id]:
                pass
            else:
                self.warningsload[server.id][user.id]['Warnings'] = {}
                dataIO.save_json(self.warnings, self.warningsload) 
            self.warningsload[server.id][user.id]['Warnings'][ID] = {
                                        'User': user.id,
                                        'Mod': mod.id,
                                        'Reason': reason,
                                        'Warning Number': countnum,
                                        'Message ID': msgid
                                    }
            dataIO.save_json(self.warnings,
                 self.warningsload) 
            try:
                await self.bot.ban(user, delete_message_days=0)
            except discord.errors.Forbidden:
                await self.bot.say("I don't have permissions to ban that user.")
        if 'Punishment Roles' in self.settingsload[server.id] and can_role:
            if self.settingsload[server.id]['Punishment Roles'] == True:
                poops = count * "\U0001f528"
                role_name = "Warning {}".format(poops)
                is_there = False
                colour = 0xbc7642
                for role in server.roles:
                    if role.name == role_name:
                        poop_role = role
                        is_there = True
                if not is_there:
                    poop_role = await self.bot.create_role(server)
                    await self.bot.edit_role(role=poop_role,
                                             name=role_name,
                                             server=server)
                try:
                    await self.bot.add_roles(user,
                                             poop_role)
                except discord.errors.Forbidden:
                    await self.bot.say("No permission to add roles")
    
    async def setup_channel(self, channel, role):
        perms = discord.PermissionOverwrite()
        
        if channel.type == discord.ChannelType.text:
            perms.send_messages = False
        elif channel.type == discord.ChannelType.voice:
            perms.speak = False

        await self.bot.edit_channel_permissions(channel, role, overwrite=perms)            
    async def _punish_cmd_common(self, ctx, member, reason):
        server = ctx.message.server
        mutetime = self.settingsload[server.id]["Mute Time"]
        duration = _parse_time(mutetime)
        if duration < 1:
            await self.bot.say("Duration must be 1 second or longer.")
            return False
        rolename = self.settingsload[server.id]['Mute Role']
        role = discord.utils.get(server.roles, name=rolename)
        
        if role is None:
            await self.bot.say("Please make sure the role {} exists!".format(role))
            return

        if role >= server.me.top_role:
            await self.bot.say('The %s role is too high for me to manage.' % role)
            return
        self.warningsload[server.id][member.id]['User Muted'] = {}
        dataIO.save_json(self.warnings, self.warningsload) 
        self.warningsload[server.id][member.id]['User Muted'] = {
            'Action': 'Muted',
            'until': (time.time() + duration),
            'by': member.id,
            'reason': reason
        }
        dataIO.save_json(self.warnings, self.warningsload)
        perms = discord.Permissions.none()
        
        if role is None:
            role = await self.bot.edit_role(server, role, permissions=perms)
            await self.bot.move_role(server, role, server.me.top_role.position - 1)
            for channel in server.channels:
                await self.setup_channel(channel, role)
        await self.bot.add_roles(member, role)

        # schedule callback for role removal
        if duration:
           self.schedule_unpunish(duration, member, reason)

        return True
        
    async def on_channel_create(self, channel):
        """Run when new channels are created and set up role permissions"""
        if channel.is_private:
            return

        server = channel.server
        if server.id != "374596069989810176":
            return
            
        rolename = self.settingsload[server.id]['Mute Role']
        role = discord.utils.get(server.roles, name=rolename)
        if not role:
            return

        await self.setup_channel(channel, role)
    def schedule_unpunish(self, delay, member, reason=None):   
        """Schedules role removal, canceling and removing existing tasks if present"""
        sid = member.server.id

        if sid not in self.handles:
            self.handles[sid] = {}

        if member.id in self.handles[sid]:
            self.handles[sid][member.id].cancel()

        coro = self._unpunish(member, reason)

        handle = self.bot.loop.call_later(delay, self.bot.loop.create_task, coro)
        self.handles[sid][member.id] = handle

    async def _unpunish(self, member, reason=None):
        """Remove punish role, delete record and task handle"""
        server = member.server
        rolename = self.settingsload[server.id]['Mute Role']
        role = discord.utils.get(server.roles, name=rolename)
        if role:
            # Has to be done first to prevent triggering on_member_update listener
            self._unpunish_data(member)
            await self.bot.remove_roles(member, role)

            msg = 'Your punishment in %s has ended.' % member.server.name
            if reason:
                msg += "\nReason was: %s" % reason
                
    def _unpunish_data(self, member):
        """Removes punish data entry and cancels any present callback"""
        sid = member.server.id
        if sid in self.warningsload and member.id in self.warningsload[sid]:
            del(self.warningsload[member.server.id][member.id]['User Muted'])
            dataIO.save_json(self.warnings, self.warningsload)
        
    async def on_member_join(self, member):
        """Restore punishment if punished user leaves/rejoins"""
        server = member.server
        sid = member.server.id

        if server.id != "374596069989810176":
            return
        
        #role = discord.utils.get(server.roles, name=rolename)
        deniedrole = self.settingsload[server.id]['Denied Role']
        
        #re-adds warning roles
        if 'Punishment Roles' in self.settingsload[sid]:
            if self.settingsload[sid]['Punishment Roles'] == True:
                if member.id in self.warningsload[sid]:
                    count = self.warningsload[sid][member.id]["Count"]
                    if count >= 1:
                        poops = "\U0001f528" * count
                        role_name = "Warning {}".format(poops)
                        is_there = False
                        colour = 0xbc7642
                        for role in member.server.roles:
                            if role.name == role_name:
                                poop_role = role
                                is_there = True
                        if not is_there:
                            server = member.server
                            poop_role = await self.bot.create_role(server)
                            await self.bot.edit_role(role=poop_role,
                                                     name=role_name,
                                                     server=server)
                            try:
                                await self.bot.add_roles(member,
                                                         poop_role)
                            except discord.errors.Forbidden:
                                await self.bot.say("No permission to add roles")
                else:
                    pass
        #checks if denied from a channel and re-adds role
        for mid in self.warningsload[sid]:
            try:
                for warning_key, data in self.warningsload[server.id][mid]["Warnings"].items():
                    if data['Warning Number'] == 'Channel Denied':          
                        role = discord.utils.get(server.roles, name=deniedrole)
                        await self.bot.add_roles(member, role)
                        break
            except:
                continue
                
        if member.id in self.warningsload[sid]:
            if 'User Muted' in self.warningsload[sid][member.id]:
                duration = self.warningsload[sid][member.id]['User Muted']['until'] - time.time()
                if duration > 0:
                    rolename = self.settingsload[server.id]['Mute Role']
                    role = discord.utils.get(member.server.roles, name=rolename)
                    await self.bot.add_roles(member, role)
      
                    if member.id not in self.handles[sid]:
                        self.schedule_unpunish(duration, member, reason)

    #other commands
    

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin()
    async def warns(self, ctx):
        """Lists all the warnings on the server"""
        server = ctx.message.server
        server_id = server.id
        newcount = 0
        deniedcheck = True
        if not (server_id in self.warningsload and self.warningsload[server_id]):
            await self.bot.say("No users are currently punished.")
            return
        for mid in self.warningsload[server.id]:
            try:
                for warning_key, data in self.warningsload[server.id][mid].items():
                    count = self.warningsload[server.id][mid]["Count"]
                    newcount += int(count)
                for warning_key, data in self.warningsload[server.id][mid]["Warnings"].items():
                    if data['Warning Number'] == "Channel Denied":
                        deniedcheck = True
                    else:
                        deniedcheck = False
            except:
                continue
                
        def getmname(mid):
            member = discord.utils.get(server.members, id=mid)
            if member:
                    return str(member)
            else:
                mid = str(mid)
                msg = '{}'.format(mid)
                return msg
        if newcount == 0 and deniedcheck == False:
            await self.bot.say("No users are currently punished.")
            return
        headers = ['Case ID', 'Member', 'Warning Number', 'Moderator', 'Reason']
        table = []
        disp_table = []   
        for mid in self.warningsload[server.id]:
            try:
                for warning_key, data in self.warningsload[server.id][mid]["Warnings"].items():
                    warnid = warning_key
                    member_name = getmname(data['User'])
                    numwarns = data['Warning Number']
                    punisher_name = getmname(data['Mod'])
                    reason = data['Reason']
                    table.append((warnid, member_name, numwarns, punisher_name, reason))
            except:
                continue

        for warnid, member_name, numwarns, punisher_name, reason in sorted(table, key=lambda x: x[0]):
            disp_table.append((warnid, member_name, numwarns, punisher_name, reason))

        for page in pagify(tabulate(disp_table, headers)):
            await self.bot.say(box(page))

    async def delwarning(self, ctx, server, warnid, reason):
        server = ctx.message.server
        channel = ctx.message.channel
        revokemessage = self.settingsload[server.id]['Revoke Message']
        rolename = self.settingsload[server.id]['Mute Role']
        role = discord.utils.get(server.roles, name=rolename)
        for mid in self.warningsload[server.id]:
            try:
                for warning_key, data in self.warningsload[server.id][mid]["Warnings"].items():
                    if warning_key == warnid:
                        await self.bot.say("Are you sure you want to delete warn number **{}**?\n\nType `yes` to continue.".format(warnid)) 
                        continuemsg = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                        if 'yes' in continuemsg.content:
                            user = discord.utils.get(server.members, id = mid)
                            if data['Warning Number'] == 'Channel Denied':
                                role = self.settingsload[server.id]['Denied Role']
                                role = discord.utils.get(server.roles, name = role)
                                await self.bot.remove_roles(user,role)
                                await self.bot.say("The denied role has been removed from this user!")
                            else:
                                count = self.warningsload[server.id][mid]["Count"]
                                count = int(count)-1
                                self.warningsload[server.id][mid].update({"Count": count})
                                if 'Punishment Roles' in self.settingsload[server.id]:
                                    if self.settingsload[server.id]['Punishment Roles'] == True:
                                        try:
                                            role = role = list(filter(lambda r: r.name.startswith('Warning \U0001f528'), server.roles))
                                            await self.bot.remove_roles(user, *role)
                                        except discord.errors.Forbidden:
                                            await self.bot.send_message(channel, "No permission to add roles")
                                    if count >= 1:
                                        poops = count * "\U0001f528"
                                        role_name = "Warning {}".format(poops)
                                        is_there = False
                                        colour = 0xbc7642
                                        for role in server.roles:
                                            if role.name == role_name:
                                                poop_role = role
                                                is_there = True
                                        if not is_there:
                                            poop_role = await self.bot.create_role(server)
                                            await self.bot.edit_role(role=poop_role,
                                                                     name=role_name,
                                                                     server=server)
                                        try:
                                            await self.bot.add_roles(user,
                                                                     poop_role)
                                        except discord.errors.Forbidden:
                                            await self.bot.say("No permission to add roles") 
                            embed = discord.Embed(title='Warning Revoked by {}'.format(ctx.message.author), description = revokemessage, color=0x00ff40)
                            embed.add_field(name = 'Reason:', value = reason)
                            embed.set_footer(text=credits, icon_url=creditIcon)
                            channel = await self.bot.start_private_message(user)
                            await self.bot.send_message(channel, embed=embed)
                            warnid = warning_key
                            del(self.warningsload[server.id][mid]['Warnings'][warnid])
                            dataIO.save_json(self.warnings, self.warningsload)
                            logchannel = self.settingsload[server.id]["Log Channel"]
                            logchannel = discord.utils.get(server.channels, name = logchannel)
                            messageid = data['Message ID']

                            await self.bot.say("Warning deleted!")

                            try:
                                embed2 = await self.bot.get_message(logchannel, messageid)
                                newembed = discord.Embed(title='Warning Revoked', color=0x00ff40, description='The warning for **{}** has been revoked by **{}** for the reason **{}**.'.format(user, ctx.message.author, reason))
                                await self.bot.edit_message(embed2, embed=newembed)
                                await self.bot.clear_reactions(embed2)
                            except discord.NotFound:
                                await self.bot.say("Log Message is not found. If you changed the log channel you will need to react to the message there")
                            
                            return
            except:
                continue
        await self.bot.say("This warning was not found. Please make sure you typed it correctly!")
                     
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin()
    async def delwarn(self, ctx, id, *, reason):
        server = ctx.message.server
        channel = ctx.message.channel
        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        await self.delwarning(ctx, server = server, warnid=id, reason=reason)

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin()
    async def setcount(self, ctx, user: discord.Member, count):
        server = ctx.message.server
        channel = ctx.message.channel
        counter = self.warningsload[server.id][user.id]["Count"]
        max = self.warningsload[server.id][user.id]["Warn Limit"]
        max = int(max)
        counter = int(counter)
        count = int(count)
        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        if server.id not in self.warningsload:
            await self.bot.say("This user has no warnings!")
            return        
        
        if user.id not in self.warningsload[server.id]:
            await self.bot.say("This user has no warnings!")
            return
        if counter == 0:
            await self.bot.say("This user has no warnings!")
            return
        if count >= max:
            await self.bot.say("Please set the count to be under the maximum amount of warnings!")
            return
        self.warningsload[server.id][user.id].update({'Count': count})
        dataIO.save_json(self.warnings, self.warningsload)
        await self.bot.say("Count updated!")

    @commands.command(no_pm=True, pass_context=True)
    @checks.mod()
    async def deny(self, ctx, user: discord.Member, *, reason: str=None):
        """Denies a user from the channel"""
        server = ctx.message.server
        user = user
        ID = 10000
        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        revokechannel = self.settingsload[server.id]['Denied Channel']
        deniedrole = self.settingsload[server.id]['Denied Role']
        channel = discord.utils.get(server.channels, name = revokechannel)
        if channel is None:
            msg = await self.bot.say ("I was unable to write to your log channel. Please make sure there is a channel called {} on the server!".format(revokechannel))
            return
        else:
            pass
        if "ID" in self.warningsload[server.id]:
            ID = self.warningsload[server.id]["ID"]
        else:
            ID = 10000  
        if reason is None:
            msg = await self.bot.say("Please enter a reason!")
            await asyncio.sleep(5)
            await self.bot.delete_message(msg)
            return
        if server.id not in self.warningsload:
            self.warningsload[server.id] = {}
            dataIO.save_json(self.warnings,
                             self.warningsload)        
        if user.id in self.warningsload[server.id]:
            for warning_key, data in self.warningsload[server.id][user.id]["Warnings"].items():
                try:
                    if data['Warning Number'] == 'Channel Denied':
                        msg = await self.bot.say("This user has already been denied access to the channel.")
                        await asyncio.sleep(8)
                        await self.bot.delete_message(msg)          
                        await self.bot.delete_message(ctx.message)
                        return
                except:
                    continue

            else:
                role = discord.utils.get(server.roles, name = deniedrole)
                mod = ctx.message.author
                await self.bot.delete_message(ctx.message)
                await self.bot.add_roles(user, role)
                dmuser = await self.bot.start_private_message(user)
                embed = discord.Embed(title='You have been denied from {}'.format(channel), description = 'This is to let you know that you have been denied read permissions for the {} channel.'.format(channel))
                await self.bot.send_message(dmuser, embed=embed)
                reason=reason
                if 'ID' not in self.warningsload[server.id]:
                    self.warningsload[server.id].update({'ID': ID})
                    dataIO.save_json(self.warnings,
                                 self.warningsload)
                else:
                    ID = int(ID)+12
                    ID = str(ID)
                    self.warningsload[server.id].update({'ID': ID})
                    dataIO.save_json(self.warnings,
                                 self.warningsload)
                if 'Warnings' in self.warningsload[server.id][user.id]:
                    pass
                else:
                    self.warningsload[server.id][user.id]['Warnings'] = {}
                    dataIO.save_json(self.warnings, self.warningsload) 
                countnum = 'User Denied'
                logchannel = self.settingsload[server.id]['Log Channel']
                logchannel = discord.utils.get(server.channels, name = logchannel)
                mod = ctx.message.author
                await self.embedlog(mod, user, reason, countnum, logchannel, ID, warntype='denied')
                self.warningsload[server.id][user.id]["Warnings"][ID] = {
                    'Message ID': msgid,
                    'Reason': reason,
                    'Mod': ctx.message.author.id,
                    'User': user.id,
                    'Warning Number': 'Channel Denied'
                }
                dataIO.save_json(self.warnings, self.warningsload)
                for channel in server.channels:
                    perms = discord.PermissionOverwrite()           
                    if channel.type == discord.ChannelType.text:
                        perms.send_messages = False
                        perms.read_messages = False
                    await self.bot.edit_channel_permissions(channel, role, overwrite=perms)            

    @commands.command(no_pm=True, pass_context=True)
    @checks.mod()
    async def attach(self, ctx, warnid):
        """Attaches evidence to a warning"""  
        server = ctx.message.server
        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        def getmname(mid):
            member = discord.utils.get(server.members, id=mid)
            if member:
                if member.nick:
                    return '%s (%s)' % (member.nick, member)
                else:
                    return str(member)
            else:
                mid = str(mid)
                msg = '{} (Member not present)'.format(mid)
                return msg
        for mid in self.warningsload[server.id]:
            try:
                for warning_key, data in self.warningsload[server.id][mid]["Warnings"].items():
                    if warning_key == warnid:
                        logchannel = self.settingsload[server.id]["Log Channel"]
                        logchannel = discord.utils.get(server.channels, name = logchannel)
                        messageid = data['Message ID']
                        await self.bot.say("Warning attachment manager sent through DM!")
                        try:
                            embed2 = await self.bot.get_message(logchannel, messageid)
                        except discord.NotFound:
                            await self.bot.say("Message is not found. If you changed the log channel you will need to react to the message there")
                            return
                        dmchannel = await self.bot.start_private_message(ctx.message.author)
                        await self.bot.send_message(dmchannel, "Please send your attachments for the warning {}. When you have finished please type `stop`.".format(warnid))
                        if 'Attachments' in self.warningsload[server.id][mid]["Warnings"][warnid]:
                            if 'None' not in self.warningsload[server.id][mid]["Warnings"][warnid]['Attachments']:
                                attachlist = self.warningsload[server.id][mid]["Warnings"][warnid]['Attachments']
                        else:
                            attachlist = []
                        stuff = await self.bot.wait_for_message(channel=dmchannel, author=ctx.message.author)
                        while stuff.content is not None:
                            if stuff.content == 'stop':
                                await self.bot.send_message(dmchannel, "Done!")
                                break
                            else:
                                if stuff.attachments or 'discord' in proof.content or 'gyazo' in proof.content or 'prntscr' in proof.content:
                                    if stuff.attachments:
                                        attachmentlist = stuff.attachments[0]
                                        attachment = attachmentlist['url']
                                        attachlist.append(attachment)
                                        await self.bot.add_reaction(stuff, emoji = '\U0001f4ce')
                                        stuff = await self.bot.wait_for_message(channel=dmchannel, author=ctx.message.author)
                                    else:
                                        attachlist.append(stuff.content)
                                        await self.bot.add_reaction(stuff, emoji = '\U0001f4ce')
                                        stuff = await self.bot.wait_for_message(channel=dmchannel, author=ctx.message.author)
                                   
                                else:
                                    await self.bot.send_message(dmchannel, "Please send a picture or a link")
                                    stuff = await self.bot.wait_for_message(channel=dmchannel, author=ctx.message.author)
                        attachlist2 = ('\n'.join(attachlist))
                        embed = embed2.embeds[0]
                        title = embed['title']

                        user = discord.utils.get(server.members, id=data['User'])
                        avatar = user.avatar_url if user.avatar else user.default_avatar_url

                        newembed = discord.Embed(title=title, color=embed['color'])
                        newembed.set_thumbnail(url=avatar)
                        newembed.add_field(name = 'Case ID:', value = warnid, inline = False)
                        newembed.add_field(name = 'User:', value = getmname(data['User']), inline = False)
                        newembed.add_field(name = 'Reason:', value = data['Reason'], inline = False)
                        newembed.add_field(name = 'Warning Number:', value = data['Warning Number'], inline = False)
                        newembed.add_field(name = 'Attachments:', value = attachlist2, inline = False)
                        newembed.set_footer(text=credits, icon_url=creditIcon)
                        await self.bot.edit_message(embed2, embed=newembed)
                        self.warningsload[server.id][mid]["Warnings"][warnid].update({"Attachments": attachlist})                   
                        dataIO.save_json(self.warnings, self.warningsload)
                        return
                    # else:
            except:
                continue
          
    @commands.command(no_pm=True, pass_context=True)
    async def report(self, ctx, user: discord.Member):
        """Reports a user to the staff"""
        server = ctx.message.server
        if server.id not in self.settingsload:
            await self.bot.say("Please run the `[p]setup` command before running this command.")
            return
        channel = await self.bot.start_private_message(ctx.message.author)
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(channel, "You are reporting {}. This will inform the staff members of this users actions. Are you sure you want to continue? \n\n Type `yes` to continue...".format(user))
        await self.bot.wait_for_message(channel = channel, author=ctx.message.author, content = 'yes')
        await self.bot.send_message(channel, "Please enter a reason")
        reason = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
        await self.bot.send_message(channel, "Your reason is {}. Are you sure? \n\nType `yes` to continue or `no` to return.".format(reason.content))
        confirm = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
        attachlist = []
        while confirm.content is not None:
            if confirm.content == 'yes':
                await self.bot.send_message(channel, "Please enter your image attachments as proof. Formats accepted are: Discord, Gyazo and Lightshot. File uploads via discord are also allowed. Once you are done type `send`.")
                proof = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                while proof.content is not None:
                    if proof.content == 'send':
                        await self.bot.send_message(channel, "Sent!")
                        break
                    else:
                        if proof.attachments or 'discord' in proof.content or 'gyazo' in proof.content or 'prntscr' in proof.content:
                            if proof.attachments:
                                attachmentlist = proof.attachments[0]
                                attachment = attachmentlist['url']
                                attachlist.append(attachment)
                                await self.bot.add_reaction(proof, emoji = '\U0001f4ce')
                                proof = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                            else:
                                attachlist.append(proof.content)
                                await self.bot.add_reaction(proof, emoji = '\U0001f4ce')
                                proof = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
                           
                        else:
                            await self.bot.send_message(channel, "Please send a picture or a link")
                            proof = await self.bot.wait_for_message(channel=channel, author=ctx.message.author) 
                break
            if confirm.content == 'no':
                confirm = await self.bot.wait_for_message(channel=channel, author=ctx.message.author)
        logchannel = self.settingsload[server.id]['Log Channel']
        logchannel = discord.utils.get(server.channels, name = logchannel)
        attachlist2 = ('\n'.join(attachlist))
        embed = discord.Embed(title = 'Report', color=0x0080ff)
        embed.add_field(name = 'User:', value = user, inline = False)
        embed.add_field(name = 'Reason:', value = reason.content, inline = False)
        embed.add_field(name = 'Attachments:', value = attachlist2, inline = False)
        embed.set_footer(text=credits, icon_url=creditIcon)
        react = await self.bot.send_message(logchannel, embed = embed)
        await self.bot.add_reaction(react, "\U0001f44d")
        await self.bot.add_reaction(react, "\U0001f44e")
        await self.bot.add_reaction(react, "\U0001f937")
      
def check_folder():
    if not os.path.exists("data/fmod"):
        print("Creating data/fmod/server.id folder")
        os.makedirs("data/fmod")
    if not os.path.exists(PATH):
        log.debug('Creating folder: data/fmod')
        os.makedirs(PATH)


def check_file():
    data = {}
    a = "data/fmod/settings.json"
    b = "data/fmod/warnings.json"
    if not dataIO.is_valid_json(a):
        print("Creating data/fmod/settings.json")
        dataIO.save_json(a,
                         data)
    if not dataIO.is_valid_json(b):
        print("Creating data/fmod/warnings.json")
        dataIO.save_json(b,
                         data) 
def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(fmod(bot))
