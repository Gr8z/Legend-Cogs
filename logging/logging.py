import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
import asyncio

import sqlite3

class dbHandler:

  def __init__(self, dbPath):
    self.dbPath = dbPath
    self.DB_TABLE_LOG = 'log'
    self.DB_LOG_SERVER_NAME = 'server_name'
    self.DB_LOG_MESSAGE_ID = 'message_id'
    self.DB_LOG_OPERATION = 'operation_type'
    self.DB_LOG_MESSAGE_CONTENT = 'message_content'
    self.DB_LOG_AUTHOR_NAME = 'author_name'
    self.DB_LOG_CHANNEL_NAME = 'channel_name'
    self.DB_LOG_TIMESTAMP = 'timestamp'
    self.DB_TABLE_REACTION = 'reaction'
    self.DB_REACTION_SERVER_NAME = 'server_name'
    self.DB_REACTION_MESSAGE_ID = 'message_id'
    self.DB_REACTION_OPERATION = 'operation_type'
    self.DB_REACTION_MESSAGE = 'reaction_message'
    self.DB_REACTION_EMOJI = 'reaction_emoji'
    self.DB_REACTION_USER = 'reaction_user'
    self.DB_REACTION_CHANNEL_NAME = 'channel_name'
    self.dbOpen()
    self.createTableIfNotExist()

  def dbOpen(self):
    self.conn = sqlite3.connect(self.dbPath)

  def dbClose(self):
    self.conn.close()

  def createTableIfNotExist(self):
    if self.conn.cursor().execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0] == 0:
      c = self.conn.cursor()
      c.execute('CREATE table {0} ({1} TEXT, {2} TEXT, {3} TEXT, {4} TEXT, {5} TEXT, {6} TEXT, {7} TEXT)'.format(self.DB_TABLE_LOG, self.DB_LOG_SERVER_NAME, self.DB_LOG_CHANNEL_NAME, self.DB_LOG_MESSAGE_ID, self.DB_LOG_OPERATION, self.DB_LOG_MESSAGE_CONTENT, self.DB_LOG_AUTHOR_NAME, self.DB_LOG_TIMESTAMP))
      c.execute('CREATE table {0} ({1} TEXT, {2} TEXT, {3} TEXT, {4} TEXT, {5} TEXT, {6} TEXT, {7} TEXT)'.format(self.DB_TABLE_REACTION, self.DB_REACTION_SERVER_NAME, self.DB_REACTION_CHANNEL_NAME, self.DB_REACTION_OPERATION, self.DB_REACTION_MESSAGE_ID, self.DB_REACTION_MESSAGE, self.DB_REACTION_EMOJI, self.DB_REACTION_USER))

      self.conn.commit()
      return True
    return False

  def addLog(self, server_name, message_id, operation, message_content, author_name, channel_name, timestamp):
    c = self.conn.cursor()
    c.execute("INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}, {6}, {7}) VALUES (?, ?, ?, ?, ?, ?, ?)".format(self.DB_TABLE_LOG, self.DB_LOG_SERVER_NAME, self.DB_LOG_MESSAGE_ID, self.DB_LOG_OPERATION, self.DB_LOG_MESSAGE_CONTENT, self.DB_LOG_AUTHOR_NAME, self.DB_LOG_CHANNEL_NAME, self.DB_LOG_TIMESTAMP), (str(server_name), str(message_id), str(operation), str(message_content), str(author_name), str(channel_name), str(timestamp)))
    self.conn.commit()
    return True

  def addReaction(self, server_name, message_id, operation, reaction_message, emoji, user, channel_name):
    c = self.conn.cursor()
    c.execute("INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}, {6}, {7}) VALUES (?, ?, ?, ?, ?, ?, ?)".format(self.DB_TABLE_REACTION, self.DB_REACTION_SERVER_NAME, self.DB_REACTION_MESSAGE_ID, self.DB_REACTION_OPERATION, self.DB_REACTION_MESSAGE, self.DB_REACTION_EMOJI, self.DB_REACTION_USER, self.DB_REACTION_CHANNEL_NAME), (str(server_name), str(message_id), str(operation), str(reaction_message), str(emoji), str(user), str(channel_name)))
    self.conn.commit()
    return True

class logging:
    """Message Logging!"""

    def __init__(self, bot):
        self.bot = bot
        self.db = dbHandler("data/sqlite/MessageLog.sqlite3")
        self.OPERATION_REACT_ADD = 'A'
        self.OPERATION_REACT_DELETE = 'D'
        self.OPERATION_MESSAGE = 'A'
        self.OPERATION_EDIT = 'E'

    async def on_message(self, message):
        if message.author != self.bot.user:
            content = str(message.content) if len(message.content)>0 else ""
            content += str(message.attachments) if len(message.attachments)>0 else ""
            self.db.addLog(message.server, message.id, self.OPERATION_MESSAGE, content, message.author, message.channel, message.timestamp)

    async def on_message_edit(self, before, after):
        if before.author != self.bot.user and after.author != self.bot.user and not before == after:
            content = str(after.content) if len(after.content)>0 else ""
            content += str(after.attachments) if len(after.attachments)>0 else ""
            self.db.addLog(after.server, after.id, self.OPERATION_EDIT, content, after.author, after.channel, after.timestamp)

    async def on_reaction_add(self, reaction, user):
        if user != self.bot.user:
            content = str(reaction.message.content) if len(reaction.message.content)>0 else ""
            content += str(reaction.message.attachments) if len(reaction.message.attachments)>0 else ""
            self.db.addReaction(reaction.message.server, reaction.message.id, self.OPERATION_REACT_ADD, content, reaction.emoji, user, reaction.message.channel)

    async def on_reaction_remove(self, reaction, user):
        if user != self.bot.user:
            content = str(reaction.message.content) if len(reaction.message.content)>0 else ""
            content += str(reaction.message.attachments) if len(reaction.message.attachments)>0 else ""
            self.db.addReaction(reaction.message.server, reaction.message.id, self.OPERATION_REACT_DELETE, content, reaction.emoji, user, reaction.message.channel)

def check_folders():
    if not os.path.exists("data/sqlite"):
        print("Creating data/Logging folder...")
        os.makedirs("data/sqlite")

def setup(bot):
    check_folders()
    bot.add_cog(logging(bot))