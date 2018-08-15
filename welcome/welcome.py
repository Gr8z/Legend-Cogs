import discord
from discord.ext import commands
import clashroyale


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
    x = "❌"
    arrow_backward = "◀"
    arrow_forward = "▶"
    arrow_up_small = "🔼"
    arrow_down_small = "🔽"


dm_menu = {
    "main": {
        "embed": embed(title="Welcome", color=discord.Color.orange(),
                       description="Welcome to the Legend Family Server, {0.mention}! "
                                   "We are one of the oldest and biggest families in "
                                   "Clash Royale with our 700 members and 14 clans! "
                                   "<a:goblinstab:468708996153475072>\n\n"
                                   "We are glad you joined us, may I ask you a few questions?"),
        "thumbnail": "https://cdn.discordapp.com/icons/374596069989810176/8cadece4b0197ce2a77a4c41a490f0fc.jpg",
        "options": [
            {
                "name": "Yes",
                "emoji": Letter.a,
                "execute": {
                    "menu": "refferal_menu"
                }
            },
            {
                "name": "No",
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
                "name": "Royale Recruit Discord",
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
        "go_back": True
    },
    "location_menu": {
        "embed": embed(title="What part of the world do you come from?", color=discord.Color.orange(),
                       description="To better serve you, "
                                   "pick a region you currently live in."),
        "options": [
            {
                "name": "Northern America",
                "emoji": Letter.a,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Central America",
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
                "name": "Middle Africa",
                "emoji": Letter.d,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Southern Africa",
                "emoji": Letter.e,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Western Europe",
                "emoji": Letter.f,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Eastern Europe",
                "emoji": Letter.g,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Middle East",
                "emoji": Letter.h,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Asia",
                "emoji": Letter.i,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "South-east Asia",
                "emoji": Letter.j,
                "execute": {
                    "menu": "age_menu"
                }
            },
            {
                "name": "Australia",
                "emoji": Letter.k,
                "execute": {
                    "menu": "age_menu"
                }
            }
        ],
        "go_back": True
    },
    "age_menu": {
        "embed": embed(title="How old are you?", color=discord.Color.orange(),
                       description="Everyone is welcome! "
                                   "However some clans do require you to be of a"
                                   " certain age group. Please pick one."),
        "options": [
            {
                "name": "Under 18",
                "emoji": Letter.a,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "18-24",
                "emoji": Letter.b,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "25-34",
                "emoji": Letter.c,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "35-44",
                "emoji": Letter.d,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "45-54",
                "emoji": Letter.a,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "55-64",
                "emoji": Letter.e,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "65 or Above",
                "emoji": Letter.d,
                "execute": {
                    "menu": "save_tag_menu"
                }
            },
            {
                "name": "Prefer Not to Answer",
                "emoji": Letter.e,
                "execute": {
                    "menu": "save_tag_menu"
                }
            }
        ],
        "go_back": True
    },
    "save_tag_menu": {
        "embed": embed(title="What is your playertag?", color=discord.Color.orange(),
                       description="Before we let you talk in the server, we need to take a look at your stats. "
                                   "To do that, we need your Clash Royale player tag.\n\n"
                                   "Please type in **!savetag #YOURTAG** to submit your ID."),
        "image": "https://legendclans.com/wp-content/uploads/2017/11/profile_screen3.png",
        "options": [],
        "go_back": True
    },
    "choose_path": {
        "embed": embed(title="Why are you here?", color=discord.Color.orange(),
                       description="Please select your path "
                                   "below to get started."),
        "options": [
            {
                "name": "I want to join a clan.",
                "emoji": Letter.a,
                "execute": {
                    "menu": "join_clan"
                }
            },
            {
                "name": "I am just visiting.",
                "emoji": Letter.b,
                "execute": {
                    "function": "guest",
                    "parameters": ""
                }
            },
            {
                "name": "I am already in one of your clans.",
                "emoji": Letter.c,
                "execute": {
                    "function": "verify_membership",
                    "parameters": ""
                }
            }
        ],
        "go_back": False
    },
    "join_clan": {
        "embed": embed(title="Legend Family Clans", color=discord.Color.orange(),
                       description="Here are all our clans, which clan do you prefer?"),
        "dynamic_options": "clans_options",
        "options": [],
        "go_back": True
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
        "go_back": False
    },
    "end_human": {
        "embed": embed(title="Requesting assistance", color=discord.Color.orange(),
                       description="We have notified our officers about your information."
                                   " Please wait in #welcome-gate "
                                   "channel while someone comes and helps you.\n\n"
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
        "go_back": False
    },
    "end_guest": {
        "embed": embed(title="Guest Rules", color=discord.Color.orange(),
                       description="Welcome to the **Legend Family** Discord server. "
                       "As a guest, you agree to follow the following rules:\n\n"
                       "• Respect others' opinions. If you disagree, please do so "
                       "in a constructive manner.\n• This is an English only server, "
                       "please use any other languages in a private message.\n"
                       "• Do not spam, and avoid ever using @clanname without "
                       "permission from clan managers or deputies.\n"
                       "• No advertisement of any kind, e.g. clans, websites, "
                       "discord invites.\n• Use #bot-spam for bot features, "
                       "e.g. !deck or !payday\n• Respect and do not subvert "
                       "moderators and managers.\n• A good rule is to talk to "
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
        "go_back": False
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
        "go_back": False
    },
    "welcome_gate": {
        "embed": embed(title="#welcome-gate", color=discord.Color.orange(),
                       description="Click here: http://discord.gg/T7XdjFS"),
        "options": [
            {
                "name": "Done",
                "emoji": Symbol.white_check_mark,
                "execute": {}
            }
        ],
        "go_back": False
    },
    "leave_alone": {
        "embed": embed(title="Ok, I leave you alone", color=discord.Color.orange(),
                       description="You can go talk to a human in #welcome-gate. "),
        "options": [
            {
                "name": "Go to #welcome-gate",
                "emoji": Letter.a,
                "execute": {
                    "menu": "welcome_gate"
                }
            }
        ],
        "go_back": False
    },
    "kick_invite": {
        "embed": embed(title="You have been kicked", color=discord.Color.orange(),
                       description="You must complete the entry process to join the server. "
                                   "If you ever want to join again, you can use this "
                                   "invite link: https://discord.gg/yhD84nK"),
        "options": [
            {
                "name": "Done",
                "emoji": Symbol.white_check_mark,
                "execute": {}
            }
        ],
        "go_back": False
    },
    "give_tags": {
        "embed": embed(title="Membership verified", color=discord.Color.orange(),
                       description="We have unlocked all member channels for you, enjoy!"),
        "options": [
            {
                "name": "Done",
                "emoji": Symbol.white_check_mark,
                "execute": {}
            }
        ],
        "go_back": False
    }
}


class welcome:
    """Welcome user with an interactive menu."""
    def __init__(self, bot):
        self.bot = bot
        self.user_history = {}
        self.auth = self.bot.get_cog('crtools').auth
        self.tags = self.bot.get_cog('crtools').tags
        self.clans = self.bot.get_cog('crtools').clans
        self.clash = clashroyale.OfficialAPI(self.auth.getOfficialToken(), is_async=True)

    async def delete_all_messages(self, channel):
        async for message in self.bot.logs_from(channel, limit=10):
            if message.author.id == self.bot.user.id:
                await self.bot.delete_message(message)

    async def change_message(self, channel, user, new_embed, reactions: list=None):
            """
            ctx: Context as bot
            new_content: :str: content for new message to display
            userid: :int: Any users' long ID
            reactions: :list: of Emojis to react with. Defaults to None for no reactions to be used

            Changes a message's content (typically using `find_earliest_message()`) and adding reactions, if any, to the new message.
            Deletes the old message object in order to clear the recipients' previous reactions

            In the event that a user does not have an old message, userid will get the channel
            returns: message
            """
            await self.delete_all_messages(channel)

            new_message = await self.bot.send_message(user, embed=new_embed)
            for reaction in reactions:
                await self.bot.add_reaction(new_message, reaction)

            return new_message.id

    async def ReactionAddedHandler(self, reaction: discord.Reaction, user: discord.User, history):
            """
            ctx: Context as bot
            reaction: :discord.Reaction: object to handle
            user: :discord.User: user that made the reaction
            history: stack of menu's the user has been through
            """
            menu = dm_menu.get(history[-1])
            if(Symbol.arrow_backward == reaction.emoji):       # if back button then just load previous
                history.pop()
                await self.load_menu(reaction.message.channel, user, history[-1])
                return

            for option in menu.get("options"):      # do the corresponding reaction
                emoji = option.get('emoji')
                if emoji == str(reaction.emoji):
                    if "menu" in option.get('execute'):
                        history.append(option.get('execute').get("menu"))
                        await self.load_menu(reaction.message.channel, user, option.get('execute').get("menu"))
                    if "function" in option.get('execute'):       # if it is executable
                        method = getattr(self, option.get('execute').get("function"))
                        await method(user, *option.get('execute').get("parameters"))
                    return

    async def load_menu(self, channel, user: discord.User, menu: str):
            """
                ctx: Context as bot
                user: :discord.User: the user whom the menu should get sent to
                menu: :str: menu name to load, to get as key from dm_menu dictionary

                Calls
            """
            menu = dm_menu.get(menu)
            message = ""
            reactions = []

            embed = menu.get("embed")
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
                name = "Options"
                if embed.fields and embed.fields[-1].name == name:
                    embed.set_field_at(len(embed.fields) - 1, name=name, value=message)
                else:
                    embed.add_field(name=name, value=message)

            new_message = await self.change_message(channel, user, embed, reactions=reactions)

            return new_message

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if reaction.message.channel.is_private and self.bot.user.id != user.id:

            history = {"history": ["main"], "timer": 0}

            if user.id in self.user_history:
                history = self.user_history[user.id]
                history['timer'] = 0
            else:
                self.user_history.update({user.id: history})

            await self.ReactionAddedHandler(reaction, user, history["history"])

    async def _add_roles(self, member, role_names):
        """Add roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.add_roles(member, *roles)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

    async def guest(self, member: discord.Member):
        """Add guest role and change nickname to CR"""
        server = self.bot.get_server("374596069989810176")
        member = server.get_member(member.id)
        channel = await self.bot.start_private_message(member)

        async def errorer():
            await self.load_menu(channel, member, "choose_path")

            history = {"history": ["main", "choose_path"], "timer": 0}
            self.user_history.update({member.id: history})

        try:
            profiletag = await self.tags.getTag(member.id)
            profiledata = await self.clash.get_player(profiletag)
            ign = profiledata.name
        except clashroyale.RequestError:
            return await errorer()
        except KeyError:
            return await errorer()

        try:
            newname = ign + " | Guest"
            await self.bot.change_nickname(member, newname)
        except discord.HTTPException:
            return await errorer()

        role = discord.utils.get(server.roles, name="Guest")
        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            return await errorer()
        except discord.HTTPException:
            return await errorer()

        await self.load_menu(channel, member, "end_guest")

        history = {"history": ["main", "end_guest"], "timer": 0}
        self.user_history.update({member.id: history})

    async def verify_membership(self, user):
        server = self.bot.get_server("374596069989810176")
        channel = await self.bot.start_private_message(user)
        user = server.get_member(user.id)

        async def errorer():
            await self.load_menu(channel, user, "choose_path")

            history = {"history": ["main", "choose_path"], "timer": 0}
            self.user_history.update({user.id: history})

        try:
            profiletag = await self.tags.getTag(user.id)
            profiledata = await self.clash.get_player(profiletag)
            if profiledata.clan is None:
                clantag = ""
            else:
                clantag = profiledata.clan.tag.strip("#")

            ign = profiledata.name
        except clashroyale.RequestError:
            return await errorer()

        membership = await self.clans.verifyMembership(clantag)
        if membership:
            try:
                savekey = await self.clans.getClanKey(clantag)
                newclanname = await self.clans.getClanData(savekey, 'nickname')
                newname = ign + " | " + newclanname
                await self.bot.change_nickname(user, newname)
            except discord.HTTPException:
                return await errorer()

            role_names = [await self.clans.getClanData(savekey, 'role'), 'Member']
            try:
                await self._add_roles(user, role_names)
            except discord.Forbidden:
                return await errorer()
            except discord.HTTPException:
                return await errorer()
        else:
            return await errorer()

        await self.load_menu(channel, user, "give_tags")

        history = {"history": ["main", "give_tags"], "timer": 0}
        self.user_history.update({user.id: history})

    async def kick_user(self, user):
        try:
            await self.bot.kick(user)
        except discord.errors.Forbidden:
            return
        except Exception as e:
            print(e)

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

    @commands.command(pass_context=True)
    async def menu(self, ctx):
        user = ctx.message.author
        channel = ctx.message.channel
        await self.load_menu(channel, user, "main")

        if user.id in self.user_history:
            del self.user_history[user.id]
        return

    @commands.command(pass_context=True)
    async def savetag(self, ctx, profiletag: str):
        """ save your Clash Royale Profile Tag

        Example:
            [p]savetag #CRRYRPCC
        """

        server = self.bot.get_server("374596069989810176")
        member = ctx.message.author
        channel = ctx.message.channel

        profiletag = await self.tags.formatTag(profiletag)

        if not await self.tags.verifyTag(profiletag):
            return await self.bot.say("The ID you provided has invalid characters. Please try again.")

        try:
            profiledata = await self.clash.get_player(profiletag)
            name = profiledata.name

            checkUser = await self.tags.getUser(server.members, profiletag)
            if checkUser is not None:
                if checkUser != member:
                    return await self.bot.say("Error, This Player ID is already linked with **" + checkUser.display_name + "**")

            await self.tags.linkTag(profiletag, member.id)

            await self.load_menu(channel, member, "choose_path")

            history = {"history": ["main", "choose_path"], "timer": 0}
            self.user_history.update({member.id: history})

        except clashroyale.NotFoundError:
            return await self.bot.say("We cannot find your ID in our database, please try again.")
        except clashroyale.RequestError:
            return await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")


def setup(bot):
    bot.add_cog(welcome(bot))
