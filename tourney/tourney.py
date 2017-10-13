import discord
from discord.ext import commands
from random import randint
import requests
from bs4 import BeautifulSoup
import asyncio

server = discord.Server
lastTag = '0'
creditIcon = "https://cdn.discordapp.com/avatars/112356193820758016/7bd5664d82cc7c9d2ae4704e58990da3.jpg"
credits = "Bot by GR8 | Academy"

# Return parsed profile page using BS4
def parseURL():
	link = 'http://statsroyale.com/tournaments/'
	response = requests.get(link).text
	soup = BeautifulSoup(response, 'html.parser')
	return soup

# Returns a list with tournaments
def getRandomTourney():

	tourney_list={}
	soup = parseURL()

	tourney_stats = soup.find_all('div', {'class':'challenges__rowContainer'})[randint(0, 20)]

	tag = tourney_stats.find_all('div', {'class':'challenges__row'})[0].get_text().strip()
	tourney_list['tag'] = tag

	title = tourney_stats.find_all('div', {'class':'challenges__row'})[1].find('span').get_text().strip()
	tourney_list['title'] = title

	players = tourney_stats.find_all('div', {'class':'challenges__row'})[2].get_text().strip()
	tourney_list['players'] = players

	time = tourney_stats.find_all('div', {'class':'challenges__row'})[3].find('div', {'class':'challenges__timeFull'}).get_text().strip()
	tourney_list['time'] = time

	gold = tourney_stats.find_all('div', {'class':'challenges__row'})[4].find('div', {'class':'challenges__goldMetric'}).find('span').get_text().strip()
	tourney_list['gold'] = gold

	cards = tourney_stats.find_all('div', {'class':'challenges__row'})[4].find_all('div', {'class':'challenges__metric'})[1].find('span').get_text().strip()
	tourney_list['cards'] = cards

	return tourney_list

# Returns a list with tournaments
def getTopTourney():

	global lastTag
	tourney_list={}
	soup = parseURL()

	for i in range(5):
	    tourney_stats = soup.find_all('div', {'class':'challenges__rowContainer'})[i]
	    plyr = tourney_stats.find_all('div', {'class':'challenges__row'})[2].get_text().strip()
	    tag = tourney_stats.find_all('div', {'class':'challenges__row'})[0].get_text().strip()

	    if '/50' in plyr:
	    	joined = plyr.replace('/50','')
	    	joined = int(joined)
	    	maxplayers = 50
	    elif '/100' in plyr:
	    	joined = plyr.replace('/100','')
	    	joined = int(joined)
	    	maxplayers = 100
	    elif '/200' in plyr:
	    	joined = plyr.replace('/200','')
	    	joined = int(joined)
	    	maxplayers = 200
	    elif '/1000' in plyr:
	    	joined = plyr.replace('/1000','')
	    	joined = int(joined)
	    	maxplayers = 1000

	    if ((maxplayers > 50) and ((joined + 4) < maxplayers) and (tag != lastTag)):

	    	tourney_list['tag'] = tag
	    	lastTag = tag

	    	title = tourney_stats.find_all('div', {'class':'challenges__row'})[1].find('span').get_text().strip()
	    	tourney_list['title'] = title

	    	players = tourney_stats.find_all('div', {'class':'challenges__row'})[2].get_text().strip()
	    	tourney_list['players'] = players

	    	time = tourney_stats.find_all('div', {'class':'challenges__row'})[3].find('div', {'class':'challenges__timeFull'}).get_text().strip()
	    	tourney_list['time'] = time

	    	gold = tourney_stats.find_all('div', {'class':'challenges__row'})[4].find('div', {'class':'challenges__goldMetric'}).find('span').get_text().strip()
	    	tourney_list['gold'] = gold

	    	cards = tourney_stats.find_all('div', {'class':'challenges__row'})[4].find_all('div', {'class':'challenges__metric'})[1].find('span').get_text().strip()
	    	tourney_list['cards'] = cards
			
	    	return tourney_list

	return None

class tournament:
    """tournament!"""

    def __init__(self, bot):
        self.bot = bot


    # checks for a tourney every 5 minutes
    async def checkTourney(self):
    	while self is self.bot.get_cog("tournament"):
    		data = getTopTourney()
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
		    	#await self.bot.send_message(discord.Object(id='268744102944833536'), embed=embed) # testing
		    	await self.bot.send_message(discord.Object(id='345952929838006283'), embed=embed) # D82

		    	await asyncio.sleep(900)
    		await asyncio.sleep(120)

    @commands.command()
    async def tourney(self):

    	try:
    		data = getRandomTourney()
    	except(IndexError):
    		await self.bot.say("Found nothing, please search again!")
    		return

    	while ((data['players'] == '50/50') or (data['players'] == '100/100') or (data['players'] == '200/200') or (data['players'] == '1000/1000')):
    		data = getRandomTourney()

    	embed=discord.Embed(title="Open Tournament", description="Here is a good one I found. You can search again if this is not what you are looking for.", color=0x00ffff)
    	embed.set_thumbnail(url='https://statsroyale.com/images/tournament.png')
    	embed.add_field(name="Title", value=data['title'], inline=True)
    	embed.add_field(name="Tag", value=data['tag'], inline=True)
    	embed.add_field(name="Players", value=data['players'], inline=True)
    	embed.add_field(name="Ends In", value=data['time'], inline=True)
    	embed.add_field(name="Top prize", value="<:coin:351316742569721857> " + str(data['gold']) + "     <:tournamentcards:351316762614300672> " +  str(data['cards']), inline=True)
    	embed.set_footer(text=credits, icon_url=creditIcon)
    	await self.bot.say(embed=embed)

def setup(bot):
	n = tournament(bot)
	loop = asyncio.get_event_loop()
	loop.create_task(n.checkTourney())
	bot.add_cog(n)