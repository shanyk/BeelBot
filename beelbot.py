# beelbot.py
import discord

# create discord client
client = discord.Client()

# bot token
token = 'NTA2MTMxOTE4OTc5NDY1MjI3.DrdtjQ.kbUpWr-G7nFSq3bWvfQ2nYWXbtA'

# bot 
@client.event
async def on_ready():
	try:
		print(client.user.name)
		print(client.user.id)
		print(f'Discord.py Version: {discord.__version__}')
	except Exception as e:
		print(e)

@client.event
async def on_message(message):
	await message.content

client.run(token)