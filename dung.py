from discord.ext import commands
import json
import random


def user_exists(user_id, user_data):
    return str(user_id) in user_data.keys()


def update_json(user_data):
    with open('users.json', 'w') as f:
        json.dump(user_data, f)


class Dung(commands.Cog):
    def __init__(self, bot, user_data):
        self.bot = bot
        self.user_data = user_data

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

    @commands.command()
    async def signup(self, ctx):
        user_id = ctx.message.author.id
        if user_exists(user_id, self.user_data):
            await ctx.send("You have already signed up!")
        else:
            self.user_data[str(user_id)] = {"dung": 0}
            update_json(self.user_data)

    @commands.command()
    async def catch(self, ctx):
        user_id = ctx.message.author.id
        if user_exists(user_id, self.user_data):
            dung_amt = random.randint(1, 10)

            target_user_data = self.user_data[str(user_id)]
            target_user_data["dung"] += dung_amt
            update_json(self.user_data)
            await ctx.send(f"You caught {dung_amt} dung. Delicious! You now have {target_user_data['dung']} dung.")
        else:
            await ctx.send("You haven't signed up for a dung account yet. Use dung signup")

    @commands.command()
    async def donate(self, ctx, amount, user):
        user_id = ctx.message.author.id
        amount = int(amount)