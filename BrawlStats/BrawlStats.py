import discord
from discord.ext import commands
from .utils.dataIO import dataIO, fileIO
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import json
from flask import Flask, request
import requests
import os
import aiohttp
from __main__ import send_cmd_help

BOTCOMMANDER_ROLES =  ["Family Representative", "Clan Manager", "Clan Deputy", "Co-Leader", "Hub Officer", "admin"]
creditIcon = "https://i.imgur.com/TP8GXZb.png"
credits = "Bot by GR8 | Titan"

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

path = os.path.join("data", "BrawlStats", "tags.json")

# Converts seconds to time
def sec2tme(sec):
	m, s = divmod(sec, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)

	if d is 0:
		if h is 0:
			if m is 0:
				return "{} seconds".format(s)
			else:
				return "{} minutes, {} secs".format(m,s)
		else:
			return "{} hours, {} mins".format(h,m)
	else:
		return "{} days, {} hours".format(d,h)	

# Refresh player battles
def refresh(tag, element):
	if element == 'brawl':
		link = 'http://brawlstats.io/players/' + tag + '/refresh'
	if element == 'band':
		link = 'http://brawlstats.io/bands/' + tag + '/refresh'
	return requests.get(link, headers=headers)

# Return player's username, level, clan, clan tag. Brawl Stars
def getBrawlProfile(tag):

	refresh(tag, element='brawl')

	link = "https://brawlstats.io/players/"+tag
	response = requests.get(link, headers=headers).text
	soup = BeautifulSoup(response, 'html.parser')

	stats = {}

	username = soup.find('div', {'class':'player-name'}).get_text()
	stats[u'username'] = username

	avatar = soup.find('div', {'class':'profile-avatar'}).find('img')
	avatar = avatar['src']
	stats[u'avatar'] = avatar

	band = soup.find('div', {'class':'band-info'}).get_text()

	if band == 'No Band':
		stats[u'band'] = None
		stats[u'band_tag'] = '#'
	else:
		band_link = soup.find('div', {'class':'band-info'}).find('a')
		band = soup.find('div', {'class':'band-name mr-2'}).get_text()
		stats[u'band'] = band
		band_tag = band_link['href'][7:].strip()
		stats[u'band_tag'] = band_tag

	level = soup.find('div', {'class':'experience-level'}).get_text()
	stats[u'level'] = level

	experience = soup.find('div', {'class':'progress-text'}).get_text()
	stats[u'experience'] = experience

	trophies = soup.find_all('div', {'class':'trophies'})[0].get_text()
	stats[u'trophies'] = trophies

	highest_trophies = soup.find_all('div', {'class':'trophies'})[1].get_text()
	stats[u'highest_trophies'] = highest_trophies

	victories = soup.find('div', {'class':'victories'}).get_text()
	stats[u'victories'] = victories

	showdown_victories = soup.find('div', {'class':'showdown-victories'}).get_text()
	stats[u'showdown_victories'] = showdown_victories

	brawlers = soup.find_all('div', {'class':'col-12 mt-3'})[1].find('h3').get_text().replace('Brawlers (', '').replace(')','')
	stats[u'brawlers'] = brawlers

	fav = soup.find_all('div', {'class':'brawlers-brawler-slot d-inline-block'})[0].find('div', {'class':'name'}).get_text()
	stats[u'favourite'] = fav

	return stats

# Brawl stars band info
def getBand(tag):

	refresh(tag, element='band')

	link = "https://brawlstats.io/bands/"+tag
	response = requests.get(link, headers=headers).text
	soup = BeautifulSoup(response, 'html.parser')

	stats = {}

	band_profile = soup.find('div', {'class':'band-profile'})

	name = band_profile.find('div', {'class':'name'}).find('h1').get_text()
	badge = band_profile.find('img', {'class':'band-badge'})['src']
	description = band_profile.find('div', {'class':'clan-description'}).get_text()

	stats[u'name'] = name
	stats[u'badge'] = badge
	stats[u'description'] = description

	trophies = soup.find_all('div', {'class':'trophies'})[0].get_text()
	stats[u'trophies'] = trophies

	required_trophies = soup.find_all('div', {'class':'trophies'})[1].get_text()
	stats[u'required_trophies'] = required_trophies

	members = soup.find('div', {'class':'board-header my-3'}).get_text().replace('Band Members (', '').replace(')','').replace('Inactive members are highlighted in red.','')
	stats[u'members'] = members

	return stats

# Get the event data from brawlstats
def getEvents(self):

	link = "https://brawlstats.io/events"
	response = requests.get(link, headers=headers).text
	soup = BeautifulSoup(response, 'html.parser')

	event_list={}

	event_list = soup.find('div', {'id':'eventData'})['data-events']

	return event_list

class BrawlStats:
    """Live statistics for brawl stars"""

    def __init__(self, bot):
    	self.bot = bot
    	self.brawl = dataIO.load_json(path)


    async def updateBrawl(self):
        self.brawl = dataIO.load_json(path)

    @commands.command(pass_context=True)
    async def brawlProfile(self, ctx, member: discord.Member = None):
    	"""View your Brawl Stars Profile Data and Statstics."""

    	await self.updateBrawl()
    	try :
	    	if member is None:
	    		member = ctx.message.author

	    	profiletag = self.brawl[member.id]['tag']
	    	profiledata = getBrawlProfile(profiletag)

	    	embed=discord.Embed(title="", color=0x0080ff)
	    	embed.set_author(name=profiledata['username'] + "(#" + profiletag + ")", url='https://brawlstats.io/players/' + profiletag, icon_url='https://brawlstats.io/images/bs-stats.png')
	    	embed.set_thumbnail(url='https://brawlstats.io' + str(profiledata['avatar']))
	    	embed.add_field(name="Trophies", value=profiledata['trophies'], inline=True)
	    	embed.add_field(name="Highest Trophies", value=profiledata['highest_trophies'], inline=True)
	    	embed.add_field(name="Level", value=profiledata['level'], inline=True)
	    	embed.add_field(name="Experience", value=profiledata['experience'], inline=True)
	    	embed.add_field(name="Band", value=profiledata['band'], inline=True)
	    	embed.add_field(name="Victoies", value=profiledata['victories'], inline=True)
	    	embed.add_field(name="Showdown Victories", value=profiledata['showdown_victories'], inline=True)
	    	embed.add_field(name="Brawlers Unlocked", value=profiledata['brawlers'], inline=True)
	    	embed.add_field(name="Top Brawler", value=profiledata['favourite'], inline=True)
	    	embed.set_footer(text=credits, icon_url=creditIcon)

    		await self.bot.say(embed=embed)

    	except:
    		await self.bot.say("You need to first save your profile using ``!save brawl #GAMETAG``")

    @commands.command(pass_context=True)
    async def band(self, ctx, clantag = None):
    	"""View Brawl Stars Clan statistics and information """
    	await self.updateBrawl()
    	if clantag is None:
    	    try:
    	    	author = ctx.message.author
    	    	
    	    	clantag = self.brawl[author.id]['band_tag']
    	    except :
    	    	await self.bot.say("You need to first save your profile using ``!save brawl #GAMETAG``")
    	    	return

    	clandata = getBand(clantag)

    	embed=discord.Embed(title=clandata['name'] + " (#" + clantag + ")", description=clandata['description'], color=0x0080ff)
    	embed.set_thumbnail(url='https://brawlstats.io'+ str(clandata['badge']))
    	embed.add_field(name="Members", value=clandata['members'], inline=True)
    	embed.add_field(name="Score", value=clandata['trophies'], inline=True)
    	embed.add_field(name="Required Trophies", value=clandata['required_trophies'], inline=True)
    	embed.set_footer(text=credits, icon_url=creditIcon)
    	await self.bot.say(embed=embed)

    @commands.command()
    async def events(self):
    	"""See upcoming Brawl Stars Events"""

    	eventData = json.loads(getEvents(self))

    	try:
    	 	fourthTitle = eventData['now'][3]['mode']['name'] + " at " + eventData['now'][3]['location']
    	except:
    		fourthTitle = "No Event"

    	embed=discord.Embed(title="Brawl Stars Events", description="Here are the current and upcoming events.", color=0x0080ff)
    	embed.add_field(name="1. " + eventData['now'][0]['mode']['name'] + " at " + eventData['now'][0]['location'], value="<:coin:351316742569721857> 52 Coins     :clock10: " + sec2tme(eventData['later'][0]['time']['starts_in']) + "\n\n**NEXT** - " + eventData['later'][0]['mode']['name'] + " at " + eventData['later'][0]['location'], inline=False)
    	embed.add_field(name="2. " + eventData['now'][1]['mode']['name'] + " at " + eventData['now'][1]['location'], value="<:coin:351316742569721857> 32 Coins     :clock10: " + sec2tme(eventData['later'][1]['time']['starts_in']) + "\n\n**NEXT** - " + eventData['later'][1]['mode']['name'] + " at " + eventData['later'][1]['location'], inline=False)
    	embed.add_field(name="3. " + eventData['now'][2]['mode']['name'] + " at " + eventData['now'][2]['location'], value="<:coin:351316742569721857> 12 Coins     :clock10: " + sec2tme(eventData['later'][2]['time']['starts_in']) + "\n\n**NEXT** - " + eventData['later'][2]['mode']['name'] + " at " + eventData['later'][2]['location'], inline=False)
    	embed.add_field(name="4. " + fourthTitle, value="<:coin:351316742569721857> 16 Coins     :clock10: " + sec2tme(eventData['later'][3]['time']['starts_in']) + "\n\n**NEXT** - " + eventData['later'][3]['mode']['name'] + " at " + eventData['later'][3]['location'], inline=False)
    	embed.set_footer(text=credits, icon_url=creditIcon)
    	await self.bot.say(embed=embed)

def setup(bot):
	if soupAvailable:
		bot.add_cog(BrawlStats(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")