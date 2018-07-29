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
    """Automatically convert Clash Royale friend links to beautiful embeds"""

    def __init__(self, bot):
        self.bot = bot
        self.regex = re.compile(r"<?(https?:\/\/)?(www\.)?(link\.clashroyale\.com\/invite\/friend)\b([-a-zA-Z0-9/]*)>?")
        self.auth = self.bot.get_cog('crtools').auth
        self.clash = clashroyale.RoyaleAPI(self.auth.getToken(), is_async=True)

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name:
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

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

            arenaFormat = profiledata.arena.arena.replace(' ', '').lower()

            embed = discord.Embed(title='Click this link to add as friend in Clash Royale!', url=url[0], color=0x0080ff)
            embed.set_author(name=profiledata.name + " (#"+profiledata.tag+")", icon_url=clanurl)
            embed.set_thumbnail(url="https://imgur.com/C9rLoeh.jpg")
            embed.add_field(name="User", value=message.author.mention, inline=True)
            embed.add_field(name="Trophies", value="{} {:,}".format(self.emoji(arenaFormat), profiledata.trophies), inline=True)
            embed.add_field(name="Level", value="{} {}".format(self.emoji("level"), profiledata.stats.level), inline=True)
            if profiledata.clan is not None:
                embed.add_field(name="Clan {}".format(profiledata.clan.role.capitalize()),
                                value="{} {}".format(self.emoji("clan"), profiledata.clan.name),
                                inline=True)
            embed.set_footer(text=credits, icon_url=creditIcon)

            await self.bot.send_message(message.channel, embed=embed)

            await self.bot.delete_message(message)

        except Exception as e:
            raise
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
