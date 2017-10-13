import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
import asyncio

class profanity:
    """profanity!"""

    def __init__(self, bot):
        self.bot = bot
        self.bannedwords = dataIO.load_json('data/Profanity/banned_words.json')

    async def banned_words(self, message):

        word_set = set(self.bannedwords)
        phrase_set = set(message.content.replace("*", "").replace("_", "").replace("#", "").split())
        if word_set.intersection(phrase_set):
            await self.bot.delete_message(message)
            msg = await self.bot.send_message(
                message.channel,
                "{}, **We do not allow Hateful, obscene, offensive, racist, sexual, or violent words in any public channels.**".format(
                    message.author.mention
                )
            )
            await asyncio.sleep(6)
            await self.bot.delete_message(msg)
            return

    async def on_message_edit(self, before, after):
        await self.banned_words(after)

    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        await self.banned_words(message)

def check_folders():
    if not os.path.exists("data/Profanity"):
        print("Creating data/Profanity folder...")
        os.makedirs("data/Profanity")

def check_files():
    f = "data/Profanity/banned_words.json"
    if not fileIO(f, "check"):
        print("Creating empty banned_words.json...")
        fileIO(f, "save", [])

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(profanity(bot))