# Developed by Redjumpman for Redbot.
# Inspired by the snail race mini game

# STD Library
import asyncio
import random
import os
import time

# Discord and Red Utils
import discord
from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
from .utils.dataIO import dataIO

creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

animals = ((':rabbit2:', 'fast'), (':monkey:', 'fast'), (':cat2:', 'fast'), (':mouse2:', 'slow'),
           (':chipmunk:', 'fast'), (':rat:', 'fast'), (':dove:', 'fast'), (':bird:', 'fast'),
           (':dromedary_camel:', 'steady'), (':camel:', 'steady'), (':dog2:', 'steady'),
           (':poodle:', 'steady'), (':racehorse:', 'steady'), (':ox:', 'abberant'),
           (':cow2:', 'abberant'), (':elephant:', 'abberant'), (':water_buffalo:', 'abberant'),
           (':ram:', 'abberant'), (':goat:', 'abberant'), (':sheep:', 'abberant'),
           (':leopard:', 'predator'), (':tiger2:', 'predator'), (':dragon:', 'special'),
           (':unicorn:', 'special'), (':turtle:', 'slow'), (':bug:', 'slow'), (':rooster:', 'slow'),
           (':snail:', 'slow'), (':scorpion:', 'slow'), (':crocodile:', 'slow'), (':pig2:', 'slow'),
           (':turkey:', 'slow'), (':duck:', 'slow'), (':baby_chick:', 'slow'))


class PluralDict(dict):
    def __missing__(self, key):
        if '(' in key and key.endswith(')'):
            key, rest = key.split('(', 1)
            value = super().__getitem__(key)
            suffix = rest.rstrip(')').split(',')
            if len(suffix) == 1:
                suffix.insert(0, '')
            return suffix[0] if value <= 1 else suffix[1]
        raise KeyError(key)


class Racer:

    track = '•   ' * 20

    def __init__(self, animal, mode, user):
        self.animal = animal
        self.mode = mode
        self.user = user
        self.turn = 0
        self.position = 80
        self.placed = False
        self.current = Racer.track + self.animal

    def field(self):
        field = "<:elixir:488709583418687539> **{}** :flag_black:  [{}]".format(self.current, self.user.display_name)
        return field

    def get_position(self):
        return self.current.find(self.animal)

    def update_track(self):
        distance = self.move()
        self.current = (Racer.track[:max(0, self.position - distance)] + self.animal +
                        Racer.track[max(0, self.position - distance):])

    def update_position(self):
        self.turn += 1
        self.update_track()
        self.position = self.get_position()

    def move(self):
        if self.mode == 'slow':
            return random.randint(1, 3) * 3

        elif self.mode == 'fast':
            return random.randint(0, 4) * 3

        elif self.mode == 'steady':
            return 2 * 3

        elif self.mode == 'abberant':
            if random.randint(1, 100) >= 90:
                return 5 * 3
            else:
                return random.randint(0, 2) * 3

        elif self.mode == 'predator':
            if self.turn % 2 == 0:
                return 0
            else:
                return random.randint(2, 5) * 3

        elif self.animal == '<:EliteBarbarians:329284880070606861>':
            if self.turn % 3:
                return random.choice([len('blue'), len('red'), len('green')]) * 3
            else:
                return 0
        else:
            if self.turn == 1:
                return 14 * 3
            elif self.turn == 2:
                return 0
            else:
                return random.randint(0, 2) * 3


class Race:
    """Cog for racing animals"""

    def __init__(self, bot):
        self.bot = bot
        self.system = {}
        self.config = dataIO.load_json('data/race/race.json')
        self.version = "1.1.03"
        self.cooldown = {}

    def getCRChars(self):
        """Get a list of CR emojis."""
        return ((self.emoji('Bandit'), 'predator'),
                (self.emoji('MegaKnight'), 'predator'),
                (self.emoji('BattleRam'), 'predator'),
                (self.emoji('IceSpirit'), 'fast'),
                (self.emoji('FireSpirits'), 'fast'),
                (self.emoji('GoblinGiant'), 'abberant'),
                (self.emoji('LavaHound'), 'abberant'),
                (self.emoji('Golem'), 'slow'),
                (self.emoji('Giant'), 'slow'),
                (self.emoji('HogRider'), 'fast'),
                (self.emoji('PEKKA'), 'predator'),
                (self.emoji('Goblins'), 'fast'),
                (self.emoji('SpearGoblins'), 'abberant'),
                (self.emoji('Princess'), 'abberant'),
                (self.emoji('Wizard'), 'fast'),
                (self.emoji('IceWizard'), 'fast'),
                (self.emoji('ElectroWizard'), 'fast'),
                (self.emoji('Sparky'), 'slow'),
                (self.emoji('Miner'), 'abberant'),
                (self.emoji('Valkyrie'), 'fast'),
                (self.emoji('GoblinGang'), 'fast'),
                (self.emoji('RoyalGhost'), 'fast'),
                (self.emoji('MagicArcher'), 'fast'),
                (self.emoji('NightWitch'), 'slow'),
                (self.emoji('InfernoDragon'), 'slow'),
                (self.emoji('BabyDragon'), 'slow'),
                (self.emoji('Lumberjack'), 'fast'),
                (self.emoji('SkeletonArmy'), 'fast'),
                (self.emoji('Skeletons'), 'fast'),
                (self.emoji('Guards'), 'fast'),
                (self.emoji('Hunter'), 'slow'),
                (self.emoji('DarkPrince'), 'predator'),
                (self.emoji('Prince'), 'predator'),
                (self.emoji('Bowler'), 'slow'),
                (self.emoji('Balloon'), 'slow'),
                (self.emoji('Witch'), 'abberant'),
                (self.emoji('CannonCart'), 'abberant'),
                (self.emoji('Executioner'), 'slow'),
                (self.emoji('GiantSkeleton'), 'slow'),
                (self.emoji('IceGolem'), 'slow'),
                (self.emoji('MegaMinion'), 'slow'),
                (self.emoji('DartGoblin'), 'fast'),
                (self.emoji('Musketeer'), 'fast'),
                (self.emoji('Zappies'), 'fast'),
                (self.emoji('FlyingMachine'), 'slow'),
                (self.emoji('MiniPEKKA'), 'abberant'),
                (self.emoji('ThreeMusketeers'), 'fast'),
                (self.emoji('RoyalHogs'), 'fast'),
                (self.emoji('Bats'), 'fast'),
                (self.emoji('SkeletonBarrel'), 'slow'),
                (self.emoji('Bomber'), 'fast'),
                (self.emoji('Minions'), 'fast'),
                (self.emoji('MinionHorde'), 'fast'),
                (self.emoji('Archers'), 'fast'),
                (self.emoji('Knight'), 'slow'),
                (self.emoji('Barbarians'), 'fast'),
                (self.emoji('EliteBarbarians'), 'fast'),
                (self.emoji('RoyalGiant'), 'slow'),
                (self.emoji('Rascals'), 'abberant'),
                (self.emoji('RoyalRecruits'), 'steady'))

    def getBSChars(self):
        """Get a list of BS emojis."""
        return ((self.emoji('Shelly'), 'slow'),
                (self.emoji('Colt'), 'slow'),
                (self.emoji('Nita'), 'slow'),
                (self.emoji('Bo'), 'slow'),
                (self.emoji('Bull'), 'predator'),
                (self.emoji('Jessie'), 'slow'),
                (self.emoji('Brock'), 'slow'),
                (self.emoji('Dynamike'), 'slow'),
                (self.emoji('ElPrimo'), 'abberant'),
                (self.emoji('Barley'), 'slow'),
                (self.emoji('Poco'), 'slow'),
                (self.emoji('Darryl'), 'predator'),
                (self.emoji('Penny'), 'slow'),
                (self.emoji('Ricochet'), 'slow'),
                (self.emoji('Frank'), 'abberant'),
                (self.emoji('Piper'), 'slow'),
                (self.emoji('Pam'), 'slow'),
                (self.emoji('Mortis'), 'fast'),
                (self.emoji('Tara'), 'slow'),
                (self.emoji('Crow'), 'fast'),
                (self.emoji('Spike'), 'slow'),
                (self.emoji('Leon'), 'slow'))

    def emoji(self, name):
        """Emoji by name."""
        for emoji in self.bot.get_all_emojis():
            if emoji.name == name:
                return '<:{}:{}>'.format(emoji.name, emoji.id)
        return ''

    @commands.group(pass_context=True, no_pm=True)
    async def race(self, ctx):
        """Race cog's group command"""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @commands.group(pass_context=True, no_pm=True)
    async def setrace(self, ctx):
        """Race cog's settings group command"""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @setrace.command(name="prize", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _prize_setrace(self, ctx, minimum: int, maximum: int):
        """Set the prize range

        A number of credits will be randomly picked from the set
        miminum to the set maximum.

        Parameters:
            minimum: integer
                Must be lower than maximum
            maximum: integer
                Must be higher than minimum

        Returns:
            Bot replies with invalid mode
            Bot replies with valid mode and saves choice
        """

        if minimum > maximum:
            return await self.bot.say("https://simple.wikipedia.org/wiki/Maximum_and_minimum")
        server = ctx.message.server
        settings = self.check_config(server)
        settings['Prize'] = (minimum, maximum)
        self.save_settings()
        await self.bot.say("Prize range set to {}-{}".format(minimum, maximum))

    @setrace.command(name="cost", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _cost_setrace(self, ctx, num: int):
        """Set the cost to enter the race

        Returns:
            Bot replies with invalid mode
            Bot replies with valid mode and saves choice
        """

        server = ctx.message.server
        settings = self.check_config(server)
        settings['Cost'] = num
        self.save_settings()
        await self.bot.say("Cost set to {} credits.".format(num))

    @setrace.command(name="time", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _time_setrace(self, ctx, time: int):
        """Set the time players have to enter a race

        Amount of time for the bot to wait for entrants until the race
        is ready to begin.

        Parameters:
            time: integer
                Unit is expressed in seconds
                Default is set to 60 seconds

        Returns:
            Bo
        """
        author = ctx.message.author
        if time < 0:
            return await self.bot.say("{}. You are a dumbass. I can't turn back"
                                      "time.".format(author.name))

        settings = self.check_config(author.server)
        settings['Time'] = time
        self.save_settings()
        await self.bot.say("Wait time set to {}s".format(time))

    @setrace.command(name="mode", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _mode_setrace(self, ctx, mode: str):
        """Set the race mode

        Standard Mode assigns everyone a turtle. Everyone has the same
        random movement formula.

        Zoo Mode assigns every entrant a random animal. Animals are grouped into
        classes that meet a special formula for movement. 8 different animal classes!

        Parameters:
            mode: string
                Must be standard or zoo
        Returns:
            Bot replies with invalid mode
            Bot replies with valid mode and saves choice
        """
        server = ctx.message.server
        settings = self.check_config(server)
        mode = mode.lower()
        modes = ['standard', 'zoo', 'clashroyale', 'brawlstars']
        if mode not in modes:
            return await self.bot.say("Invalid mode. Acceptable responses "
                                      "include: {}.".format(', '.join(modes)))
        settings['Mode'] = mode
        self.save_settings()
        await self.bot.say("Mode now set to {}.".format(mode))

    @race.command(name="reset", pass_context=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _reset_race(self, ctx):
        """Reset race parameters DEBUG USE ONLY"""
        server = ctx.message.server
        data = self.check_server(server)
        self.game_teardown(data, force=True)
        await self.bot.say("Parameters reset.")

    @race.command(name="enter", pass_context=True)
    async def _enter_race(self, ctx):
        """Start an animal race and enter yourself as participant

            Returns:
                Two text outputs. One to start the race,
                and the second to represent the race. The second
                msg will be edited multiple times to represent the race.

            Notes:
                Must wait 2 minutes after every race to start a new one.
                You cannot start a race if a race is already active.
                A race is considered active once this command is used.
                A race is considered started once the track is displayed.
                The user who starts a race, will be automatically entered.
                The bot will always join a race.
                There are no cheaters and it isn't rigged.
        """
        author = ctx.message.author
        server = ctx.message.server
        data = self.check_server(author.server)
        cooldown = self.check_cooldown(author.server)
        settings = self.check_config(author.server)
        cost = settings["Cost"]
        timer = 600

        channel = ctx.message.channel
        if channel.name != "race":
            return await self.bot.say("You cannot run this command in this channel. Please run this command at #race")

        if data['Race Active']:
            if author.id in data['Players']:
                return await self.bot.say("You are already in the race!")
            elif not self.bank_check(settings, author):
                return await self.bot.say("You do not meet the cost of entry. You need atleast {} credits.".format(cost))
            elif len(data['Players']) == 10:
                return await self.bot.say("There are no more spots left in the race!")
            else:
                bank = self.bot.get_cog('Economy').bank
                bank.withdraw_credits(author, cost)
                data['Players'][author.id] = {}
                return await self.bot.say("**{}** entered the race!".format(author.display_name))

        if time.time() - cooldown < timer:
            return await self.bot.say("You need to wait {} before starting another race.".format(self.time_format(int(timer - (time.time() - cooldown)))))

        if self.bank_check(settings, author):
            bank = self.bot.get_cog('Economy').bank
            bank.withdraw_credits(author, cost)
        else:
            return await self.bot.say("You do not meet the cost of entry. You need atleast {} credits.".format(cost))

        role_name = "Race"
        raceRole = discord.utils.get(server.roles, name=role_name)
        if raceRole is None:
            await self.bot.create_role(server, name=role_name)
            raceRole = discord.utils.get(server.roles, name=role_name)

        self.game_teardown(data, force=True)
        data['Race Active'] = True
        data['Players'][author.id] = {}
        wait = settings['Time']

        await self.bot.edit_role(server, raceRole, mentionable=True)
        await self.bot.say(":triangular_flag_on_post: {} has started a race! Type ``{}race enter`` "
                           "to join! :triangular_flag_on_post:\n{}The {} will "
                           "begin in {} seconds!".format(author.mention, ctx.prefix, ' ' * 23, raceRole.mention, wait))
        await self.bot.edit_role(server, raceRole, mentionable=False)

        await asyncio.sleep(wait)

        racers = self.game_setup(author, data, settings['Mode'])

        await self.bot.say(":checkered_flag: The race is now in progress :checkered_flag:")

        data['Race Start'] = True

        perm = discord.PermissionOverwrite(send_messages=False, read_messages=False)
        await self.bot.edit_channel_permissions(ctx.message.channel, server.default_role, perm)

        race_msg = await self.bot.say('\u200b'+'\n'+'\n'.join([player.field() for player in racers]))
        await self.run_game(racers, race_msg, data)

        first = ':first_place:  {0.display_name}'.format(*data['First'])
        fv = '{1} {2:.2f}s'.format(*data['First'])
        second = ':second_place: {0.display_name}'.format(*data['Second'])
        sv = '{1} {2:.2f}s'.format(*data['Second'])
        if data['Third']:
            mention = "{} {} {}".format(data['First'][0].mention, data['Second'][0].mention, data['Third'][0].mention)
            third = ':third_place:  {0.display_name}'.format(*data['Third'])
            tv = '{1} {2:.2f}s'.format(*data['Third'])
        else:
            mention = "{} {}".format(data['First'][0].mention, data['Second'][0].mention)
            third = ':third_place:'
            tv = '--'

        perm = discord.PermissionOverwrite(send_messages=None, read_messages=False)
        await self.bot.edit_channel_permissions(ctx.message.channel, server.default_role, perm)

        embed = discord.Embed(colour=0x00CC33)
        embed.add_field(name=first, value=fv)
        embed.add_field(name=second, value=sv)
        embed.add_field(name=third, value=tv)
        embed.add_field(name='-' * 70, value='Type ``!race claim`` to receive prize money. \nType ``!togglerole race`` to get notified on the next race.')
        embed.title = "Race Results"
        embed.set_footer(text=credits, icon_url=creditIcon)
        await self.bot.say(content=mention, embed=embed)

        self.game_teardown(data)

        self.cooldown[server.id] = time.time()

    @race.command(name="claim", pass_context=True)
    async def _claim_race(self, ctx):
        """Claim your prize from the animal race

        Returns:
                One of three outcomes based on result
            :Text output giving random credits from 10-100
            :Text output telling you are not the winner
            :Text output telling you to get a bank account

        Raises:
            cogs.economy.NoAccount Error when bank account not found.

        Notes:
            If you do not have a bank account with economy, the bot will take your money
            and spend it on cheap booze and potatoes.
        """
        author = ctx.message.author
        data = self.check_server(author.server)
        settings = self.check_config(author.server)
        prize_pool = (len(data['Players']) * settings['Cost']) * 2
        prize = prize_pool

        if data['Race Active']:
            return

        if all(v is None for v in [data['First'], data['Second'], data['Third']]):
            return await self.bot.say("There is nothing to collect.")

        if data['First'] is not None:
            if data['First'][0].id == author.id:
                prize = int(prize_pool * 0.5)
                data['First'] = None

        if data['Second'] is not None:
            if data['Second'][0].id == author.id:
                prize = int(prize_pool * 0.20)
                data['Second'] = None

        if data['Third'] is not None:
            if data['Third'][0].id == author.id:
                prize = int(prize_pool * 0.10)
                data['Third'] = None

        if prize == prize_pool:
            return await self.bot.say("Scram kid. You didn't win nothing yet.")

        try:
            bank = self.bot.get_cog('Economy').bank
        except AttributeError:
            return await self.bot.say("Economy is not loaded.")

        try:  # Because people will play games for money without a fucking account smh
            bank.deposit_credits(author, prize)
        except Exception as e:
            print('{} raised {} because they are stupid.'.format(author.name, type(e)))
            await self.bot.say("We wanted to give you a prize, but you didn't have a bank "
                               "account.\nTo teach you a lesson, your winnings are mine this "
                               "time. Now go register!")
        else:
            await self.bot.say("After paying for king's tax, entrance fees, and arena fees, "
                               "you get **{}** credits.".format(prize))

    def bank_check(self, settings, user):
        bank = self.bot.get_cog('Economy').bank
        amount = settings["Cost"]
        if bank.account_exists(user):
            try:
                if bank.can_spend(user, amount):
                    return True
                else:
                    return False
            except:
                return False

    def time_format(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        data = PluralDict({'hour': h, 'minute': m, 'second': s})
        if h > 0:
            fmt = "{hour} hour{hour(s)}"
            if data["minute"] > 0 and data["second"] > 0:
                fmt += ", {minute} minute{minute(s)}, and {second} second{second(s)}"
            if data["second"] > 0 == data["minute"]:
                fmt += ", and {second} second{second(s)}"
            msg = fmt.format_map(data)
        elif h == 0 and m > 0:
            if data["second"] == 0:
                fmt = "{minute} minute{minute(s)}"
            else:
                fmt = "{minute} minute{minute(s)}, and {second} second{second(s)}"
            msg = fmt.format_map(data)
        elif m == 0 and h == 0 and s > 0:
            fmt = "{second} second{second(s)}"
            msg = fmt.format_map(data)
        else:
            msg = "No Cooldown"
        return msg

    def check_server(self, server):
        if server.id in self.system:
            return self.system[server.id]
        else:
            self.system[server.id] = {'Race Start': False, 'Race Active': False, 'Players': {},
                                      'Winner': None, 'First': None, 'Second': None, 'Third': None
                                      }
            return self.system[server.id]

    def check_cooldown(self, server):
        if server.id in self.cooldown:
            return self.cooldown[server.id]
        else:
            self.cooldown[server.id] = 0
            return self.cooldown[server.id]

    def check_config(self, server):
        if server.id in self.config['Servers']:
            return self.config['Servers'][server.id]
        else:
            self.config['Servers'][server.id] = {'Prize': (1, 100), 'Cost': 500, 'Mode': 'standard', 'Time': 60}
            self.save_settings()
            return self.config['Servers'][server.id]

    def game_teardown(self, data, force=False):
        if data['Winner'] == self.bot.user or force:
            data['Winner'] = None
            data['First'] = None
            data['Second'] = None
            data['Third'] = None
            data['Players'].clear()
        data['Race Active'] = False
        data['Race Start'] = False

    def save_settings(self):
        dataIO.save_json('data/race/race.json', self.config)

    def game_setup(self, author, data, mode):

        racers = []

        if mode == 'zoo':
            characters = animals
        elif mode == 'clashroyale':
            characters = self.getCRChars()
        elif mode == 'brawlstars':
            characters = self.getBSChars()
        else:
            characters = ((":turtle:", "slow"), (':rabbit2:', 'fast'))

        if len(data['Players']) == 1:
            bot_set = random.choice(characters)
            racers = [Racer(bot_set[0], bot_set[1], self.bot.user)]

        for user in data['Players']:
            mobj = author.server.get_member(user)
            animal_set = random.choice(characters)
            racers.append(Racer(animal_set[0], animal_set[1], mobj))

        return racers

    async def run_game(self, racers, game, data):
        while True:
            await asyncio.sleep(2.0)
            for player in racers:
                player.update_position()
                position = player.get_position()
                if position == 0:
                    if not data['Winner']:
                        speed = player.turn + random.uniform(0.1, 0.88)
                        data['Winner'] = player.user
                        data['First'] = (player.user, player.animal, speed)
                        player.placed = True
                    elif not data['Second'] and not player.placed:
                        if data['First'][2] > player.turn:
                            speed = player.turn + random.uniform(0.89, 0.99)
                        else:
                            speed = player.turn + random.uniform(0.1, 0.88)
                        data['Second'] = (player.user, player.animal, speed)
                        player.placed = True
                    elif not data['Third'] and not player.placed:
                        if data['Second'][2] > player.turn:
                            speed = player.turn + random.uniform(0.89, 0.99)
                        else:
                            speed = player.turn + random.uniform(0.1, 0.88)
                        data['Third'] = (player.user, player.animal, speed)
                        player.placed = True
            field = [player.field() for player in racers]
            await self.bot.edit_message(game, '\u200b'+'\n'+'\n'.join(field))

            if [player.get_position() for player in racers].count(0) == len(racers):
                break

        prize = random.randint(10, 100)
        data['Prize'] = prize


def check_folders():
    if not os.path.exists('data/race'):
        print("Creating data/race folder...")
        os.makedirs('data/race')


def check_files():
    system = {"Servers": {}}

    f = 'data/race/race.json'
    if not dataIO.is_valid_json(f):
        print('data/race/race.json')
        dataIO.save_json(f, system)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Race(bot))
