import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
import asyncio

import dbHandler

class logging:
    """Message Logging!"""

    def __init__(self, bot):
        self.bot = bot
        self.db = dbHandler.dbHandler("data/sqlite/MessageLog.sqlite3")

    async def on_message(message):
        if message.author != bot.user:
            content = str(message.content) if len(message.content)>0 else ""
            content += str(message.attachments) if len(message.attachments)>0 else ""
            self.db.addLog(message.server, message.id, db.OPERATION_MESSAGE, content, message.author, message.channel, message.timestamp)

    async def on_message_edit(before, after):
        if before.author != bot.user and after.author != bot.user and not before == after:
            content = str(after.content) if len(after.content)>0 else ""
            content += str(after.attachments) if len(after.attachments)>0 else ""
            self.db.addLog(after.server, after.id, db.OPERATION_EDIT, content, after.author, after.channel, after.timestamp)

    async def on_reaction_add(reaction, user):
        if user != bot.user:
            content = str(reaction.message.content) if len(reaction.message.content)>0 else ""
            content += str(reaction.message.attachments) if len(reaction.message.attachments)>0 else ""
            self.db.addReaction(reaction.message.server, reaction.message.id, db.OPERATION_REACT_ADD, content, reaction.emoji, user, reaction.message.channel)

    async def on_reaction_remove(reaction, user):
        if user != bot.user:
            content = str(reaction.message.content) if len(reaction.message.content)>0 else ""
            content += str(reaction.message.attachments) if len(reaction.message.attachments)>0 else ""
            self.db.addReaction(reaction.message.server, reaction.message.id, db.OPERATION_REACT_DELETE, content, reaction.emoji, user, reaction.message.channel)

def check_folders():
    if not os.path.exists("data/sqlite"):
        print("Creating data/Logging folder...")
        os.makedirs("data/sqlite")

def setup(bot):
    check_folders()
    bot.add_cog(logging(bot))