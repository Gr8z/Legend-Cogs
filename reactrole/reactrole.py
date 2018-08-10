# Game made by GR8 from Legend Family.

import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
import os
from cogs.utils import checks
from copy import deepcopy

settings_path = "data/reactrole/settings.json"
default_settings = {"roles": {}, "messages": []}

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"


class reactrole:
    """Clash Royale 1v1 Duels with bets"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(settings_path)

    def add_defualt_settings(self, server):
        if server.id not in self.settings:
            self.settings[server.id] = deepcopy(default_settings)
            dataIO.save_json(settings_path, self.settings)

    @commands.group(pass_context=True, name="reactrole")
    @checks.mod_or_permissions(administrator=True)
    async def _reactrole(self, ctx):
        """Base command for managing reaction roles"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_reactrole.command(pass_context=True, name="add")
    @checks.mod_or_permissions(administrator=True)
    async def _reactrole_add(self, ctx, emoji, role: discord.Role):
        """Link a role to an emoji reaction"""
        server = ctx.message.server
        emoji = str(emoji.replace(">", "").replace("<", ""))
        self.add_defualt_settings(server)

        try:
            await self.bot.add_reaction(ctx.message, emoji)
        except (discord.errors.HTTPException, discord.errors.InvalidArgument):
            return await self.bot.say("Error, That's not an emoji I recognize.")

        if emoji in self.settings[server.id]["roles"]:
            return await self.bot.say("Error, that emoji is already linked to a role.")

        self.settings[server.id]["roles"][emoji] = role.id
        await self.bot.say("<{}> is now linked to {}.".format(emoji, role.name))
        dataIO.save_json(settings_path, self.settings)

    @_reactrole.command(pass_context=True, name="remove")
    @checks.mod_or_permissions(administrator=True)
    async def _reactrole_remove(self, ctx, emoji):
        """Remove an emoji from reactrole"""
        server = ctx.message.server
        emoji = str(emoji.replace(">", "").replace("<", ""))
        self.add_defualt_settings(server)

        try:
            await self.bot.add_reaction(ctx.message, emoji)
        except (discord.errors.HTTPException, discord.errors.InvalidArgument):
            return await self.bot.say("Error, That's not an emoji I recognize.")

        if emoji not in self.settings[server.id]["roles"]:
            return await self.bot.say("Error, that emoji is not linked to a role.")

        self.settings[server.id]["roles"].pop(emoji)
        await self.bot.say("<{}> is now removed from reactrole.".format(emoji))
        dataIO.save_json(settings_path, self.settings)

    @_reactrole.command(pass_context=True, name="message")
    @checks.mod_or_permissions(administrator=True)
    async def _reactrole_message(self, ctx, messageID: int):
        """Add a message to react to, to get roles

        To get a message id, enable developer mode in Discord's
        settings, 'appearance' tab. Then right click a message
        and copy its id.

        You can use this command again to add more messages.
        """
        server = ctx.message.server
        channel = ctx.message.channel
        self.add_defualt_settings(server)

        if messageID in self.settings[server.id]["messages"]:
            self.settings[server.id]["messages"].remove(messageID)
            dataIO.save_json(settings_path, self.settings)
            return await self.bot.say("Reactrole will no longer check for reactions in that message.")

        msg = await self.bot.get_message(channel, messageID)
        if not msg:
            return await self.bot.say("Error, Message not found, execute this command where the message exists.")

    @_reactrole.command(pass_context=True, name="embed")
    @checks.mod_or_permissions(administrator=True)
    async def _reactrole_embed(self, ctx):
        """Dummy embed (do not use)"""
        server = ctx.message.server
        embed = discord.Embed(title="Notification Roles", description="React with emojis to choose which notifications you would like to turn on!", color=0x0080ff)
        embed.add_field(name="Tournaments", value=f"<:tourney:466243255504470036> — When a 100-1000 player tournament is posted in {server.get_channel('374597050530136064').mention}", inline=False)
        embed.add_field(name="Giveaways", value=f"<:coin:380832316932489268> — When a giveaway for credits/games is hosted in {server.get_channel('421623464567504896').mention}", inline=False)
        embed.add_field(name="Challenges", value=f":hourglass: — When a Word Challenge Game starts in {server.get_channel('405062108175269898').mention}", inline=False)
        embed.add_field(name="Heist", value=f":bank: — When a Heist is planned in {server.get_channel('381338682298466315').mention}", inline=False)
        embed.add_field(name="Duels", value=f"<:battle:466243249149837314> — When a player is looking for a Clash Royale battle in {server.get_channel('430083671429611530').mention}", inline=False)
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.say(embed=embed)

    async def on_reaction_add(self, reaction, user):
        if not reaction.message.channel.is_private and self.bot.user.id != user.id:
            server = reaction.message.server
            channel = reaction.message.channel
            reactionEmoji = str(reaction.emoji).replace(">", "").replace("<", "")
            if int(reaction.message.id) in self.settings[server.id]["messages"]:
                emoji = self.settings[server.id]["roles"]
                if reactionEmoji in emoji.keys():
                    role = discord.utils.get(server.roles, id=emoji[reactionEmoji])
                    if role is None:
                        return await self.bot.send_message(channel, "ReactRole: Role not found.")
                    try:
                        await self.bot.add_roles(user, role)
                    except discord.errors.Forbidden:
                        await self.bot.send_message(channel, "ReactRole: No permission to add roles.")

    async def on_reaction_remove(self, reaction, user):
        if not reaction.message.channel.is_private and self.bot.user.id != user.id:
            server = reaction.message.server
            channel = reaction.message.channel
            reactionEmoji = str(reaction.emoji).replace(">", "").replace("<", "")
            if int(reaction.message.id) in self.settings[server.id]["messages"]:
                emoji = self.settings[server.id]["roles"]
                if reactionEmoji in emoji.keys():
                    role = discord.utils.get(server.roles, id=emoji[reactionEmoji])
                    if role is None:
                        return await self.bot.send_message(channel, "ReactRole: Role not found.")
                    try:
                        await self.bot.remove_roles(user, role)
                    except discord.errors.Forbidden:
                        await self.bot.send_message(channel, "ReactRole: No permission to remove roles.")


def check_folders():
    if not os.path.exists("data/reactrole"):
        print("Creating data/reactrole folder...")
        os.makedirs("data/reactrole")


def check_files():
    f = settings_path
    if not fileIO(f, "check"):
        print("Creating reactrole settings.json...")
        fileIO(f, "save", {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(reactrole(bot))
