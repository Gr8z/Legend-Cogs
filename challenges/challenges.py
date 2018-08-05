# Game made by GR8 from Legend Family.

import discord
from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO
from collections import Counter, namedtuple
from .utils.chat_formatting import box
from __main__ import send_cmd_help
import os
from copy import deepcopy
import asyncio
import random
import operator
import chardet
import time
import math

default_settings = {"CHANNEL": "381338442543398912", "CREDITS": 50,
                    "ROLE": None, "LOCK": False, "QUESTIONS": 60, "DELAY": 60}
settings_path = "data/challenges/settings.json"
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

TriviaLine = namedtuple("TriviaLine", "question answers")


class challenges:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(settings_path)
        self.active = False

    def add_defualt_settings(self, server):
        if server.id not in self.settings:
            self.settings[server.id] = deepcopy(default_settings)
            dataIO.save_json(settings_path, self.settings)

    def get_game_channel(self, server):
        try:
            return server.get_channel(self.settings[server.id]["CHANNEL"])
        except:
            return None

    def verify_role(self, server, role_name):
        """Verify the role exist on the server"""
        role = discord.utils.get(server.roles, name=role_name)
        return role is not None

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def chalset(self, ctx):
        """Sets Challenges settings"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @chalset.command(pass_context=True)
    async def channel(self, ctx, channel: discord.Channel):
        """Sets the channel to play challenges.

        If channel isn't specified, the server's default channel will be used"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        if channel is None:
            channel = ctx.message.server.default_channel
        if not server.get_member(self.bot.user.id
                                 ).permissions_in(channel).send_messages:
            await self.bot.say("I do not have permissions to send "
                               "messages to {0.mention}".format(channel))
            return
        self.settings[server.id]["CHANNEL"] = channel.id
        dataIO.save_json(settings_path, self.settings)
        channel = self.get_game_channel(server)
        await self.bot.send_message(channel, "I will now use {0.mention} to start challenges".format(channel))

    @chalset.command(pass_context=True)
    async def credits(self, ctx, num):
        """Set credits you get per correct answer."""
        server = ctx.message.server
        self.add_defualt_settings(server)

        self.settings[server.id]["CREDITS"] = int(num)
        await self.bot.say("Credits per answer has been set to {}.".format(num))
        dataIO.save_json(settings_path, self.settings)

    @chalset.command(pass_context=True)
    async def role(self, ctx, role):
        """Set role you would like to mention when a challenge starts"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        if not self.verify_role(server, role):
            await self.bot.say("{} is not a valid role on this server.".format(role))
            return

        self.settings[server.id]["ROLE"] = role
        await self.bot.say("Mentionable role has been set to {}.".format(role))
        dataIO.save_json(settings_path, self.settings)

    @chalset.command(pass_context=True)
    async def channellock(self, ctx):
        """Lock channel when challenge starts"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        self.settings[server.id]["LOCK"] = not self.settings[server.id]["LOCK"]
        await self.bot.say("Challenge lock set to {}.".format(str(self.settings[server.id]["LOCK"])))
        dataIO.save_json(settings_path, self.settings)

    @chalset.command(pass_context=True)
    async def questions(self, ctx, num):
        """Set number of questions per challenge"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        self.settings[server.id]["QUESTIONS"] = int(num)
        await self.bot.say("questions per challenge has been set to {}.".format(num))
        dataIO.save_json(settings_path, self.settings)

    @chalset.command(pass_context=True)
    async def delay(self, ctx, num):
        """Set delay in second to start the challenge"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        self.settings[server.id]["DELAY"] = int(num)
        await self.bot.say("challenge delay has been set to {}.".format(num))
        dataIO.save_json(settings_path, self.settings)

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def chal(self, ctx):
        """Challenge Controls"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @chal.command(pass_context=True)
    async def start(self, ctx):
        """Start the challenge on the specified channel"""
        server = ctx.message.server
        self.add_defualt_settings(server)

        channel = self.get_game_channel(server)
        role_name = self.settings[server.id]["ROLE"]
        lock_state = self.settings[server.id]["LOCK"]
        delay = self.settings[server.id]["DELAY"]

        if self.active:
            await self.bot.say("A challenge is already running, wait for it to end first.")
            return

        if channel is None:
            await self.bot.say("Challenge channel not set, use ``[p]chalset channel`` to set your channel.")
            return

        if role_name is not None:
            challenges_role = discord.utils.get(server.roles, name=role_name)
            if challenges_role is None:
                await self.bot.create_role(server, name=role_name)
                challenges_role = discord.utils.get(server.roles, name=role_name)

            await self.bot.edit_role(server, challenges_role, mentionable=True)
            await self.bot.send_message(channel, (":rotating_light: New challenge starting in "
                                                  "{} seconds :rotating_light: {}".format(str(delay),
                                                                                          challenges_role.mention)))
            await self.bot.edit_role(server, challenges_role, mentionable=False)
        else:
            await self.bot.send_message(channel, (":rotating_light: New challenge starting in "
                                                  "{} seconds :rotating_light:".format(str(delay))))

        if lock_state:
            perm = discord.PermissionOverwrite(send_messages=False, read_messages=False)
            await self.bot.edit_channel_permissions(channel, server.default_role, perm)

        self.active = True

        await asyncio.sleep(delay)

        if lock_state:
            perm = discord.PermissionOverwrite(send_messages=None, read_messages=False)
            await self.bot.edit_channel_permissions(channel, server.default_role, perm)

        c = challengeSession(self.bot)
        await c.start_game(server)

        self.active = False

    @chal.command(pass_context=True)
    async def stop(self, ctx):
        """Stop the challenge on the specified channel"""
        await self.bot.say("Challenge stopped.")
        self.active = False


class challengeSession():
    def __init__(self, bot):
        self.bot = bot
        self.games = 0
        self.timeout = 0
        self.settings = dataIO.load_json(settings_path)
        self.emoji = dataIO.load_json("data/challenges/emoji.json")
        self.words = dataIO.load_json("data/challenges/words.json")
        self.bank = self.bot.get_cog('Economy').bank
        self.scores = Counter()
        self.statusNum = ""
        self.gameList = [self.emoji_reacter, self.word_scramble, self.trivia,
                         self.maths, self.guess, self.stop]
        self.trivia_list = ['artandliterature', 'clashroyale', 'computers',
                            'elements', 'games', 'general', 'worldcapitals',
                            'entertainment', 'riddles']

    def get_game_channel(self, server):
        try:
            return server.get_channel(self.settings[server.id]["CHANNEL"])
        except:
            return None

    def RepresentsInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def parse_trivia_list(self, filename):
        path = "data/trivia/{}.txt".format(filename)
        parsed_list = []

        with open(path, "rb") as f:
            try:
                encoding = chardet.detect(f.read())["encoding"]
            except:
                encoding = "ISO-8859-1"

        with open(path, "r", encoding=encoding) as f:
            trivia_list = f.readlines()

        for line in trivia_list:
            if "`" not in line:
                continue
            line = line.replace("\n", "")
            line = line.split("`")
            question = line[0]
            answers = []
            for l in line[1:]:
                answers.append(l.strip())
            if len(line) >= 2 and question and answers:
                line = TriviaLine(question=question, answers=answers)
                parsed_list.append(line)

        if not parsed_list:
            raise ValueError("Empty trivia list")

        return parsed_list

    async def send_table(self):
        t = "+ Results: \n\n"
        for user, score in self.scores.most_common():
            t += "+ {}\t{}\n".format(user.display_name, score)
        await self.bot.say(box(t, lang="diff"))

    async def correct_answer(self, server, answer):
        try:
            self.bank.deposit_credits(answer.author, self.settings[server.id]["CREDITS"])
            await self.bot.say("You got it {} (+{} credits)".format(answer.author.mention,
                                                                    self.settings[server.id]["CREDITS"]))
        except:
            await self.bot.say("You got it {} (please do ``!bank register``)".format(answer.author.mention))

        self.scores[answer.author] += 1
        self.timeout = 0

    async def start_game(self, server):
        q_num = self.settings[server.id]["QUESTIONS"]

        if self is self.bot.get_cog("challenges"):
            return

        if self.timeout > 10:
            await asyncio.sleep(5)
            self.timeout = 0
            if self.scores:
                await self.send_table()
            await self.bot.say("No one is playing, challenge ended. "
                               "Type ``!togglerole challenges`` to get notified on the next challenge.")
        elif self.games < q_num:
            await asyncio.sleep(3)
            await random.choice(self.gameList)(server)
        else:
            if self.scores:
                await self.send_table()
            await self.bot.say("Thats it, challenge ended. "
                               "Type ``!togglerole challenges`` to get notified on the next challenge.")

    async def emoji_reacter(self, server):
        channel = self.get_game_channel(server)
        emoji = random.choice(self.emoji)

        embed = discord.Embed(title=emoji['emoji'], description=emoji['description'], color=0x008000)
        embed.set_author(name="React with Emoji")
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.send_message(channel, embed=embed)

        while True:
            react = await self.bot.wait_for_reaction(emoji=emoji['emoji'], timeout=15)

            if react is None:
                self.timeout += 1
                break

            if react.user != self.bot.user:
                if react.reaction.emoji == emoji['emoji']:
                    try:
                        self.bank.deposit_credits(react.user, self.settings[server.id]["CREDITS"])
                        await self.bot.say("You got it {} (+{} credits)".format(react.user.mention,
                                                                                self.settings[server.id]["CREDITS"]))
                    except:
                        await self.bot.say("You got it {} (please do ``!bank register``)".format(react.user.mention))
                    self.scores[react.user] += 1
                    self.timeout = 0
                    break

        self.games += 1
        await self.start_game(server)

    async def word_scramble(self, server):
        channel = self.get_game_channel(server)

        def scramble(wordie):
            foo = list(wordie)
            scambled = wordie
            while wordie == scambled:
                random.shuffle(foo)
                scambled = ''.join(foo)
            return scambled

        word = random.choice(self.words)
        self.words.remove(word)

        embed = discord.Embed(title="", description=scramble(word).upper(), color=0x8000ff)
        embed.set_author(name="Unscramble the word")
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.send_message(channel, embed=embed)
        print("Answer: {}".format(word))

        def check(msg):
            return word in msg.content.lower()

        while True:
            answer = await self.bot.wait_for_message(check=check, timeout=15)

            if answer is None:
                await self.bot.say("Time's up, it was **{}**".format(word))
                self.timeout += 1
                break

            if answer.author != self.bot.user:
                await self.correct_answer(server, answer)
                break

        self.games += 1
        await self.start_game(server)

    async def trivia(self, server):
        channel = self.get_game_channel(server)

        trivia_list = random.choice(self.trivia_list)
        question_list = self.parse_trivia_list(trivia_list)
        current_line = random.choice(question_list)
        question_list.remove(current_line)

        embed = discord.Embed(title="", description=current_line.question, color=0xff8000)
        embed.set_author(name="Answer the question")
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.send_message(channel, embed=embed)
        print("Answer: {}".format(str(current_line.answers[0])))

        def check(msg):
            for answer in current_line.answers:
                answer = answer.lower()
                guess = msg.content.lower()
                if " " not in answer:
                    guess = guess.split(" ")
                    for word in guess:
                        if word == answer:
                            return True
                else:
                    if answer in guess:
                        return True
            return False

        while True:
            guess = await self.bot.wait_for_message(check=check, timeout=15)

            if guess is None:
                await self.bot.say("Time's up, it was **{}**".format(current_line.answers[0]))
                self.timeout += 1
                break

            if guess.author != self.bot.user:
                await self.correct_answer(server, guess)
                break

        self.games += 1
        await self.start_game(server)

    async def maths(self, server):
        channel = self.get_game_channel(server)

        ops = {'+': operator.add,
               '-': operator.sub,
               '*': operator.mul}
        num1 = random.randint(0, 120)
        num2 = random.randint(1, 100)
        op = random.choice(list(ops.keys()))
        number = ops.get(op)(num1, num2)

        embed = discord.Embed(title="", description='What is {} {} {}?\n'.format(num1, op, num2), color=0xff8080)
        embed.set_author(name="Calculate")
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.send_message(channel, embed=embed)
        print("Answer: {}".format(str(number)))

        while True:
            answer = await self.bot.wait_for_message(content=str(number), timeout=15)

            if answer is None:
                await self.bot.say("Time's up, the correct answer is **{}**".format(str(number)))
                self.timeout += 1
                break

            if answer.author != self.bot.user:
                await self.correct_answer(server, answer)
                break

        self.games += 1
        await self.start_game(server)

    async def guess(self, server):
        channel = self.get_game_channel(server)

        startNum = random.randint(10, 100)
        endNum = random.randint(startNum + 25, startNum + 100)
        number = random.randint(startNum, endNum)

        embed = discord.Embed(title="", description='A number between {} - {}'.format(startNum, endNum), color=0x0080ff)
        embed.set_author(name="Guess the number")
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.send_message(channel, embed=embed)
        print("Answer: {}".format(str(number)))

        start = time.time()

        while True:

            if (time.time() - start > 20):
                await self.bot.say("Time's up, the correct answer is **{}**".format(str(number)))
                self.timeout += 1
                break

            answer = await self.bot.wait_for_message(timeout=5)

            if answer is not None:
                if self.RepresentsInt(answer.content):
                    msgNum = int(answer.content)
                    if number == msgNum:
                        if answer.author != self.bot.user:
                            await self.correct_answer(server, answer)
                            break
                    elif number > msgNum:
                        await self.bot.add_reaction(answer, "🔽")
                    else:
                        await self.bot.add_reaction(answer, "🔼")

        self.games += 1
        await self.start_game(server)

    async def stop(self, server):
        channel = self.get_game_channel(server)

        timer = random.randint(3, 15)
        niceTry = []

        embed = discord.Embed(title="", description='Type \'stop\' only once in {} seconds.'.format(timer), color=0x804000)
        embed.set_author(name="Stop Watch")
        embed.set_footer(text=credits, icon_url=creditIcon)

        await self.bot.send_message(channel, embed=embed)
        start = time.time()

        def check(msg):
            if (math.ceil(time.time() - start) == timer) and (msg.content.lower() == "stop"):
                return True
            else:
                niceTry.append(msg.author.id)
                return False

        while True:
            if (time.time() - start > timer+3):
                await self.bot.say("Time's up, you missed it.")
                self.timeout += 1
                break

            answer = await self.bot.wait_for_message(check=check, timeout=5)

            if answer is not None:
                if answer.author.id not in niceTry:
                    if answer.author != self.bot.user:
                        await self.correct_answer(server, answer)
                        break

        self.games += 1
        await self.start_game(server)


def check_folders():
    if not os.path.exists("data/challenges"):
        print("Creating data/challenges folder...")
        os.makedirs("data/challenges")


def check_files():
    f = settings_path
    if not dataIO.is_valid_json(f):
        print("Creating challenges settings.json...")
        dataIO.save_json(f, {})
    else:  # consistency check
        current = dataIO.load_json(f)
        for k, v in current.items():
            if v.keys() != default_settings.keys():
                for key in default_settings.keys():
                    if key not in v.keys():
                        current[k][key] = deepcopy(default_settings)[key]
                        print("Adding " + str(key) +
                              " field to challenges settings.json")


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(challenges(bot))
