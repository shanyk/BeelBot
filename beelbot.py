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
	await user.add_roles(arg)
	await ctx.send(arg)

# client.run(token)
bot.run(token)