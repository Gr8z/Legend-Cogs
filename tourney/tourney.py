import discord
from discord.ext import commands
from random import randint
import requests
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import asyncio
import random
import json
from cogs.utils import checks
from .utils.dataIO import dataIO
import os
from fake_useragent import UserAgent

lastTag = '0'
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

# Returns a list with tournaments
def getTopTourneyNew():

	global lastTag
	tourney = {}

	ua = UserAgent()
	headers = {
	    "User-Agent": ua.random
	}

	try:
		tourneydata = requests.get('http://statsroyale.com/tournaments?appjson=1', timeout=5, headers=headers, proxies=dict(http="69.39.224.129:80",)).json()
	except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
		return None
	except requests.exceptions.RequestException as e:
		return None

	numTourney = len(tourneydata['tournaments'])

	for x in range(0, numTourney):

		title = tourneydata['tournaments'][x]['title']
		totalPlayers = tourneydata['tournaments'][x]['totalPlayers']
		maxPlayers = tourneydata['tournaments'][x]['maxPlayers']
		full = tourneydata['tournaments'][x]['full']
		timeLeft = tourneydata['tournaments'][x]['timeLeft']
		hashtag = tourneydata['tournaments'][x]['hashtag']
		cards = getCards(maxPlayers)
		coins = getCoins(maxPlayers)
		time = sec2tme(timeLeft)
		players = str(totalPlayers) + "/" + str(maxPlayers)

		if (maxPlayers > 50) and (not full) and (timeLeft > 600) and ((totalPlayers + 4) < maxPlayers) and (hashtag != lastTag):
			
			lastTag = hashtag
			
			tourney['tag'] = hashtag
			tourney['title'] = title
			tourney['players'] = players
			tourney['time'] = time
			tourney['gold'] = coins
			tourney['cards'] = cards

			return tourney

	return None

# Converts maxPlayers to Cards
def getCards(maxPlayers):
	if maxPlayers == 50: return 25
	if maxPlayers == 100: return 100
	if maxPlayers == 200: return 400
	if maxPlayers == 1000: return 2000

# Converts maxPlayers to Cards
def getCoins(maxPlayers):
	if maxPlayers == 50: return 175
	if maxPlayers == 100: return 700
	if maxPlayers == 200: return 2800
	if maxPlayers == 1000: return 14000

# Converts seconds to time
def sec2tme(sec):
	m, s = divmod(sec, 60)
	h, m = divmod(m, 60)

	if h is 0:
		if m is 0:
			return "{} seconds".format(s)
		else:
			return "{} minutes, {} secs".format(m,s)
	else:
		return "{} hour, {} mins".format(h,m)

class tournament:
	"""tournament!"""

	def __init__(self, bot):
		self.bot = bot
		self.path = 'data/tourney/settings.json'
		self.settings = dataIO.load_json(self.path)
		
	def save_data(self):
		"""Saves the json"""
		dataIO.save_json(self.path, self.settings)
	

	# checks for a tourney every 5 minutes
	async def checkTourney(self):
		while self is self.bot.get_cog("tournament"):
			data = getTopTourneyNew()
			if data is not None:
				embed=discord.Embed(title="New Tournament", description="We found an open tournament. You can type !tourney to search for more.", color=0x00ffff)
				embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')
				embed.add_field(name="Title", value=data['title'], inline=True)
				embed.add_field(name="Tag", value=data['tag'], inline=True)
				embed.add_field(name="Players", value=data['players'], inline=True)
				embed.add_field(name="Ends In", value=data['time'], inline=True)
				embed.add_field(name="Top prize", value="<:coin:380832316932489268> " + str(data['gold']) + "     <:tournamentcards:380832770454192140> " +  str(data['cards']), inline=True)
				embed.set_footer(text=credits, icon_url=creditIcon)
				
				for serverid in self.settings.keys():
					if self.settings[serverid]:
						await self.bot.send_message(discord.Object(id=self.settings[serverid]), embed=embed) # Family
				#await self.bot.send_message(discord.Object(id='363728974821457923'), embed=embed) # testing

				await asyncio.sleep(900)
			await asyncio.sleep(120)

	@commands.group()
	async def tourney(self):

		await self.bot.type()

		ua = UserAgent()
		headers = {
		    "User-Agent": ua.random
		}

		try:
			tourneydata = requests.get('http://statsroyale.com/tournaments?appjson=1', timeout=5, headers=headers, proxies=dict(http="69.39.224.129:80",)).json()
		except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
			await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
			return
		except requests.exceptions.RequestException as e:
			await self.bot.say(e)
			return

		numTourney = list(range(len(tourneydata['tournaments'])))
		random.shuffle(numTourney)

		for x in numTourney:

			title = tourneydata['tournaments'][x]['title']
			length = tourneydata['tournaments'][x]['length']
			totalPlayers = tourneydata['tournaments'][x]['totalPlayers']
			maxPlayers = tourneydata['tournaments'][x]['maxPlayers']
			full = tourneydata['tournaments'][x]['full']
			timeLeft = tourneydata['tournaments'][x]['timeLeft']
			startTime = tourneydata['tournaments'][x]['startTime']
			warmup = tourneydata['tournaments'][x]['warmup']
			hashtag = tourneydata['tournaments'][x]['hashtag']
			cards = getCards(maxPlayers)
			coins = getCoins(maxPlayers)

			if not full and timeLeft > 600:
				embed=discord.Embed(title="Open Tournament", description="Here is a good one I found. You can search again if this is not what you are looking for.", color=0x00ffff)
				embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')
				embed.add_field(name="Title", value=title, inline=True)
				embed.add_field(name="Tag", value="#"+hashtag, inline=True)
				embed.add_field(name="Players", value=str(totalPlayers) + "/" + str(maxPlayers), inline=True)
				embed.add_field(name="Ends In", value=sec2tme(timeLeft), inline=True)
				embed.add_field(name="Top prize", value="<:coin:380832316932489268> " + str(cards) + "     <:tournamentcards:380832770454192140> " +  str(coins), inline=True)
				embed.set_footer(text=credits, icon_url=creditIcon)
				await self.bot.say(embed=embed)
				return

	@tourney.command(pass_context=True, no_pm=True)
	@checks.admin_or_permissions(administrator=True)
	async def channel(self, ctx, channel: discord.Channel=None):
		serverid = ctx.message.server.id
		if not channel:
			self.settings[serverid] = None
			await self.bot.say("Tournament channel for this server cleared")
		else:
			self.settings[serverid] = channel.id
			await self.bot.say("Tournament channel for this server set to "+channel.mention)
		self.save_data()

def check_folders():
	if not os.path.exists("data/tourney"):
		print("Creating data/tourney folder...")
		os.makedirs("data/tourney")

def check_files():
	f = "data/tourney/settings.json"
	if not dataIO.is_valid_json(f):
		dataIO.save_json(f, {})

def setup(bot):
	check_folders()
	check_files()
	if not soupAvailable:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
	n = tournament(bot)
	loop = asyncio.get_event_loop()
	loop.create_task(n.checkTourney())
	bot.add_cog(n)