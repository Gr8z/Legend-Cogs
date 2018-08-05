import discord
from discord.ext import commands
import asyncio

BOTCOMMANDER_ROLES = ["Family Representative", "Clan Manager", "Clan Deputy",
                      "Co-Leader", "Hub Officer", "admin", "Member"]


class academy:
    """Legend Family academy for credits"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_any_role(*BOTCOMMANDER_ROLES)
    async def coaching(self, ctx):

        msg_req = ("**Request by:** {}\n"
                   "**In-game name:** {}\n"
                   "**Trophies:** {}\n"
                   "**Wants to learn:** {}\n"
                   "**Time:** {}\n"
                   "**Additional info:** {}\n{}")
        msg_timeout = ("I had to wait too long. "
                       "Start over by typing !coaching again!")
        msg_stop = "Stopped."
        msg_start = "I will ask you few questions, let's move to DM!"
        msg_start_dm = "Lets start! You can stop anytime by typing \"stop\". "

        user = ctx.message.author
        channel = await self.bot.start_private_message(user)
        channel_req = self.bot.get_channel("426689763173597185")
        server_req = self.bot.get_server("374596069989810176")
        coach_role = discord.utils.get(server_req.roles, name="Coach")

        await self.bot.send_message(ctx.message.channel, msg_start)
        await self.bot.send_message(channel, msg_start_dm)
        await asyncio.sleep(3)
        await self.bot.send_message(channel, "What's your in-game name?")
        reply = (await self.bot.wait_for_message(channel=channel, author=user, timeout=90))
        if reply is None:
            await self.bot.send_message(channel, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(channel, msg_stop)
            return
        else:
            ingame_name = reply.content

        await self.bot.send_message(channel, "How many trophies do you have?")
        reply = await self.bot.wait_for_message(channel=channel, author=user, timeout=90)
        if reply is None:
            await self.bot.send_message(channel, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(channel, msg_stop)
            return
        else:
            trophies = reply.content

        await self.bot.send_message(channel, "What archetype/deck do you want to learn?")
        reply = await self.bot.wait_for_message(channel=channel, author=user, timeout=120)
        if reply is None:
            await self.bot.send_message(channel, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(channel, msg_stop)
            return
        else:
            info = reply.content

        await self.bot.send_message(channel, "What time do you prefer (with timezones) for coaching?")
        reply = await self.bot.wait_for_message(channel=channel, author=user, timeout=120)
        if reply is None:
            await self.bot.send_message(channel, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(channel, msg_stop)
            return
        else:
            time = reply.content

        await self.bot.send_message(channel, "Do you have anything else you want to add? (Type \"No\" if not)")
        reply = await self.bot.wait_for_message(channel=channel, author=user, timeout=120)
        if reply is None:
            await self.bot.send_message(channel, msg_timeout)
            return
        elif reply.content.lower() == "stop":
            await self.bot.send_message(channel, msg_stop)
            return
        else:
            more_info = reply.content

        await self.bot.send_message(channel_req,
                                    msg_req.format(
                                        user.mention,
                                        ingame_name,
                                        trophies,
                                        info,
                                        time,
                                        more_info,
                                        coach_role.mention)
                                    )

        await self.bot.send_message(channel, "Ok! I sent your request to coaches, "
                                             "someone will get to you as soon as possible.")


def setup(bot):
    bot.add_cog(academy(bot))
