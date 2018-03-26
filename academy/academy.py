import discord
from discord.ext import commands
import requests
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks
import asyncio
import json

class academy:
    """Legend Family academy for credits"""

    def __init__(self, bot):
        self.bot = bot
        self.tags = dataIO.load_json('cogs/tags.json')
        self.clans = dataIO.load_json('cogs/clans.json')
        self.auth = dataIO.load_json('cogs/auth.json')

    def getAuth(self):
        return {"auth" : self.auth['token']}

    async def updateClash(self):
        self.tags = dataIO.load_json('cogs/tags.json')

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
            
    def clanArray(self):
        return self.clans.keys()

    def numClans(self):
        return len(self.clans.keys())

    async def mass_purge(self, messages):
        while messages:
            if len(messages) > 1:
                await self.bot.delete_messages(messages[:100])
                messages = messages[100:]
            else:
                await self.bot.delete_message(messages[0])
                messages = []
            await asyncio.sleep(1.5)

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def keepcleaning(self, ctx, message_id : int):
        """ Clean the channel its executed on"""
        channel = ctx.message.channel
        author = ctx.message.author
        server = channel.server
        has_permissions = channel.permissions_for(server.me).manage_messages

        to_delete = []

        after = await self.bot.get_message(channel, message_id)

        if not has_permissions:
            await self.bot.say("I'm not allowed to delete messages.")
            return
        elif not after:
            return

        async for message in self.bot.logs_from(channel, limit=2000,
                                                after=after):
            to_delete.append(message)
            
        await self.mass_purge(to_delete)   
        
    @commands.command(pass_context=True)
    async def coaching(self, ctx):  
        msg_req = "**Request by:** {}\n**In-game name:** {}\n**Trophies:** {}\n**Wants to learn:** {}\n**Time:** {}\n**Additional info:** {}\n{}"
        msg_timeout = "I had to wait too long. Start over by typing !coaching again!"
        msg_stop = "Stopped."
        msg_err = "Process was interrupted! Please do not send messages in LeGeND server while filling the request! Start over by typing !coaching."
        msg_start = "I will ask you few questions, let's move to DM!"
        msg_start_dm = "Please do not send any message to LeGeND server while filling this request! You can stop anytime by typing \"stop\". Let's start!"
        
        user = ctx.message.author
        channel_req = self.bot.get_channel("426689763173597185")
        server_req = self.bot.get_server("374596069989810176")
        coach_role= discord.utils.get(server_req.roles, name="Coach")
    
        await self.bot.send_message(ctx.message.channel, msg_start)
        await self.bot.send_message(user, msg_start_dm)
        await asyncio.sleep(3)
        await self.bot.send_message(user, "What's your in-game name?")
        reply = (await self.bot.wait_for_message(author=user, timeout=90))
        if reply == None:
            await self.bot.send_message(user, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(user, msg_stop)
            return
        if not reply.channel.is_private:
            await self.bot.send_message(user, msg_err)
            return
        else:
            ingame_name = reply.content
                 
        await self.bot.send_message(user, "How many trophies do you have?")
        reply = (await self.bot.wait_for_message(author = user, timeout=90))
        if reply == None:
            await self.bot.send_message(user, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(user, msg_stop)
            return
        if not reply.channel.is_private:
            await self.bot.send_message(user, msg_err)
            return
        else:
            trophies = reply.content
        
        await self.bot.send_message(user, "What archetype/deck do you want to learn?")
        reply = (await self.bot.wait_for_message(author=user, timeout=120))
        if reply == None:
            await self.bot.send_message(user, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(user, msg_stop)
            return
        if not reply.channel.is_private:
            await self.bot.send_message(user, msg_err)
            return
        else:
            info = reply.content 
        
        await self.bot.send_message(user, "What time do you prefer (with timezones) for coaching?")
        reply = (await self.bot.wait_for_message(author=user, timeout=120))
        if reply == None:
            await self.bot.send_message(user, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(user, msg_stop)
            return
        if not reply.channel.is_private:
            await self.bot.send_message(user, msg_err)
            return
        else:
            time = reply.content        
        
        await self.bot.send_message(user, "Do you have anything else you want to add? (Type \"No\" if not)")
        reply = (await self.bot.wait_for_message(author = user, timeout=120))
        if reply == None:
            await self.bot.send_message(user, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(user, msg_stop)
            return
        if not reply.channel.is_private:
            await self.bot.send_message(user, msg_err)
            return
        else:
            more_info = reply.content        
        
        await self.bot.send_message(channel_req, msg_req.format(user.display_name, ingame_name, trophies, info, time, more_info, coach_role.mention))
        await self.bot.send_message(user, "Ok! I sent your request to coaches, someone will get to you as soon as possible.")


def setup(bot):
    bot.add_cog(academy(bot))
