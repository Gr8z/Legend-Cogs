import discord
from discord.ext import commands
from random import randint
import requests
from bs4 import BeautifulSoup
import asyncio
import random

server = discord.Server
lastTag = '0'
creditIcon = "https://cdn.discordapp.com/avatars/112356193820758016/7bd5664d82cc7c9d2ae4704e58990da3.jpg"
credits = "Bot by GR8 | Academy"

# Returns a list with tournaments
def getTopTourneyNew():

	global lastTag
	tourney = {}

	try:
		tourneydata = requests.get('http://statsroyale.com/tournaments?appjson=1', timeout=5).json()
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
		    	embed.add_field(name="Top prize", value="<:coin:351316742569721857> " + str(data['gold']) + "     <:tournamentcards:351316762614300672> " +  str(data['cards']), inline=True)
		    	embed.set_footer(text=credits, icon_url=creditIcon)

		    	await self.bot.send_message(discord.Object(id='258729887068585984'), embed=embed) # Family
		    	#await self.bot.send_message(discord.Object(id='363728974821457923'), embed=embed) # testing
		    	#await self.bot.send_message(discord.Object(id='345952929838006283'), embed=embed) # D82

		    	await asyncio.sleep(900)
    		await asyncio.sleep(120)

    @commands.command()
    async def tourney(self):

    	await self.bot.type()

    	try:
    		tourneydata = requests.get('http://statsroyale.com/tournaments?appjson=1', timeout=5).json()
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
    			embed.add_field(name="Top prize", value="<:coin:351316742569721857> " + str(cards) + "     <:tournamentcards:351316762614300672> " +  str(coins), inline=True)
    			embed.set_footer(text=credits, icon_url=creditIcon)
    			await self.bot.say(embed=embed)
    			return

def setup(bot):
	n = tournament(bot)
	loop = asyncio.get_event_loop()
	loop.create_task(n.checkTourney())
	bot.add_cog(n)