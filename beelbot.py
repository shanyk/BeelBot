# beelbot.py
import discord
import asyncio
import asyncpg
from discord.ext import commands

# command prefix
prefix = "$"

# create discord bot
bot = commands.Bot(command_prefix=prefix)


token = None
user = None
pw = None

with open('userpass.txt', 'r') as f:
	user = f.readline().strip()
	pw = f.readline().strip()
	token = f.readline().strip()

# bot is online
@bot.event
async def on_ready():
	print('Beel is online.')

# bot ping command
@bot.command()
async def ping(ctx):
	latency = bot.latency
	await ctx.send(latency)

'''
	gives the user the correct KL tag based on the KL they entered
'''
@bot.command()
async def kl(ctx, arg):

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

'''
	Catch all for all command errors. Sends the error string to the discord.
'''
@bot.event
async def on_command_error(ctx, error):
	await ctx.send(f'{ctx.author.mention} {error}')

'''
	command for users with the 'Admin' role on discord to turn off the discord bot
'''
@bot.command()
async def offline(ctx):	
	if 'Admin' in [role.name for role in ctx.author.roles]:	
		await ctx.send('Going offline...')
		await bot.close()
	else:
		await ctx.send('Nice try')
		return

'''
	update command updates the database with new KL, medals, and mpm
	will throw errors if data entered is less than what it was before
	will also display stat increases
'''
@bot.command()
async def update(ctx, KL, medals, mpm, gd = None):
	
	# await ctx.send(f'{type(ctx.author.id)} {ctx.author.id}')
	# await ctx.send(f'{type(ctx.author.display_name)} {ctx.author.display_name}')
	# await ctx.send(f'{type(medal)} {medal}')
	# await ctx.send(f'{type(mpm)} {mpm}')

	pool = await asyncpg.create_pool(user=user, password=pw, database='beelbot')

	ID = ctx.author.id
	name = ctx.author.display_name

	KL_gain = None
	mpm_gain = None
	medal_gain = None

	member = None

	async with pool.acquire() as con:
		member = await con.fetchrow(f'SELECT kl, medals, mpm, guild FROM profile WHERE id = {ID}')

	if member == None:
		async with pool.acquire() as con:
			await con.execute((f'INSERT INTO profile (id, name, medals, mpm, kl, guild) '
				f'VALUES ({ctx.author.id}, \'{ctx.author.display_name}\', \'{medals}\', \'{mpm}\', \'{KL}\', \'{gd}\')'))
			await profile.invoke(ctx)
			await ctx.send(f'You have been entered into the database!')
		return

	
	old_KL = member['kl'] 
	old_mpm = member['mpm']
	old_medals = member['medals']
	guild = member['guild'] if member['guild'] != None else ''

	medal_gain = calc_dif(old_medals, medals)
	mpm_gain = calc_dif(old_mpm, mpm)
	KL_gain = int(KL) - old_KL

	if medal_gain == None:
		await ctx.send(('Please make sure you entered the correct amount of medals.\n'
			f'You entered: {medals}\n'
			f'Previous record was: {old_medals}\n'
			f'No update will be made because medal gain is negative.'))
		return

	br = '=' * 10
	kl_prev = 'Previous KL: '
	kl_new = 'New KL: '
	kl_gain_str = 'KLs gained: '
	md_prev = 'Previous Medals: '
	md_new = 'New Medals: '
	md_gain_str = 'Medals gained: '
	md_percent = 'Medal gain %: '
	mpm_prev = 'Previous MPM: '
	mpm_new = 'New MPM: '
	mpm_gain_str = 'MPM gain: '
	mpm_percent = 'MPM gain %: '

	update_str = (f'{ctx.author.mention}\n'
		f'```{ctx.author.display_name}   KL {KL}\n'
		f'{guild}\n'
		f'{br}\n'
		f'{kl_prev:<13} {old_KL:>4}\n'
		f'{kl_new:<13} {KL:>4}\n'
		f'{kl_gain_str:<13} {KL_gain:>4}\n'
		f'{br}\n'
		f'{md_prev:<17} {old_medals:>6}\n'
		f'{md_new:<17} {medals:>6}\n'
		f'{md_gain_str:<17} {medal_gain[0]:>6}\n'
		f'{md_percent:<17} {medal_gain[1]:>6}\n'
		f'{br}\n'
		f'{mpm_prev:<14} {old_mpm:>6}\n'
		f'{mpm_new:<14} {mpm:>6}\n'
		f'{mpm_gain_str:<14} {mpm_gain[0]:>6}\n'
		f'{mpm_percent:<14} {mpm_gain[1]:>6}\n```')

	await ctx.send(update_str)

	async with pool.acquire() as con:
		await con.execute((f'UPDATE profile SET mpm = \'{mpm}\', medals = \'{medals}\', kl = {int(KL)}'
			f'WHERE id = {ctx.author.id}'))
		await ctx.send('Profile updated successfully!')

	await pool.close()

	
'''
	first command that any new member of the discord should call in order to set their profile
	for the first time
'''
@bot.command()
async def set(ctx, KL, medals, mpm, guild):

	pool = await asyncpg.create_pool(user=user, password=pw, database='beelbot')

	async with pool.acquire() as con:
		await con.execute((f'INSERT INTO profile (id, name, medals, mpm, kl, guild) '
			f'VALUES ({ctx.author.id}, \'{ctx.author.display_name}\', \'{medals}\', \'{mpm}\', \'{KL}\', \'{guild}\')'))
		await ctx.send(f'{ctx.author.mention} you have been entered into the database!')

	await pool.close()

'''
	profile command lets user see their personal stats or query another user
	name KL
	guild
	total medals
	mpm
'''
@bot.command()
async def profile(ctx, name=None):

	pool = await asyncpg.create_pool(user=user, password=pw, database='beelbot')

	KL = ''
	medals = ''
	mpm = ''
	guild = ''
	dname = ctx.author.display_name if name == None else name

	if name == None:
		async with pool.acquire() as con:
			member = await con.fetchrow((f'SELECT name, kl, medals, mpm, guild FROM profile WHERE id = {ctx.author.id}'))
			KL = member['kl']
			medals = member['medals']
			mpm = member['mpm']
			guild = member['guild']
			dname = member['name']
	else:
		async with pool.acquire() as con:
			member = await con.fetchrow((f'SELECT name, kl, medals, mpm, guild FROM profile WHERE name ILIKE \'%{name}%\''))
			KL = member['kl']
			medals = member['medals']
			mpm = member['mpm']
			guild = member['guild']
			dname = member['name']

	total = 'Total Medals: '
	current = 'Current MPM: '
	br = '=' * 10

	profile_str = (f'{ctx.author.mention}\n'
		f'```{dname}   KL {KL}\n'
		f'{guild}\n'
		f'{br}\n'
		f'{total:<14} {medals:>6}\n'
		f'{current:<14} {mpm:>6}```'
		)

	await ctx.send(profile_str)

	await pool.close()

'''
	calc_dif is used to calculate the difference between old medals and new medals 
	as well as old mpm and new mpm. medals and mpm are passed into the function as string.

	two strings are returned as a number+char representation and a percentage representation
	returns None if the gain is negative because this is indicative of data entry error
'''
def calc_dif(old, new):

	old_num = float(old[:-1])
	old_char = old[-1:].lower()

	new_num = float(new[:-1])
	new_char = new[-1:].lower()

	multiplier = (ord(new_char) - ord(old_char)) * 1000

	gain = new_num - old_num if multiplier == 0 else new_num * multiplier - old_num
	gain_percent = (gain/old_num) * 100

	if gain >= 1000:
		gain_str = f'{gain/1000:.2f}{new_char}'
		gain_percent_str = f'{gain_percent:.2f}%'

		return (gain_str, gain_percent_str)
	elif gain >= 0:
		gain_str = f'{gain:.1f}{old_char}'
		gain_percent_str = f'{gain_percent:.2f}%'

		return (gain_str, gain_percent_str)
	else: 
		return None

bot.run(token)

