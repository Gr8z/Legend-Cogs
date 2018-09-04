import discord
from discord.ext import commands
import clashroyale
from copy import deepcopy
from .utils.dataIO import dataIO
from random import choice as rand_choice
from .utils import checks
import asyncio


def embed(**kwargs):
    return discord.Embed(**kwargs).set_footer(
        text="Legend Family",
        icon_url="https://i.imgur.com/dtSMITE.jpg"
    )


class Letter:
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = \
        "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", \
        "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"
    alphabet = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z]


class Symbol:
    white_check_mark = "✅"
    arrow_backward = "◀"


dm_menu = {
    "main": {
        "embed": embed(title="Welcome", color=discord.Color.orange(),
                       description="Welcome to the Legend Family Server, {0.mention}! "
                                   "We are one of the oldest and biggest families in "
                                   "Clash Royale with our 700 members and 14 clans! "
                                   "<a:goblinstab:468708996153475072>\n\n"
                                   "We are glad you joined us, can we ask a few questions "
                                   "to customize your experience?"),
        "thumbnail": "https://cdn.discordapp.com/icons/374596069989810176/8cadece4b0197ce2a77a4c41a490f0fc.jpg",
        "options": [
            {
                "name": "Yes please!",
                "emoji": Letter.a,
                "execute": {
                    "menu": "refferal_menu"
                }
            },
            {
                "name": "Skip it, and talk to our friendly staff.",
                "emoji": Letter.b,
                "execute": {
                    "menu": "leave_alone"
                }
            }
        ],
        "go_back": False
    },
    "refferal_menu": {
        "embed": embed(title="How did you get here?", color=discord.Color.orange(),
                       description="We know you are from the interwebz. "
                                   "But where exactly did you find us?"),
        "options": [
            {
                "name": "Legend Website",
                "emoji": Letter.a,
                "execute": {
                    "menu": "location_menu"
                }
            },
            {
                "name": "RoyaleAPI Website",
                "emoji": Letter.b,
                "execute": {
                    "menu": "location_menu"
                }
            },
            {
                "name": "Reddit",
                "emoji": Letter.c,
                "execute": {
                    "menu": "location_menu"
                }
            },
            {
                "name": "Discord",
                "emoji": Letter.d,
                "execute": {
                    "menu": "location_menu"
                }
            },
            {
                "name": "Twitter",
                "emoji": Letter.e,
                "execute": {
                    "menu": "location_menu"
                }
            },
            {
                "name": "From in-game",
                "emoji": Letter.f,
                "execute": {
                    "menu": "location_menu"
                }
            },
            {
                "name": "Other",
                "emoji": Letter.g,
                "execute": {
                    "menu": "location_menu"
                }
            }
        ],
        "go_back": True,
        "track": True
    },
    "location_menu": {
        "embed": embed(title="What part of the world do you come from?", color=discord.Color.orange(),
                       description="To better serve you, "
                                   "pick the region you currently live in."),
        "options": [
            {
                "name": "North America",
                "emoji": Letter.a,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "South America",
                "emoji": Letter.b,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Northern Africa",
                "emoji": Letter.c,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Southern Africa",
                "emoji": Letter.d,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Europe",
                "emoji": Letter.e,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Middle East",
                "emoji": Letter.f,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Asia",
                "emoji": Letter.g,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Southeast Asia",
                "emoji": Letter.h,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Australia",
                "emoji": Letter.i,
                "execute": {
                    "menu": "age_menu"
                }
            }
        ],
        "go_back": True,
        "track": True
    },
    "age_menu": {
        "embed": embed(title="How old are you?", color=discord.Color.orange(),
                       description="Everyone is welcome! "
                                   "However, some clans do require you to be of a"
                                   " certain age group. Please pick one."),
        "options": [
            {
                "name": "Under 16",
                "emoji": Letter.a,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "16-20",
                "emoji": Letter.b,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "21-30",
                "emoji": Letter.c,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "31-40",
                "emoji": Letter.d,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "41-50",
                "emoji": Letter.e,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "51-60",
                "emoji": Letter.f,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "61 or Above",
                "emoji": Letter.g,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "Prefer Not to Answer",
                "emoji": Letter.h,
                "execute": {
                    "menu": "save_tag_menu"
                }
            }
        ],
        "go_back": True,
        "track": True
    },
    "save_tag_menu": {
        "embed": embed(title="What is your Clash Royale player tag?", color=discord.Color.orange(),
                       description="Before we let you talk in the server, we need to take a look at your stats. "
                                   "To do that, we need your Clash Royale player tag.\n\n"),
        "options": [
            {
                "name": "Continue",
                "emoji": Letter.a,
                "execute": {
                    "menu": "save_tag"
                }
            },
            {
                "name": "I don't play Clash Royale",
                "emoji": Letter.b,
                "execute": {
                    "menu": "leave_alone"
                }
            }
        ],
        "go_back": True
    },
    "save_tag": {
        "embed": embed(title="Type in your tag", color=discord.Color.orange(),
                       description="Please type **!savetag #YOURTAG** below to submit your ID.\n\n"
                                   "You can find your player tag in your profile in game."),
        "image": "https://legendclans.com/wp-content/uploads/2017/11/profile_screen3.png",
        "options": [],
        "go_back": True
    },
    "choose_path": {
        "embed": embed(title="So, why are you here?", color=discord.Color.orange(),
                       description="Please select your path "
                                   "below to get started."),
        "options": [
            {
                "name": "I am just visiting.",
                "emoji": Letter.a,
                "execute": {
                    "function": "guest"
                }
            },
            {
                "name": "I want to join a clan.",
                "emoji": Letter.b,
                "execute": {
                    "menu": "join_clan"
                }
            },
            {
                "name": "I am already in one of your clans.",
                "emoji": Letter.c,
                "execute": {
                    "function": "verify_membership"
                }
            }
        ],
        "go_back": False,
        "track": True
    },
    "join_clan": {
        "embed": embed(title="Legend Family Clans", color=discord.Color.orange(),
                       description="Here are all our clans, which clan do you prefer?"),
        "dynamic_options": "clans_options",
        "options": [],
        "go_back": True,
        "track": True
    },
    "end_member": {
        "embed": embed(title="That was it", color=discord.Color.orange(),
                       description="Your chosen clan has been informed. "
                                   " Please wait in #welcome-gate channel "
                                   "while a discord officer comes to approve you.\n\n"
                                   " Please do not join any clans without talking to an officer.\n\n"
                                   "**Enjoy your stay!**"),
        "options": [
            {
                "name": "Go to #welcome-gate",
                "emoji": Letter.a,
                "execute": {
                    "menu": "welcome_gate"
                }
            }
        ],
        "go_back": False,
        "finished": True
    },
    "end_human": {
        "embed": embed(title="Requesting assistance", color=discord.Color.orange(),
                       description="We have notified our officers about your information."
                                   " Please wait in #welcome-gate "
                                   "channel while an officer comes and helps you.\n\n"
                                   " Please do not join any clans without talking to an officer.\n\n"
                                   "**Enjoy your stay!**"),
        "options": [
            {
                "name": "Go to #welcome-gate",
                "emoji": Letter.a,
                "execute": {
                    "menu": "welcome_gate"
                }
            }
        ],
        "go_back": False,
        "finished": True
    },
    "end_guest": {
        "embed": embed(title="Enjoy your stay", color=discord.Color.orange(),
                       description="Welcome to the **Legend Family** Discord server. "
                       "As a guest, you agree to the following rules:\n\n"
                       "• Respect others' opinions. If you disagree, please do so "
                       "in a constructive manner.\n• This is an English only server, "
                       "please use any other languages in a private message.\n"
                       "• Do not spam, and avoid ever using @clanname without "
                       "permission from clan managers or deputies.\n"
                       "• No advertisement of any kind, e.g. clans, websites, "
                       "discord invites, etc.\n• Use #bot-spam for bot features, "
                       "e.g. !deck or !payday.\n• Respect and do not subvert "
                       "moderators or managers.\n• A good rule is to talk to "
                       "people as if you were talking to them face to face.\n\n"
                       "Failure to follow these rules will get you kicked from the server. "
                       "Repeat offenders will be banned.\n\nYou can chat with "
                       "family members and guests in `#global-chat`. "
                       "For games, you can check out `#heist` `#duels` "
                       "and `#challenges`.\n\nIf you would like to invite "
                       "your friends to join this server, you may use this "
                       "Discord invite: <https://discord.gg/yhD84nK>\n\n"
                       "Additional help and information: https://legendclans.com\n\n"
                       "Thanks + enjoy!\n"),
        "options": [
            {
                "name": "Go to #global-chat",
                "emoji": Letter.a,
                "execute": {
                    "menu": "global_chat"
                }
            }
        ],
        "go_back": False,
        "finished": True
    },
    "give_tags": {
        "embed": embed(title="Membership verified", color=discord.Color.orange(),
                       description="We have unlocked all member channels for you, enjoy your stay!"),
        "options": [
            {
                "name": "Go to #global-chat",
                "emoji": Letter.a,
                "execute": {
                    "menu": "global_chat"
                }
            }
        ],
        "go_back": False,
        "finished": True
    },
    "leave_alone": {
        "embed": embed(title="Enjoy your stay", color=discord.Color.orange(),
                       description="We look forward to welcoming "
                                   "you into the Legend Clan Family!\n\n"
                                   "You can go talk to an officer in #welcome-gate. "),
        "options": [
            {
                "name": "Go to #welcome-gate",
                "emoji": Letter.a,
                "execute": {
                    "menu": "welcome_gate"
                }
            }
        ],
        "go_back": False,
        "finished": True
    },
    "global_chat": {
        "embed": embed(title="#global-chat", color=discord.Color.orange(),
                       description="Click here: http://discord.gg/T7XdjFS"),
        "options": [
            {
                "name": "Done",
                "emoji": Symbol.white_check_mark,
                "execute": {}
            }
        ],
        "go_back": False,
        "hide_options": True
    },
    "welcome_gate": {
        "embed": embed(title="#welcome-gate", color=discord.Color.orange(),
                       description="Click here: https://discord.gg/yhD84nK"),
        "options": [
            {
                "name": "Done",
                "emoji": Symbol.white_check_mark,
                "execute": {}
            }
        ],
        "go_back": False,
        "hide_options": True
    }
}


class welcome:
    """Welcome user with an interactive menu."""
    def __init__(self, bot):
        self.bot = bot
        self.user_history = {}
        self.welcome = dataIO.load_json('data/legend/welcome.json')
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.clans = self.bot.get_cog('crtools').clans
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)

    async def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name.replace(" ", "").replace("-", "").replace(".", ""):
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    async def change_message(self, user, new_embed, reactions: list=None):
        channel = await self.bot.start_private_message(user)

        async for message in self.bot.logs_from(channel, limit=10):
            if message.author.id == self.bot.user.id:
                try:
                    await self.bot.delete_message(message)
                except discord.NotFound:
                    pass

        try:
            new_message = await self.bot.send_message(user, embed=new_embed)
            for reaction in reactions:
                await self.bot.add_reaction(new_message, reaction)
        except discord.Forbidden:
            await self.logger(user)

        return new_message.id

    async def ReactionAddedHandler(self, reaction: discord.Reaction, user: discord.User, history, data):
        menu = dm_menu.get(history[-1])
        if(Symbol.arrow_backward == reaction.emoji):       # if back button then just load previous
            history.pop()
            await self.load_menu(user, history[-1])
            return

        for option in menu.get("options"):      # do the corresponding reaction
            emoji = option.get('emoji')
            if emoji == str(reaction.emoji):
                if "track" in menu:
                    data[history[-1]] = option.get('name')
                if "menu" in option.get('execute'):
                    history.append(option.get('execute').get("menu"))
                    await self.load_menu(user, option.get('execute').get("menu"))
                if "function" in option.get('execute'):       # if it is executable
                    method = getattr(self, option.get('execute').get("function"))
                    await method(user)
                return

    async def load_menu(self, user: discord.User, menu: str):
        menu = dm_menu.get(menu)
        message = ""
        reactions = []

        embed = deepcopy(menu.get("embed"))
        embed.description = embed.description.format(user)

        if "thumbnail" in menu:
            embed.set_thumbnail(url=menu.get("thumbnail"))

        if "image" in menu:
            embed.set_image(url=menu.get("image"))

        if "dynamic_options" in menu:
            method = getattr(self, menu.get("dynamic_options"))
            menu["options"] = await method(user)

        if "options" in menu:
            for option in menu.get("options"):
                emoji = option.get('emoji')
                reactions.append(emoji.replace(">", "").replace("<", ""))
                message += f"{emoji} "
                message += option.get('name')
                message += "\r\n"

        if menu.get("go_back"):
            message += "\r\n"
            message += f":arrow_backward: "
            message += "Go back"
            message += "\r\n"
            reactions.append(Symbol.arrow_backward)

        if "options" in menu:
            if "hide_options" not in menu:
                name = "Options"
                if embed.fields and embed.fields[-1].name == name:
                    embed.set_field_at(len(embed.fields) - 1, name=name, value=message)
                else:
                    embed.add_field(name=name, value=message)

        if "finished" in menu:
            await self.logger(user)

        new_message = await self.change_message(user, embed, reactions=reactions)

        return new_message

    async def _add_roles(self, member, role_names):
        """Add roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        await self.bot.add_roles(member, *roles)

    async def errorer(self, member: discord.User):
        menu_name = "choose_path"
        await self.load_menu(member, menu_name)
        self.user_history[member.id]["history"].append(menu_name)

    async def guest(self, member: discord.Member):
        """Add guest role and change nickname to CR"""
        server = self.bot.get_server("374596069989810176")
        member = server.get_member(member.id)

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            ign = profiledata.name
        except (clashroyale.RequestError, KeyError):
            return await self.errorer(member)

        try:
            newname = ign + " | Guest"
            await self.bot.change_nickname(member, newname)
        except (discord.Forbidden, discord.HTTPException):
            pass

        role = discord.utils.get(member.server.roles, name="Guest")
        try:
            await self.bot.add_roles(member, role)
        except (discord.Forbidden, discord.HTTPException):
            pass

        menu_name = "end_guest"
        await self.load_menu(member, menu_name)
        self.user_history[member.id]["history"].append(menu_name)

    async def verify_membership(self, member: discord.Member):
        server = self.bot.get_server("374596069989810176")
        member = server.get_member(member.id)

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            if profiledata.clan is None:
                clantag = ""
            else:
                clantag = profiledata.clan.tag.strip("#")

            ign = profiledata.name
        except clashroyale.RequestError:
            return await self.errorer(member)

        membership = await self.clans.verifyMembership(clantag)
        if membership:
            try:
                savekey = await self.clans.getClanKey(clantag)
                newclanname = await self.clans.getClanData(savekey, 'nickname')
                newname = ign + " | " + newclanname
                await self.bot.change_nickname(member, newname)
            except (discord.Forbidden, discord.HTTPException):
                pass

            role_names = [await self.clans.getClanData(savekey, 'role'), 'Member']
            try:
                await self._add_roles(member, role_names)
            except (discord.Forbidden, discord.HTTPException):
                pass
        else:
            return await self.errorer(member)

        menu_name = "give_tags"
        await self.load_menu(member, menu_name)
        self.user_history[member.id]["history"].append(menu_name)

        welcomeMsg = rand_choice(self.welcome["GREETING"])
        await self.bot.send_message(discord.Object(id='374596069989810178'), welcomeMsg.format(member))

    async def clans_options(self, user):
        clandata = []
        options = []
        for clankey in self.clans.keysClans():
            try:
                clan = await self.clash.get_clan(await self.clans.getClanData(clankey, 'tag'))
                clandata.append(clan)
            except clashroyale.RequestError:
                return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")

        clandata = sorted(clandata, key=lambda x: (x.required_trophies, x.clan_score), reverse=True)

        index = 0
        for clan in clandata:
            clankey = await self.clans.getClanKey(clan.tag.strip("#"))

            member_count = clan.get("members")
            if member_count < 50:
                showMembers = str(member_count) + "/50"
            else:
                showMembers = "**FULL**"

            title = "[{}] {} ({}+) ".format(showMembers, clan.name, clan.required_trophies)

            options.append({
                "name": title,
                "emoji": Letter.alphabet[index],
                "execute": {
                    "menu": "end_member"
                }
            })

            index += 1

        options.append({
            "name": "I am not sure, I want to talk to a human.",
            "emoji": Letter.alphabet[index],
            "execute": {
                "menu": "end_human"
            }
        })

        return options

    async def logger(self, user):
        """Log into a channel"""
        channel = self.bot.get_channel("374597911436328971")

        embed = discord.Embed(color=discord.Color.green(), description="User Joined")
        avatar = user.avatar_url if user.avatar else user.default_avatar_url
        embed.set_author(name=user.name, icon_url=avatar)

        try:
            data = self.user_history[user.id]["data"]
        except KeyError:
            return await self.bot.send_message(channel, embed=embed)

        if "choose_path" in data:
            path_map = {
                "I am just visiting.": "Guest Joined",
                "I want to join a clan.": "Recruit Joined",
                "I am already in one of your clans.": "Member Joined",
            }
            embed.description = path_map[data["choose_path"]]

        if "name" in data:
            embed.add_field(name="Player:", value="{} {} ({})".format(data["emoji"],
                                                                      data["name"],
                                                                      data["tag"]), inline=False)

        if "clan" in data:
            embed.add_field(name="Current clan:", value=data["clan"], inline=False)

        if "join_clan" in data:
            if data["join_clan"] != "I am not sure, I want to talk to a human.":
                embed.add_field(name="Clan Preference:", value=data["join_clan"], inline=False)

        if "refferal_menu" in data:
            if data["refferal_menu"] != "Other":
                embed.add_field(name="Invited from:", value=data["refferal_menu"], inline=False)

        if "location_menu" in data:
            embed.add_field(name="Region:", value=data["location_menu"], inline=False)

        if "age_menu" in data:
            if data["age_menu"] != "Prefer Not to Answer":
                embed.add_field(name="Age:", value=data["age_menu"], inline=False)

        await self.bot.send_message(channel, embed=embed)

    async def on_member_join(self, member):
        server = member.server
        if server.id != "374596069989810176":
            return

        await self.load_menu(member, "main")

        if member.id in self.user_history:
            del self.user_history[member.id]

        await asyncio.sleep(1200)

        if member.id in self.user_history:
            return

        if member in server.members:
            menu_name = "leave_alone"
            await self.load_menu(member, menu_name)
            self.user_history[member.id]["history"].append(menu_name)

    async def on_member_remove(self, member):
        server = member.server

        embed = discord.Embed(color=discord.Color.red(), description="User Left")
        avatar = member.avatar_url if member.avatar else member.default_avatar_url
        embed.set_author(name=member.display_name, icon_url=avatar)

        await self.bot.send_message(server.get_channel("374597911436328971"), embed=embed)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if reaction.message.channel.is_private and self.bot.user.id != user.id:

            history = {"history": ["main"], "data": {}}

            if user.id in self.user_history:
                history = self.user_history[user.id]
            else:
                self.user_history.update({user.id: history})

            await self.ReactionAddedHandler(reaction, user, history["history"], history["data"])

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def menu(self, ctx):
        user = ctx.message.author
        await self.on_member_join(user)

    @commands.command(pass_context=True)
    async def savetag(self, ctx, profiletag: str):
        """ save your Clash Royale Profile Tag

        Example:
            [p]savetag #CRRYRPCC
        """
        member = ctx.message.author

        profiletag = await self.tags.formatTag(profiletag)

        if not await self.tags.verifyTag(profiletag):
            return await self.bot.say("The ID you provided has invalid characters. Please try again.")

        try:
            profiledata = await self.clash.get_player(profiletag)
            name = profiledata.name

            checkUser = await self.tags.getUser(self.bot.get_all_members(), profiletag)
            if checkUser is not None:
                if checkUser != member:
                    return await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")

            if profiledata.clan is not None:
                self.user_history[member.id]["data"]["clan"] = profiledata.clan.name

            self.user_history[member.id]["data"]["name"] = name
            self.user_history[member.id]["data"]["tag"] = profiledata.tag
            self.user_history[member.id]["data"]["emoji"] = await self.emoji(profiledata.arena.name.replace(' ', '').lower())

            await self.tags.linkTag(profiletag, member.id)

            menu_name = "choose_path"
            await self.load_menu(member, menu_name)
            self.user_history[member.id]["history"].append(menu_name)

        except clashroyale.NotFoundError:
            return await self.bot.say("We cannot find your ID in our database, please try again.")
        except clashroyale.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")


def setup(bot):
    bot.add_cog(welcome(bot))
