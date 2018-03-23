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

        logger.info("{}({}) deleted {} messages in channel {}"
                    "".format(author.name, author.id,
                              len(to_delete), channel.name))

        await self.mass_purge(to_delete)   


def setup(bot):
    bot.add_cog(academy(bot))