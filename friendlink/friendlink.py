import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
import asyncio
import re
import urllib.parse as urlparse
import clashroyale

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

class friendlink:
    """friendlink!"""

    def __init__(self, bot):
        self.bot = bot
        self.regex = re.compile(r"<?(https?:\/\/)?(www\.)?(link\.clashroyale\.com\/invite\/friend)\b([-a-zA-Z0-9/]*)>?")
        self.auth = self.bot.get_cog('crtools').auth
        self.clash = clashroyale.Client(self.auth.getToken(), is_async=True)

    async def friend_link(self, message):

        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)

        try:

            parsed = urlparse.urlparse(url[0])
            profiletag = urlparse.parse_qs(parsed.query)['tag'][0]
            token = urlparse.parse_qs(parsed.query)['token'][0]
            platform = urlparse.parse_qs(parsed.query)['platform'][0]

            try:
                profiledata = await self.clash.get_player(profiletag)
            except clashroyale.RequestError:
                return

            if profiledata.clan is None:
                clanurl = "https://i.imgur.com/4EH5hUn.png"
            else:
                clanurl = profiledata.clan.badge.image

            embed=discord.Embed(title='Click this link to add as friend in Clash Royale!', url=url[0], color=0x0080ff)
            embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", icon_url=clanurl)
            embed.set_thumbnail(url="https://imgur.com/C9rLoeh.jpg")
            embed.add_field(name="User", value=message.author.mention, inline=True)
            embed.add_field(name="Trophies", value=profiledata.trophies, inline=True)
            if profiledata.clan is not None:
                embed.add_field(name="Clan", value=profiledata.clan.name, inline=True)
            embed.add_field(name="Arena", value=profiledata.arena.name, inline=True)
            embed.set_footer(text=credits, icon_url=creditIcon)

            await self.bot.send_message(message.channel, embed=embed)

            await self.bot.delete_message(message)

        except Exception as e:
            return

    async def on_message(self, message):

        server = message.server
        author = message.author

        if message.author.id == self.bot.user.id:
            return

        if self.regex.search(message.content) is None:
            return

        await self.friend_link(message)

def setup(bot):
    bot.add_cog(friendlink(bot))