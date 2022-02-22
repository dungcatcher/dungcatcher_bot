import discord
import asyncio
from discord.ext import commands
import json

bot = commands.Bot(command_prefix="dung ")
with open('users.json') as f:
    user_data = json.load(f)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


# @bot.event
# async def on_message(message):
#     global user_data
#
#     if str(message.author.id) not in user_data.keys():
#         user_data[str(message.author.id)] = {'dung': 0}
#         with open('users.json', 'w') as f:
#             json.dump(user_data, f)
#         print(user_data)
#
#         ctx = await bot.get_context(message)
#         await ctx.channel.send("Thank you for volunteering for dungcoin")


@bot.command()
async def amount(ctx):
    if str(ctx.message.author.id) in user_data.keys():
        await ctx.channel.send(f'You have {user_data[str(ctx.message.author.id)]["dung"]} dung')


@bot.command()
async def catch(ctx, amt):
    if str(ctx.message.author.id) in user_data.keys():
        if amt.isnumeric():
            if len(amt) < 50:
                amt = int(amt)
                if ctx.message.author.id != 446936397786513408:
                    user_data[str(ctx.message.author.id)]["dung"] += amt
                else:
                    user_data[str(ctx.message.author.id)]["dung"] -= amt
                await ctx.channel.send(f'You now have {user_data[str(ctx.message.author.id)]["dung"]}')
                with open('users.json', 'w') as f:
                    json.dump(user_data, f)
            else:
                await ctx.channel.send('aiya catching too much dung please slow down')
        else:
            await ctx.channel.send('aiya put in number so stupid failure')
    else:
        await ctx.channel.send('grr signup for dungcoin')


@bot.command()
async def gamble(ctx):
    if str(ctx.message.author.id) in user_data.keys():
        if user_data[str(ctx.message.author.id)]["dung"] > 0:
            await ctx.channel.send('Pick a side, heads or tails...')
            await asyncio.sleep(1)
            await ctx.channel.send('You HAVE picked heads')
            await ctx.channel.send('It was tails you are so stupid how did you get this wrong I will take all of ur dung L')
            user_data[str(ctx.message.author.id)]["dung"] = 0
            await ctx.channel.send('L you have 0 dung')


TOKEN = 'NzExNzIxNzk5NjE1Nzc0NzIw.XsHIlA.wN-iOVgnOywMlk8_RTkro5rYXtQ'
bot.run(TOKEN)
