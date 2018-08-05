import discord
from discord.ext import commands
import os
from cogs.utils import checks

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
        self.DB_REACTION_TIMESTAMP = 'timestamp'
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
            c.execute('CREATE table {0} ({1} TEXT, {2} TEXT, {3} TEXT, {4} TEXT, {5} TEXT, {6} TEXT, {7} TEXT, {8} TEXT)'.format(self.DB_TABLE_REACTION, self.DB_REACTION_SERVER_NAME, self.DB_REACTION_CHANNEL_NAME, self.DB_REACTION_OPERATION, self.DB_REACTION_MESSAGE_ID, self.DB_REACTION_MESSAGE, self.DB_REACTION_EMOJI, self.DB_REACTION_USER, self.DB_REACTION_TIMESTAMP))

            self.conn.commit()
            return True
        return False

    def addLog(self, server_name, message_id, operation, message_content, author_name, channel_name, timestamp):
        c = self.conn.cursor()
        ts = str(timestamp)
        c.execute("INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}, {6}, {7}) VALUES (?, ?, ?, ?, ?, ?, ?)".format(self.DB_TABLE_LOG, self.DB_LOG_SERVER_NAME, self.DB_LOG_MESSAGE_ID, self.DB_LOG_OPERATION, self.DB_LOG_MESSAGE_CONTENT, self.DB_LOG_AUTHOR_NAME, self.DB_LOG_CHANNEL_NAME, self.DB_LOG_TIMESTAMP), (str(server_name), str(message_id), str(operation), str(message_content), str(author_name), str(channel_name), ts[:19]))
        self.conn.commit()
        return True

    def addReaction(self, server_name, message_id, operation, reaction_message, emoji, user, channel_name, timestamp):
        c = self.conn.cursor()
        ts = str(timestamp)
        c.execute("INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)".format(self.DB_TABLE_REACTION, self.DB_REACTION_SERVER_NAME, self.DB_REACTION_MESSAGE_ID, self.DB_REACTION_OPERATION, self.DB_REACTION_MESSAGE, self.DB_REACTION_EMOJI, self.DB_REACTION_USER, self.DB_REACTION_CHANNEL_NAME, self.DB_REACTION_TIMESTAMP), (str(server_name), str(message_id), str(operation), str(reaction_message), str(emoji), str(user), str(channel_name), ts[:19]))
        self.conn.commit()
        return True

    def deleteOldLogReaction(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM {0} WHERE ({1} <= datetime('now', '-1 month'))".format(self.DB_TABLE_LOG, self.DB_LOG_TIMESTAMP))
        c.execute("DELETE FROM {0} WHERE ({1} <= datetime('now', '-1 month'))".format(self.DB_TABLE_REACTION, self.DB_REACTION_TIMESTAMP))

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

        if message.author.bot:
            return

        content = str(message.content) if len(message.content) > 0 else ""
        content += "" if not message.attachments else str(message.attachments[0]['url'])
        self.db.addLog(message.server, message.id, self.OPERATION_MESSAGE, content, message.author, message.channel, message.timestamp)

    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        if after.author.bot:
            return

        if before != after:
            content = str(after.content) if len(after.content) > 0 else ""
            content += "" if not after.attachments else str(after.attachments[0]['url'])
            self.db.addLog(after.server, after.id, self.OPERATION_EDIT, content, after.author, after.channel, after.timestamp)

    async def on_reaction_add(self, reaction, user):

        if user.bot:
            return

        content = str(reaction.message.content) if len(reaction.message.content) > 0 else ""
        content += "" if not reaction.message.attachments else str(reaction.message.attachments[0]['url'])
        self.db.addReaction(reaction.message.server, reaction.message.id,
                            self.OPERATION_REACT_ADD, content, reaction.emoji, user,
                            reaction.message.channel, reaction.message.timestamp)

    async def on_reaction_remove(self, reaction, user):

        if user.bot:
            return

        content = str(reaction.message.content) if len(reaction.message.content) > 0 else ""
        content += "" if not reaction.message.attachments else str(reaction.message.attachments[0]['url'])
        self.db.addReaction(reaction.message.server, reaction.message.id, self.OPERATION_REACT_DELETE,
                            content, reaction.emoji, user,
                            reaction.message.channel, reaction.message.timestamp)

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin()
    async def removelogs(self):
        self.db.deleteOldLogReaction()
        print("Logs older than 30 days deleted.")


def check_folders():
    if not os.path.exists("data/sqlite"):
        print("Creating data/Logging folder...")
        os.makedirs("data/sqlite")


def setup(bot):
    check_folders()
    bot.add_cog(logging(bot))
