# beelbot.py
import discord
import asyncio
from discord.ext import commands

# command prefix
prefix = "$"

# create discord bot
bot = commands.Bot(command_prefix=prefix)

# bot token
token = 'NTA2MTMxOTE4OTc5NDY1MjI3.DrdtjQ.kbUpWr-G7nFSq3bWvfQ2nYWXbtA'

# bot is online
@bot.event
async def on_ready():
	print('beelbot is ready')

# bot ping command
@bot.command()
async def ping(ctx):
	latency = bot.latency
	await ctx.send(latency)

# bot echo test command
@bot.command()
async def echo(ctx, *, content:str):
	await ctx.send(ctx.guild)
	await ctx.send(ctx.author.roles)
	await ctx.send(content)

# role assignment command
@bot.command()
async def KL(ctx, arg):
	user = ctx.author
	roles = ctx.guild.roles
	role_id = None 
	name = user.display_name

	for role in roles:
		if arg in role.name:
			role_id = role

	if role_id == None:
		await ctx.send(f'Role not found.')
		return

	try:
		await user.add_roles(role_id, atomic=True)
		await ctx.send(f'{name} has been assigned {role_id}')
	except (discord.Forbidden, discord.HTTPException) as e:
		await ctx.send(f'{role_id} could not be assigned')

# client.run(token)
bot.run(token)