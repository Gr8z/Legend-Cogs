import discord
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
        self.constants = self.bot.get_cog('crtools').constants
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)

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

            try:
                profiledata = await self.clash.get_player(profiletag)
            except clashroyale.RequestError:
                return

            arenaFormat = profiledata.arena.name.replace(' ', '').lower()

            embed = discord.Embed(title='Click this link to add as friend in Clash Royale!', url=url[0], color=0x0080ff)
            embed.set_author(name=profiledata.name + " ("+profiledata.tag+")", icon_url=await self.constants.get_clan_image(profiledata))
            embed.set_thumbnail(url="https://imgur.com/C9rLoeh.jpg")
            embed.add_field(name="User", value=message.author.mention, inline=True)
            embed.add_field(name="Trophies", value="{} {:,}".format(self.emoji(arenaFormat), profiledata.trophies), inline=True)
            embed.add_field(name="Level", value=self.emoji("level{}".format(profiledata.expLevel)), inline=True)
            if profiledata.clan is not None:
                embed.add_field(name="Clan {}".format(profiledata.role.capitalize()),
                                value="{} {}".format(self.emoji("clan"), profiledata.clan.name),
                                inline=True)
            embed.set_footer(text=credits, icon_url=creditIcon)

            await self.bot.send_message(message.channel, embed=embed)

            await self.bot.delete_message(message)

        except Exception as e:
            raise
            return

    async def on_message(self, message):

        author = message.author

        if author.id == self.bot.user.id:
            return

        if self.regex.search(message.content) is None:
            return

        await self.friend_link(message)


def setup(bot):
    bot.add_cog(friendlink(bot))
