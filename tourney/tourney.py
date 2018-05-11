import discord
from discord.ext import commands
from random import randint
import requests
import asyncio
from .utils.dataIO import dataIO, fileIO
import time
import random

lastTag = '0'
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

class tournament:
	"""tournament!"""

	def __init__(self, bot):
		self.bot = bot
		self.auth = dataIO.load_json('cogs/auth.json')

	def getAuth(self):
		return {"auth" : self.auth['token']}

	# Converts maxPlayers to Cards
	def getCards(self, maxPlayers):
		if maxPlayers == 50: return 25
		if maxPlayers == 100: return 100
		if maxPlayers == 200: return 400
		if maxPlayers == 1000: return 2000

	# Converts maxPlayers to Cards
	def getCoins(self, maxPlayers):
		if maxPlayers == 50: return 175
		if maxPlayers == 100: return 700
		if maxPlayers == 200: return 2800
		if maxPlayers == 1000: return 14000

	# Converts seconds to time
	def sec2tme(self, sec):
		m, s = divmod(sec, 60)
		h, m = divmod(m, 60)

		if h is 0:
			if m is 0:
				return "{} seconds".format(s)
			else:
				return "{} minutes, {} secs".format(m,s)
		else:
			return "{} hour, {} mins".format(h,m)

	# Returns a list with tournaments
	async def getTopTourney(self):

		global lastTag
		try:
			openTourney = requests.get('https://api.royaleapi.com/tournaments/open', headers=self.getAuth(), timeout=10).json()
		except:
			return None

		for tourney in openTourney:

			tag = tourney['tag']
			joined = tourney['playerCount']
			maxplayers = tourney['maxCapacity']

			if ((maxplayers > 50) and ((joined + 4) < maxplayers) and (tag != lastTag)):

				try:
					tourneyAPI = requests.get('https://api.royaleapi.com/tournaments/{}'.format(tag), headers=self.getAuth(), timeout=10).json()
					joined = tourneyAPI['playerCount']
					maxplayers = tourneyAPI['maxCapacity']
				except:
					return None

				if ((maxplayers > 50) and ((joined + 4) < maxplayers) and  (tourneyAPI['status'] != "ended") and (tourneyAPI['type'] != "passwordProtected")):
					tourneyAPI['tag'] = tag
					
					return tourneyAPI

		return None

	# Returns a list with tournaments
	async def getRandomTourney(self):

		try:
			openTourney = requests.get('https://api.royaleapi.com/tournaments/open', headers=self.getAuth(), timeout=10).json()
		except:
			return None

		random.shuffle(openTourney)
		for tourney in openTourney:

			tag = tourney['tag']
			joined = tourney['playerCount']
			maxplayers = tourney['maxCapacity']

			if ((joined + 1) < maxplayers):

				try:
					tourneyAPI = requests.get('https://api.royaleapi.com/tournaments/{}'.format(tag), headers=self.getAuth(), timeout=10).json()
					joined = tourneyAPI['playerCount']
					maxplayers = tourneyAPI['maxCapacity']
				except:
					return None

				if ((joined < maxplayers) and  (tourneyAPI['status'] != "ended") and (tourneyAPI['type'] != "passwordProtected")):
					tourneyAPI['tag'] = tag
					
					return tourneyAPI

		return None

	# checks for a tourney every 5 minutes
	async def checkTourney(self):
		while self is self.bot.get_cog("tournament"):
			data = await self.getTopTourney()
			if data is not None:
				maxCapacity = tourneydata['maxCapacity']
				cards = self.getCards(maxCapacity)
				coins = self.getCoins(maxCapacity)

				embed=discord.Embed(title="Click this link to join the Tournament in Clash Royale!", url="https://legendclans.com/tournaments?id={}".format(tourneydata['tag']), color=0xFAA61A)
				embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

				embed.set_author(name=tourneydata['name']+" (#"+tourneydata['tag']+")")

				embed.add_field(name="Players", value=str(tourneydata['playerCount']) + "/" + str(maxCapacity), inline=True)
				embed.add_field(name="Status", value=tourneydata['status'].title(), inline=True)

				if tourneydata['status'] != "inProgress":
					startTime = self.sec2tme((tourneydata['createTime'] + tourneydata['preparationDuration']) - int(time.time()))
					embed.add_field(name="Starts In", value=startTime, inline=True)

				endTime = self.sec2tme((tourneydata['createTime'] + tourneydata['preparationDuration'] + tourneydata['duration']) - int(time.time()))
				embed.add_field(name="Ends In", value=endTime, inline=True)

				embed.add_field(name="Top prize", value="<:tournamentcards:380832770454192140> " + str(cards) + "	 <:coin:380832316932489268> " +  str(coins), inline=True)
				embed.set_footer(text=credits, icon_url=creditIcon)

				await self.bot.send_message(discord.Object(id='374597050530136064'), embed=embed) # Family
				await self.bot.send_message(discord.Object(id='363728974821457923'), embed=embed) # testing
				await asyncio.sleep(900)
			await asyncio.sleep(120)

	@commands.command()
	async def tourney(self):
		""" Get a open tournament"""

		await self.bot.type()

		tourneydata = await self.getRandomTourney()
		
		if tourneydata is not None:
			maxCapacity = tourneydata['maxCapacity']
			cards = self.getCards(maxCapacity)
			coins = self.getCoins(maxCapacity)

			embed=discord.Embed(title="Click this link to join the Tournament in Clash Royale!", url="https://legendclans.com/tournaments?id={}".format(tourneydata['tag']), color=0xFAA61A)
			embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')

			embed.set_author(name=tourneydata['name']+" (#"+tourneydata['tag']+")")

			embed.add_field(name="Players", value=str(tourneydata['playerCount']) + "/" + str(maxCapacity), inline=True)
			embed.add_field(name="Status", value=tourneydata['status'].title(), inline=True)

			if tourneydata['status'] != "inProgress":
				startTime = self.sec2tme((tourneydata['createTime'] + tourneydata['preparationDuration']) - int(time.time()))
				embed.add_field(name="Starts In", value=startTime, inline=True)

			endTime = self.sec2tme((tourneydata['createTime'] + tourneydata['preparationDuration'] + tourneydata['duration']) - int(time.time()))
			embed.add_field(name="Ends In", value=endTime, inline=True)

			embed.add_field(name="Top prize", value="<:tournamentcards:380832770454192140> " + str(cards) + "	 <:coin:380832316932489268> " +  str(coins), inline=True)
			embed.set_footer(text=credits, icon_url=creditIcon)
			await self.bot.say(embed=embed)
		else:
			await self.bot.say("Found nothing, please try again after a few minutes!")
			return

def check_auth():
    c = dataIO.load_json('cogs/auth.json')
    if 'token' not in c:
        c['token'] = ""
    dataIO.save_json('cogs/auth.json', c)

def setup(bot):
	n = tournament(bot)
	check_auth()
	loop = asyncio.get_event_loop()
	loop.create_task(n.checkTourney())
	bot.add_cog(n)