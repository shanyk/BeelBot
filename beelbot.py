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

roles = None

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

	KL = None

	try:
		KL = int(arg)
	except ValueError as e:
		await ctx.send('Please enter an integer for your KL. ex. $KL 100')
		return

	rounded_KL = KL if KL % 25 == 0 else KL - 25 + (25 - KL % 25)

	user = ctx.author
	roles = [role for role in ctx.guild.roles if role.name.startswith('KL')]
	role_id = None 
	name = user.display_name

	role_dict = {int(role.name[3:6]):role for role in roles}

	role_id = role_dict[rounded_KL]

	if role_id == None:
		await ctx.send(f'Role not found.')
		return

	try:
		await user.add_roles(role_id, atomic=True)
		await ctx.send(f'{ctx.author.mention} has been assigned {role_id}')
	except (discord.Forbidden, discord.HTTPException) as e:
		await ctx.send(f'{ctx.author.mention} {role_id} could not be assigned')

@bot.event
async def on_command_error(ctx, error):
	await ctx.send(f'{ctx.author.mention} {error}')

@bot.command()
async def offline(ctx):
	await ctx.send('I\'m dying...')
	await bot.close()

# client.run(token)
bot.run(token)