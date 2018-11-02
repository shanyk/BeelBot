# beelbot.py
import discord
import asyncio
import asyncpg
from discord.ext import commands

# command prefix
prefix = "$"

# create discord bot
bot = commands.Bot(command_prefix=prefix)

# bot token
token = 'NTA2MTMxOTE4OTc5NDY1MjI3.DrdtjQ.kbUpWr-G7nFSq3bWvfQ2nYWXbtA'

user = None
pw = None

with open('userpass.txt', 'r') as f:
	user = f.readline().strip()
	pw = f.readline().strip()

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
	if 'Admin' in [role.name for role in ctx.author.roles]:	
		await ctx.send('I\'m dying...')
		await bot.close()
	else:
		await ctx.send('Nice try')
		return

# @bot.command()
# async def updatemedals(ctx, arg):
# 	pool = await asyncpg.create_pool(user=user, password=pw, database='beelbot')

# 	missing = False

# 	async with pool.acquire() as conn:

@bot.command()
async def update(ctx, KL, medals, mpm):
	
	# await ctx.send(f'{type(ctx.author.id)} {ctx.author.id}')
	# await ctx.send(f'{type(ctx.author.display_name)} {ctx.author.display_name}')
	# await ctx.send(f'{type(medal)} {medal}')
	# await ctx.send(f'{type(mpm)} {mpm}')

	pool = await asyncpg.create_pool(user=user, password=pw, database='beelbot')

	ID = ctx.author.id
	name = ctx.author.display_name

	old_KL = None
	old_mpm = None
	old_medals = None

	KL_gain = None
	mpm_gain = None
	medal_gain = None

	async with pool.acquire() as con:
		member = await con.fetchrow(f'SELECT kl, medals, mpm FROM profile WHERE id = {ID}')
		old_KL = member['kl'] 
		old_mpm = member['mpm']
		old_medals = member['medals']

	medal_gain = calc_dif(old_medals, medals)
	mpm_gain = calc_dif(old_mpm, mpm)
	KL_gain = int(KL) - old_KL

	await ctx.send((f'{ctx.author.mention} new KL {KL}\n'
		f'```KLs gained: {KL_gain}\n'
		f'medals gain: {medal_gain[0]}, {medal_gain[1]}\n'
		f'mpm gain: {mpm_gain[0]}, {mpm_gain[1]}```'))

	# if medal_gain[0] < 0:
	# 	await ctx.send(('Please make sure you entered the correct amount of medals. '
	# 		f'Your current gain is {medal_gain[0]} and %gain is {medal_gain[1]}'))
	# 	return

@bot.command()
async def set(ctx, KL, medals, mpm):

	pool = await asyncpg.create_pool(user=user, password=pw, database='beelbot')

	async with pool.acquire() as con:
		await ctx.send('connection established')
		await con.execute((f'INSERT INTO profile (id, name, medals, mpm, kl) '
			f'VALUES ({ID}, \'{name}\', \'{medals}\', \'{mpm}\', \'KL\')'))

	await pool.close()


def calc_dif(old, new):

	old_num = float(old[:-1])
	old_char = old[-1:]

	new_num = float(new[:-1])
	new_char = new[-1:]

	multiplier = (ord(new_char) - ord(old_char)) * 1000

	gain = new_num - old_num if multiplier == 0 else new_num * multiplier - old_num
	gain_percent = (gain/old_num) * 100

	if gain >= 1000:
		gain_str = f'{gain/1000:.2f}{new_char}'
		gain_percent_str = f'{gain_percent:.2f}%'

		return (gain_str, gain_percent_str)
	elif gain >= 0:
		gain_str = f'{gain:.2f}{old_char}'
		gain_percent_str = f'{gain_percent:.2f}%'

		return (gain_str, gain_percent_str)
	else: 
		return None

bot.run(token)

